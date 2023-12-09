#  coding: utf8

import re
import time
import json
import base64
import hashlib
import procpy

#*************************************************************************

class DBConn (object):

    """

    This class wraps SQLite resp. MySQL commands to the database manipulation commands
    needed from datastore.DBObj.
  

    """

    def __init__ (self,coordinates={'type':'sqlite'}):

        """
        TODO
        """
        
        if coordinates['type'] == 'sqlite':
            import sqlite3
            self.dbh             = sqlite3.connect(coordinates['name'])
            self.dbh.row_factory = sqlite3.Row
            self.standard_placeholder = '?'
            self.index_length         = ''
            
        if coordinates['type'] == 'mysql':
            import MySQLdb
            self.dbh             = MySQLdb.connect(coordinates['host'],
                                                   coordinates['user'],
                                                   coordinates['pass'],
                                                   coordinates['db'],charset='utf8'
                                                   )
            self.standard_placeholder = '%s'
            self.index_length         = '(80)'
            
        cursor = self.dbh.cursor()

        try:
            cursor.execute("create table entries ("
                                 + "MD5KEY CHAR(25) UNIQUE,"
                                 + "OBJID VARCHAR(50) UNIQUE,"  
                                 + "OBJCLASS TEXT,"
                                 + "SLEEP TEXT,"
                                 + "WAKETIME TEXT,"
                                 + "JUMP TEXT)"
                       )
        except:
            pass

        try:
            cursor.execute("create index md5keyidx on entries (MD5KEY)")
        except:
            pass

        try:
            cursor.execute("create index objididx on entries (OBJID)")
        except:
            pass

        self.dbh.commit()

#*************************************************************************

    def commit (self):
        self.dbh.commit()    

#*************************************************************************

    def delete_object (self,md5key):
    
        cursor = self.dbh.cursor()
        nr     = cursor.execute("delete from entries where MD5KEY like '" + md5key + "%'")
        return(nr)

#*************************************************************************

    def upsert_hold_backs (self):
    
        erg = False
        if 'hold_back' in vars(self):
            for entry in self.hold_back:
                self.upsert_extend(entry)
                erg = True
        self.hold_back = []
        return(erg)

#*************************************************************************

    def upsert_extend (self,entry,delete_mode=0):

        if 'OBJID' in entry:
            m = re.search(r"^(\D*)(9+)(\D*)$",entry['OBJID'])
            if m:
                entry['OBJID'] = m.group(1) + ( ("%0"+str(len(m.group(2)))+"u") % 1 ) + m.group(3)
                if not 'hold_back' in vars(self):
                    self.hold_back = []
                self.hold_back.append(dict(entry))
                return()

        while 0 == 0:
            md5key = self.upsert(entry,delete_mode)
            if md5key:
                return(md5key)
            if not 'OBJID' in entry:
                return(False)
            m = re.search(r"(.*?)(\d+)(.*)$",entry['OBJID'])
            if m:
                entry['OBJID'] = m.group(1) + ( ("%0"+str(len(m.group(2)))+"u") % (int(m.group(2))+1) ) + m.group(3)
            else:
                entry['OBJID'] = entry['OBJID'] + "001"

#*************************************************************************

    def upsert (self,entry,delete_mode=0):

        placeholders = [self.standard_placeholder,self.standard_placeholder]
        
        field_list   = []
        entry_values = []
        md5new       = []

        for field in entry:   #  transfer the entry into the database
            if field == 'MD5KEY':
                md5key = entry[field]
            else:
                if type(entry[field]).__name__ in ["str","int","unicode","float","long"]:
                    dumpdata = str(entry[field])
                else:
                    dumpdata = json.dumps(entry[field],sort_keys=True,indent=4,ensure_ascii=False)
                field_list.append(self.mask(field))
                entry_values.append(dumpdata)
                placeholders.append(self.standard_placeholder)
                if not field[0] == "_":
                    md5new.append(field+": "+dumpdata)

#        print(123)
        md5new.sort()
        md5new = "".join(md5new)
        md5new = re.sub(r"\n","",md5new,99999999)
        md5new = re.sub(r"\f","",md5new,99999999)
        md5new = re.sub(r"\r","",md5new,99999999)
        md5new = re.sub(r"\t","",md5new,99999999)
        md5new = re.sub(r" +"," ",md5new,99999999)
        md5new = md5new.strip()

        field_list.append('OBJDATA')
        entry_values.append(md5new)
        
        md5new = bytearray(md5new,'utf-8')
        md5new = base64.b64encode(md5new)
        md5new = hashlib.md5(md5new).digest()
        md5new = base64.b64encode(md5new)
        md5new = str(md5new,"utf-8")   # bytearray.decode(md5new,encoding="utf-8")
        md5new = re.sub(r"^(.*)\=\=$","\\1",md5new)
        field_list.append('MD5KEY')
        entry_values.append(md5new)
#        print(124,md5new,md5key)
        
        cursor = self.dbh.cursor()
        if 'md5key' in vars():     #  if there is a former MD5KEY
            if md5new == md5key:   #  which is identical to the new one
#                print(1240,md5new,md5key)
                return(md5key)     #  the entry is exactly yet in the database
            nr = cursor.execute("delete from entries where MD5KEY like '" + md5key + "%'")

#        print(125)
        if delete_mode > 0:
            return(None)

        text   = "insert into entries (" + ",".join(field_list) + ") values (" + ",".join(placeholders) + ")"
#        print(text)

        while (0 == 0):  #  add columns as long as there are some missing
            try:
                if cursor.execute(text,entry_values):
#                    print "# change " + md5new
                    pass
                break
            except Exception as e:
#                print str(e)
                m = re.search(r"(Unknown +column .*?|no +column +named +)([A-Z0-9\_]+)",str(e))
                if m:
                    o = m.group(2)   #  column extension
#                    print("# alter table entries add column " + o + " TEXT")
                    cursor.execute("alter table entries add column " + o + " TEXT")
                    if self.mask(o) == o:
                        cursor.execute("create index " + o + "idx on entries (" + o + self.index_length + ")")
                else:
                    return(False)  # if there is another error by touching the unique constraints in MD5KEY or OBJID

        return(md5new)

#*************************************************************************

    def query_data (self,md5key="",datafield="",fields="*"):
    
        """
        Creates a database cursor which represents
        a certain query against the table  entries .
        """
        cursor = self.dbh.cursor()

        if md5key == "":   #  first mode, without any parameters. Select entries whose WAKETIME is reached.
            cursor.execute("select " + fields + " from entries where " +     
                           "WAKETIME < " + str(time.time()) + " and WAKETIME >= 0")  
        elif md5key == '___dryrun___':   #  ___dryrun___ mode, Select entries whithout respect of waketime
            cursor.execute("select " + fields + " from entries where not JUMP == ''")  
        elif not datafield == "":  #  search against a special value in a given column
            cursor.execute("select " + fields + " from entries where " + datafield + " ='" + md5key + "'")
#            print("select " + fields + " from entries where " + datafield + " ='" + md5key + "'")
        else:         
            sqlclause = "select " + fields + " from entries where " + md5key   # proper SQL query clause
            if not re.search(r"\=",sqlclause) and not re.search(r"like",sqlclause):
                sqlclause = "xxxx"
            try:      
               cursor.execute(sqlclause)
            except Exception as e:                                              #  a special form of query:  searching for
                md5key = re.sub(r",","%' ) and ( OBJDATA like '%",md5key,9999)  #  <a1>,<a2>,<a3>~<b1>,<b2>  means:
                md5key = re.sub(r"~","%' ) or ( OBJDATA like '%",md5key,9999)   #  search for entries where the patterns
                md5key = "( ( OBJDATA like '%" + md5key + "%' ) )"              #  <a1>, <a2> and <a3> OR the patterns
#                print("select * from entries where " + md5key)     
                try:                                                            #  <b1> and <b2> are contained in OBJDATA
                    cursor.execute("select * from entries where " + md5key)     
                except Exception as xxx_todo_changeme:
                    (e) = xxx_todo_changeme
                    print(md5key)
                    print(str(e))
                    return ( "\nNo valid sql expression:\n\n" + sqlclause + "\n" +
                            str(e) + "\n\nand also not valid short expression:"
                            "\n\n" + str(md5key) + "\n")
        return(cursor)

#*************************************************************************

    def next_obj (self,cursor,changer=None):  #    retrieving an object in mongo format
    
        column_contents = cursor.fetchone()
        if not column_contents:
            return(None)
            
        obj     = {}

        zaehler = -1
        
        for column in column_contents:
            zaehler = zaehler + 1
            if not column:
                continue
            if cursor.description[zaehler][0] == "OBJDATA":
                continue
            
            try:
                obj[ self.demask( cursor.description[zaehler][0] ) ] = json.loads(column)
            except:
                obj[ self.demask( cursor.description[zaehler][0] ) ] = column

        
        if changer:
            changer.run(obj)
        return(obj)

#*************************************************************************

    def lock_waketime (self,md5key,nr=0):

        if nr == 0: #  nicht exklusiver lock
            nr = "(cast((cast(WAKETIME as int)+1) as str) ) where OBJID='"
        elif nr == -1:
            nr = "'-1' where PARENTID='"
        else:
            nr = "'-" + str(nr) + "' where (cast(WAKETIME as int)) >= 0 and MD5KEY='"

        cursor = self.dbh.cursor()
        cursor.execute("update entries set WAKETIME="  + nr + md5key  +  "'" )
#        print("update entries set WAKETIME="  + nr + md5key  +  "'" )
        locked = False
        if cursor.rowcount == 1:
            locked = True
        self.dbh.commit()
        return(locked)

#*************************************************************************

    def mask (self,field):
    
        field1 = ""
        for o in field:
            if o == "_" or not o == o.upper():
                field1 = field1 + "_" + o.upper()
            else:
                field1 = field1 + o
        return(field1)
        

#*************************************************************************

    def demask (self,field):
    
        field1     = ""
        make_lower = False
        for o in field:
            if make_lower:
                field1 = field1 + o.lower()
                make_lower = False
            else:
                if o == "_":
                    make_lower = True
                else:
                    field1 = field1 + o
        return(field1)
        
#*************************************************************************
#*************************************************************************




