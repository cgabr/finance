#  coding: utf-8

__author__ = 'cgabriel'
import os,re,sys,time,random,glob
import codecs
import copy

from konto.base.mysqlite import DBConn

try:
    import xlrd
    import xlwt
    import xlutils
    import xlutils.copy
except:
    import pip
    import pip._internal
    pip._internal.main(["install","xlrd"])
    pip._internal.main(["install","xlwt"])
    pip._internal.main(["install","xlutils"])
    import xlrd
    import xlwt
    import xlutils
    import xlutils.copy

# from database_interface import SQLITE3Interface as database

class Xlsmanager(object):

    def __init__(self,db):

        self.db = db
        self.compiled_text_pattern = {}

        self.index_fields = {
              'DATUM'      : 1,
              'NAME'       : 1,
              'PLZ'        : 1,
              'STADT'      : 1,
              'TEL'        : 1,
              'KTOA'       : 1,
              'KTOB'       : 1,
            }

        self.sorted_fields = ('OBJCLASS NAME VORNAME STRASSE PLZ STADT TEL FAX MOBIL MAIL SEX INDEXX INFO ' +
                              'K KTO BANK BLZ STIMM END MD5KEY').split(" ")

        self.local_enc = "iso-8859-1"
        if True or os.name == 'posix':
            self.local_enc = "utf8"

        self.DYNFIELD = True


#*************************************************************************

    def csvimport (self,csvname,make_objid=False):  #  ,tmp_entry_list=[]):

        print(csvname)


        """
        This function upserts a bulk of key-value pairs from a csv-list
        into the database table  entries .
     
        The name of the resp. csv-file is in csvname
     
        The column names will be taken from the first valid line
        (comments starting with      , empty lines und and underlining lines consisting
        only from  ----  will be skipped)
        If column names are missing, they will be created on the fly with
        with names MISC01, MISC02, ....
     
        Each cell can overwrite the static column name under which it comes:
        By denoting   <key>:  <value>   the <value> goes into the row's
        key-value pairs with the key  <key>  and the value  <value> .
        (but only if the column does not end with _ and procpy.config.DYNFIELD = True)
        """

        text = self.read_excel_file(csvname)
  
        if not text:
            text = open(csvname,'r').read()
#            text = re.sub(r"\n([A-Z][A-Z]):","\n\\1_:",text,99999999)
#            text = text.replace('\r\n', '\n')
            cells = re.split(r"\"|$",text,99999999,re.DOTALL)   #    make a list of all text patterns separated by "
            text  = re.sub(r"\"(.*?)\"","---FIELD---",text,99999999,re.DOTALL)  # replace all "..." cells with ---FIELD---
            m     = re.search(r"^(.*?---FIELD---)[^,\n]",text)
            if m:
                print("Error in csv-File" + m.group(1))
                return(0)
            text  = text.splitlines()
        
        cells_count        = -2
        entry0             = {}
        column_descriptors = []
        anzahl_importierte_datensaetze = 0
        
        for zeile in text:

            try:
               zeile_sum = zeile
               zeile     = zeile.split(",")
            except:
               zeile_sum = "".join(zeile)

            if re.search(r"^(#|\\-+ *$|-+ *$| *$|alter *table)",zeile_sum):   #  skip comments, empty lines,  underlining ---------
                continue

            m = re.search(r"^ *[qQ]\: *([^\n]*)$",zeile_sum)
            if m:
                self.import_query = m.group(1)
                continue

            if cells_count == -2:
                column_descriptors = zeile
                cells_count = -1
                continue
        
            entry   = {}
            zaehler = -1
            miscnr  = 0
            for cell in zeile:
                zaehler = zaehler + 1
                cell    = cell.strip()
                if cell == "---FIELD---":
                    cells_count = cells_count + 2
                    cell        = cells[cells_count].strip()

                while (0 == 0):
                    try:
                        if str(column_descriptors[zaehler]) == str(""):
                            miscnr = miscnr + 1
                            column_descriptors[zaehler] = str("MISC" + ("%02u" % miscnr))
                        break
                    except:
                        miscnr = miscnr + 1
                        column_descriptors.append(str("MISC" + ("%02u" % miscnr)))
                if re.search(r"^\s*$",cell,re.DOTALL):
                    continue
                field = column_descriptors[zaehler]

                if self.DYNFIELD and not field[-1] == "_":
                    m = re.search(r"^\s*([A-Za-z0-9\_]+)\: *(.*)$",cell,re.DOTALL)
                    if m:
                        field = m.group(1)
                        cell  = m.group(2)

                cell = re.sub(r"^\-\-\> *","",cell)
                cell = re.sub(r"\r","",cell,99999999)
                cell = re.sub(r"\t","    ",cell,99999999)
                cell = re.sub(r"\"","\'",cell,99999999)
                cell = cell.strip()
                if   field[0:3] == "XXX":
                    continue
                if   field == "":
                    continue
                if re.search(r"^\s*$",cell):
                    continue
                if   field == "MDEL":
                    entry['DELETE'] = cell
                elif field == "DEL":
                    if cell == "X":
                        entry['DELETE'] = cell
                elif field == "MD5KEY":
                    entry[field] = cell
                elif not re.search(r"^MISC\d+$",field):
                    entry[field] = cell
                if not '_FILE' in entry and not '_DIR' in entry:
                    filename = csvname
                    dirname  = "."
                    m = re.search(r"^(.*)[\\\/](.*)$",csvname)
                    if m:
                        dirname  = re.sub(r"[\\\/]","___",m.group(1),99999999)
                        filename = m.group(2)
                    entry['_FILE'] = filename
                    entry['_DIR']  = dirname
                if make_objid and not 'OBJID' in entry:
                    entry['OBJID'] = "%03u" % random.randint(110,990)

            if 'DELETE' in entry and entry['DELETE'] == "M":   #  2 WAY MERGE !
                entry1 = dict(entry0)
                for k in entry:
                    if k == "DELETE":
                        continue
                    if not k in entry1 or entry1[k] == "":
                        entry1[k] = entry[k]
                    elif not entry1[k] == entry[k]:
                        if re.search(r"^(INFO|INDEX+)$",k):
                            entry1[k] = entry1[k] + "\n" + entry[k]
#                        if re.search(r"^VDATE$",k):
#                            entry1[k] = entry[k]
                        else:
                            del entry1
                            break
            if 'entry1' in vars():
#                print "XXXX: 1 -----------------------------------------------"
#                time.sleep(5)
                entry0 = entry1   #  entry1 is a merge result which could be merged again
            else:                 #  and therefore put in entry0
                entry1 = entry0
                entry0 = entry    #  No merge possible. So upsert the entry0 and make the
                entry  = entry1   #  entry to the new entry0. Roll back...
                del entry1
                
            delete_mode = 0
            if 'DELETE' in entry0 and entry0['DELETE'] == "X":
                delete_mode = 1
            else:
                anzahl_importierte_datensaetze = anzahl_importierte_datensaetze + 1
#            print(entry0)
            erg = self.db.upsert_extend(entry0)
        
#            if erg:
#                entry0['MD5KEY'] = erg
#                tmp_entry_list.append(entry0)
        self.db.commit()
#        print self.import_query

        self.column_descriptors = column_descriptors
        return(anzahl_importierte_datensaetze)                

#*************************************************************************

    def read_excel_file (self,xlsname):

        m = re.search(r"^(.*)\,(.*)$",xlsname)
        if m:
            xlsname = m.group(2)
        try:
            wb = xlrd.open_workbook(xlsname)
        except:
            return(None)
            
        sheets = wb.sheet_names()
        sheet  = sheets[0]
        if m:
            sheet = m.group(1)
        try:
            sheet  = wb.sheet_by_name(sheet)
        except:
            print("Sheets in the file " + m.group(2) + ":\n" + str(sheets))
            return(0)
        text   = []

#        xrows  = sheet.row(4)
        crows = 0
        while (0 == 0): 
            if crows == sheet.nrows:
                break
            ccols = 0
            text.append([])
            while (0 == 0):
                if ccols == sheet.ncols:
                    break
                cell_content = sheet.cell_value(crows,ccols)
                try:
                    if cell_content == int(cell_content):
                       cell_content = str(int(cell_content))
                except:
                    pass
                text[-1].append(str(cell_content))
                ccols = ccols + 1
            crows = crows + 1
            
#        print text
        return(text)

#**************************************************************************

    def ff (self,text,entry=False):
    
        """
        Replaces in the string variable all occurrences of  -KEYNAME- by
        the value of entry.KEYNAME  (KEYNAME stands for  alphanumeric key notators)
        
        A special 'keyname' is: REST. It produces a printout of all 'remaining'
        key-value pairs.
        """

#        text = re.sub(r'\\',r'\\\\',text,99999999,flags=re.DOTALL)
#        text = re.sub(r'\[','@a@',text,99999999,flags=re.DOTALL)
#        text = re.sub(r'\]','@b@',text,99999999,flags=re.DOTALL)
#        text = re.sub(r'\\','@c@',text,99999999,flags=re.DOTALL)
#        print text

#        while re.search(r"\.",text):   #   Das Template kann auch eine Funktion aus einem Modul sein
#            m = re.search(r"^(.*)\.(.*)$",text)
#            try:
#                exec "import " + m.group(1)
#            except:
#                break
#            exec "erg =  " + text + "(entry)"
#            return(erg)


        if text in self.compiled_text_pattern:
            text1 = self.compiled_text_pattern[text]
        else:
            text1 =  re.sub(r"(-)(x?)(\d*[A-Za-z\_0-9\.]+?|x)(\d*)-","@SEPARATOR@"+"\\2,\\3,\\4"+"@SEPARATOR@",
                           text,99999999,flags=re.DOTALL)
#            text1 =  ( "u\'\'\'" + re.sub(r"(-)(x?)(\d*[A-Za-z\_0-9\.]+?|x)(\d*)-",
#                          "\'\'\'+unicode(self.valfield(entry,\"\\2\",\"\\3\",\"\\4\"))+u\'\'\'",
#                          text,99999999,flags=re.DOTALL) + "\'\'\'" )
            text2     = text1.split("@SEPARATOR@")
            text1     = ""
            translate = False
            for textpattern in text2:
                if translate:
                    textpattern1 = textpattern.split(",")
                    textpattern1 = self.valfield(entry,textpattern1[0],textpattern1[1],textpattern1[2])
                    text1        = text1 + textpattern1
                else:
                    text1        = text1 + textpattern
                translate = not translate

            self.compiled_text_pattern[text] = text1


        while (0 == 0):  #  substitution of include files
            break
            m = re.search(r"^(.*?)\[(\S+?)\](.*)$",text1,re.DOTALL)
            if not m:
                break
            file9 = ""
            if os.path.isfile(m.group(2)):
                file9 = m.group(2)
            elif os.path.isfile(self.ff_file(m.group(2))):
                file9 = self.ff_file(m.group(2))
            if file9:
                text1 = m.group(1) + open(file9,'r').read() + m.group(3)
            else:
                text1 = m.group(1) + "[-x-x-]" + m.group(2) + "[-y-y-]" + m.group(3)
        text1 = re.sub(r"\[-x-x-\]","[",text1,99999999)
        text1 = re.sub(r"\[-y-y-\]","]",text1,99999999)
        erg   = text1

        return(erg)
        

#**************************************************************************

    def ff_file (self,text,entry=False):   #  Filename normalisieren

        text1 = text
        text1 = re.sub(r"(^|\/|\\)x","\\1-x",text)
#        text1 = re.sub(r"^--","-","-"+text1)
        text2 = re.sub(r"(-)(x?)(\d*[A-Z][A-Za-z0-9]*?|x)(\d*)-","",text1,99999999)
        entry_cache = self.entry_cache.copy()
        text1 = self.ff(text1,entry)
        self.entry_cache = entry_cache
        text1 = re.sub(r"[\;\: \?\!]","_",text1,99999999)
        text1 = re.sub("ü","ue",text1,99999999)
        text1 = re.sub("ö","oe",text1,99999999)
        text1 = re.sub("ä","ae",text1,99999999)
        text1 = re.sub("Ü","Ue",text1,99999999)
        text1 = re.sub("Ä","Ae",text1,99999999)
        text1 = re.sub("Ö","Oe",text1,99999999)
        text1 = re.sub("ß","ss",text1,99999999)
        text1 = re.sub(r"___","/",text1,99999999)
        text1 = re.sub(r"^-","",text1)
        text1 = re.sub(r"\+","-",text1)
        text1 = re.sub(r"\/","_",text1)
        if text2.lower() == text2 and not "-" in text2:
            text1 = text1.lower()

        return(text1)
        
        
#**************************************************************************

    def ff_content (self,text,entry=False):   #  Filename normalisieren

        text1 = self.ff(text,entry)
#        text1 = self.ff(text1,entry)
#        m = re.search(r"PERSONALIZE: +(.+?),(.+?),(.+?),(.+?),(.+?),(.*?),(.*?),(.*?),(.+?),(.+?),",text1)
#        if m:
#            self.entry_cache['TOADR']      = m.group(3)
#            self.entry_cache['TONAME']     = m.group(4)
#            self.entry_cache['TOANREDE']   = m.group(5)
#            self.entry_cache['TOAMODE']    = m.group(6)
#            self.entry_cache['TOBMODE']    = m.group(7)
#            self.entry_cache['TOCMODE']    = m.group(8)
#            self.entry_cache['TOGRUSS']    = m.group(9)
#            self.entry_cache['TOABSENDER'] = m.group(10)
#            text1 = self.ff(text,entry)
#            text1 = re.sub(r"DELTEXT.*?DELTEXT",text1,99999999,flags=re.DOTALL)

        return(text1)

#*************************************************************************

    def xxvalfield (self,entry,delflag,field,nr=""):
    
        erg0 = None
        erg  = self.valfield1(entry,delflag,field,nr)
        return(self.ff(erg,entry))
#        return(erg)
#        while (0 == 0):
#            print erg, erg0
#            if erg0 and erg0 == erg:
#                return(erg)
#            erg0 = erg
#            print erg, erg0
#            time.sleep(1)
#            erg  = self.ff(erg,entry)

#*************************************************************************

    def valfield (self,entry,delflag,field,nr=""):
    

        if field == "x" and delflag == "":
            delflag = "x"
            field   = ""

        erg = ""
        while (0 == 0):
            try:
                erg = self.entry_cache[field]
                break
            except:
                pass
                
            if not field == "DELETE":
                try:
                    erg = entry[field]
                except:
                    try:
                        erg = entry[field]
                    except:
                        try:
                            erg = entry[field+nr] ##  check!!! @@@@
                        except:
                            pass

            if erg == "" and not nr == "" and 'INDEXX' in entry:
                if re.search((field+nr),(" " + entry['INDEXX'] + " ")):
                   field = field+nr
                   nr    = ""
                   continue

            if not nr == "" and (field+nr) in entry:
                   field = field+nr
                   nr    = ""

            if type(erg) == type(None):
                erg = ""
            if not nr == "":
                try:
                    erg = (erg.split(","))[int(nr)-1]
                except:
                    pass
                    
            m = re.search(r"^([MW])(\d)([A-Z]+)$",field)  # personalized data
            if m:
                if re.search("^"+m.group(1).lowercase()+".* "+m.group(3).lowercase+mgroup(2),self.valfield(entry,"SEX")):
                    erg = "1"
                    break                

            if field == "COUNT":
                erg = str(self.entries_count)

            elif re.search(r"^REST",field):
                exclude_columns = field.split("_")
                field = "REST"
                erg   = ""
                ee    = list(entry.keys())
                ee.sort()
                for k in self.sorted_fields + ee:
                    if not k in entry:
                        continue
                    if not k in self.entry_cache and type(entry[k]) != type(None):
                        self.entry_cache[k] = str(entry[k])
                        if k == "MD5KEY" and not delflag == "":
                            continue
                        if k in exclude_columns:
                            continue
                        if k[0] == "_":
                            continue
#                        if field == "REST":
#                            erg = erg + "\n" + k + ": " + self.valfield(entry,"",k) + "\",\""
                        o   = str(entry[k]) 
                        if re.search(r"\n",o,re.DOTALL):
                            o = "\n" + o + "\n"
                        erg = erg + "\n" + ("%-15s" % (k + ": ")) + o + "\",\""
                erg = "\"" + erg + "\n\""
            self.entry_cache[field+nr] = erg
            break        

        if erg == "":
            m = re.search(r"^(.*)FROM(.*)",field)
            if m:
                erg = self.valfield(entry,delflag,m.group(1),nr)

        if erg == "" and field[0:2] == "TO" and not re.search(r"^(TOOLS?|TODO)$",field):
#            print field
            return(delflag+field[2:])
        if erg == "" and delflag == "":
            erg = "-" + field + nr + "-"
            

        if delflag == "x":   #  put it in double quotes if necessary
            try:
                erg = re.sub(r"^\"(.*)\"$","\\1",erg,flags=re.DOTALL)
                if re.search(r"[\"\,\n]",erg):
                    erg = '"' + erg + '"'
            except:
                pass

        try:
            erg = str(erg)
        except:
            pass

        if not re.search(r"^-[^-]*-$",erg):
            erg = self.ff(erg,entry)

        return(erg)


#*************************************************************************

    def export_data (self,pars,print_to_console=True):
    
        """
        This function reads out data from the database in a rendered form.
      
        A parameter which is a .csv or .adr file is taken as a data source
        and its entries are upserted by the csvimport function.
      
        The other parameters are read in in the database in the order:
      
        First parameter (filter):     The sql-filter expression against the table  entries
                                      ( or the short form  <pattern1>,<pattern2>,...~<pattern3>, ....)
        Second parameter (template):  The text template. Each occurences of -<KEY>- will be
                                      replaced by the respective value of the actual entry.
                                      -x<KEY>- works at the same but replaced by "" if no
                                      such key exists.
                                      If the text template is a name of an existing file,
                                      then the contents will be written in files where
                                      the placeholders in the filename also are replaced,
                                      so that the can be as a result many files. The
                                      placeholders in the contents of the file wille be also
                                      replaced.
        Third parameter (sort1):      Sorts the entries to a pattern given by the template  sort1
                                      Each entries with the same sort1-Value will be given
                                      to the merge function which returns a merged list
                                      of entries.
        Fourth paramater (filter_template):  Filters  filter , but on the
                                      pattern given by filter_template, and only if the
                                      form  <pattern1>,<pattern2>,...~<pattern3>, ....
                                      for filter is used
        """

        pars1 = []   #   Aufloesung von Wildcards, ggfs aus der Windows-Shell
        for par in pars:
            par = re.sub(r"'","",par,9999)
            if re.search(r"\*",par):
                pars1 = pars1 + glob.glob(par)
            else:
                pars1.append(par)
        pars = pars1


#   1.   Preparation of parameters   ------------------------------------


        def sort_e (x):
            if 'VDATE' in x:
                erg = x['VDATE']
            else:
                erg = 99999999
            return(erg)
                
        self.output_text    = ""
        self.import_query   = ""
        obj_to_change_entry = None

        if "__MERGE__" in pars:
            self.merge_files = []

        for par in pars:

            par = par.strip()  #  .decode(self.local_enc)       #  hier wird erstmal getestet, ob ein Parameter ein File ist
            m = re.search(r"^(.*),(.*)$",par)
            if m:
                parfile = m.group(2)
            else:
                parfile = par
#            print("import " + re.sub(r"^(.*)\.(.*)$","\\1",par))
            try:    #   hier versuchen, den Paraeter als entry-changing Objekt zu laden
                exec("import " + re.sub(r"^(.*)\.(.*)$","\\1",par))
                exec("obj_to_change_entry = " + par + "()")
                continue
            except Exception as e:
                pass

            if not 'filter' in vars():
                if (os.path.isfile(parfile)):
                    if 'merge_files' in vars(self):  #  nur der Ancestor muss sich von den anderen Eintraegen unterscheiden                    
                        anzahl_importierte_datensaetze = self.csvimport(par,len(self.merge_files)==0)   #  ,tmp_entry_list)
                        self.merge_files.append(par)
                    else:
                        anzahl_importierte_datensaetze = self.csvimport(par)  #  ,tmp_entry_list)
                else:
                    if 'merge_files' in vars(self):
                        if par == "__MERGE__":
                            filter = '~'
                    else:
                        filter = par 
            elif not 'template' in vars():
                template        = par
            elif not 'sort1'    in vars():
                sort1           = par
            elif not 'filter_template' in vars():
                filter_template = par

#        print self.merge_files

        if self.db.upsert_hold_backs():  #  Read in hold back entries which have an OBJID field with value:
#            tmp_entry_list.append(self.db.hold_back)
#            anzahl_importierte_datensaetze = anzahl_importierte_datensaetze + len(self.db.hold_back)
#            self.db.hold_back = []
            self.db.commit()             #  \D*9+\D*, to get new OBJID computation

        if not 'filter' in vars():
            filter = "~" 
        if not 'template' in vars():
#            template = "-MD5KEY-,-REST-"
            template = "-REST_MD5KEY-"

        output_file_template = ""         #  define an output file
        if 'merge_files' in vars(self):    #  __MERGE__
            output_file_template = re.sub(r"\.xlsx?$",".csv","x-" + self.merge_files[1])  #  write back the 3way result in %A-file for git
#            print(output_file_template)
            os.unlink(self.merge_files[1])
        if os.path.isfile(template):       #  wenn das Template ein File ist, dieses einlesen
            output_file_template = template
            text = self.read_excel_file(output_file_template)   #  erstmal versuchen, als Excel-File einzulesen
            if text:
                template = ""
                for xls_row in text:
                    zeile = ",".join(xls_row)
                    template = template + zeile + "\n"
            else:
                template = open(output_file_template,'r').read()
            if re.search(r"(csv|xlsx?)$",output_file_template):
                template = re.sub(r"\r?\n","",template,99999999)
            template = template.strip()

#        template = re.sub(r"\\n","\n",template,99999999,flags=re.DOTALL) # keine Ahnung mehr, wozu diese Zeile gut sein sollte

        convert_to_xls = False
        output_header  = ""
        m = re.search(r"^\s*([^\n]+?)\s*$",template,flags=re.DOTALL)  #  wenn das Template nur aus einer einzigen
        if m:
            output_header = re.sub(r"-x?","",m.group(1),99999999)     #  Zeile besteht, dann daraus einen template header
            if re.search(r"\{.*\}",output_header):                    #  erzeugen
                convert_to_xls = True   #  wenn xls-Formatierungen vorgefunden werden, in Excel-Tabelle schreiben
                m = re.search(r"^(\{.*?\})(.*)$",output_header,flags=re.DOTALL)
                if m:
                    output_header = re.sub(r"\{.*?\}","",m.group(2),99999999)
                    output_header = re.sub(r"($|,)",m.group(1)+"\\1",output_header,99999999)
                    template      = re.sub(r"^\{(.*?)\}(.*)$","\\2",template)
        
#   2.   Pre-Filter  ------------------------------------

        cursor = self.db.query_data(filter)

        if 'filter_template' in vars():
            filter_conditions = []
            for pattern in filter.split("~"):
                filter_conditions.append(pattern.split(","))
            entries = []
            while (0 == 0):
                self.entry_cache           = {}
                self.compiled_text_pattern = {}
                entry = self.db.next_obj(cursor,obj_to_change_entry)
                if not entry:
                    break
                filter_str = self.ff(filter_template,entry)
                for p1 in filter_conditions:
                    bed = True
                    for p2 in p1:
                        if re.search(p2,filter_str):
                            continue
                        bed = False
                        break
                    if bed:
                        break
                if bed:
                    entries.append(entry) 
                    
#   3.   Post-Sort by Sort-Pattern  ------------------------------------
                    
        if 'sort1' in vars():
            entries_by_sort = {}
            zaehler         = 0
            while (0 == 0):
                self.entry_cache           = {}
                self.compiled_text_pattern = {}
                if 'filter_template' in vars():
                    try:
                        entry  = entries[zaehler]
                    except:
                        break
                    zaehler = zaehler + 1
                else:
                    entry = self.db.next_obj(cursor,obj_to_change_entry)
                    if not entry:
                        break
                sort_text  = self.ff(sort1,entry)
                if sort_text in entries_by_sort:
                    entry['DEL'] = "M"
                if not sort_text in entries_by_sort:
                    entries_by_sort[sort_text] = []
                entries_by_sort[sort_text].append(entry)
            sorting_of_entries = list(entries_by_sort.keys())
            sorting_of_entries.sort()
            entries = []
            for sort_text in sorting_of_entries:   #   sort the grouped entries
                entries1 = []
                for e in entries_by_sort[sort_text]:
                    entries1.append(e)
                entries1.sort(key=sort_e)
                entries1.reverse()
#                if 'merge_files' in vars(self):
                entries1 = self.merge_23way(entries1)
                if not 'VDATE' in entries1[0] and 'DEL' in entries1[0]:  #  VDATE can be a date to which the entry is vaiid
                    del entries1[0]['DEL']
                entries = entries + entries1
                
#    4. ------------------  Main loop   -------------------------------

        zaehler            = 0
        self.entries_count = 0
        touched_files      = {}

        while (0 == 0):
            self.entry_cache           = {}
            self.compiled_text_pattern = {}
            if 'entries' in vars():
                try:
                    entry = entries[zaehler]
                except:
                    break
                zaehler = zaehler + 1
            else:
                entry = self.db.next_obj(cursor,obj_to_change_entry)
                if not entry:
                    break
            output_file    = self.ff_file(output_file_template,entry)
            if output_file == output_file_template:
                output_file = ""    #  to prevent from overwriting template-file
            output_content = self.ff_content(template,entry)
            
            m = re.search(r"^(.*)\/(.*)$",output_file)
            if m:
                try:
                    os.makedirs(m.group(1))
                except:
                    pass
                    
            if not output_file in touched_files:
                touched_files[output_file] = 1
                if output_file == "":
                    if print_to_console:
                        print(output_header)
                        print(re.sub(r".","-",output_header))
                    else:
                        self.output_text = self.output_text + output_header
                        self.output_text = self.output_text + re.sub(r".","-",
                               re.sub(r"\{[a-z0-9]+\}","",output_header,9999))
                else:
                    open(output_file,'w').write(output_header+"\n")
                    if print_to_console:
                        print(output_file) # .encode(self.local_enc)
                    else:
                        self.output_text = self.output_text + output_file
                    open(output_file,'a').write(re.sub(r".","-",
                           re.sub(r"\{[a-z0-9]+\}","",output_header,9999))+"\n")
            cr = ""
            text = self.ff_content(template,entry)
            if re.search("\n",text):
                cr = "\n"
            if output_file == "":
                if print_to_console:
                    print((cr+text+cr))  #  .encode(self.local_enc))
                else:
                    self.output_text = self.output_text + cr + text + cr
            else:
                if os.path.isfile(output_file):
                    open(output_file,'a').write(cr+text+cr+"\n")
                else:
                    open(output_file,'a').write(text+cr+"\n")

#    5.   ------ Conversion of files to xls

        if convert_to_xls:
    
            for file in touched_files:

                template_content1 = open(file,'r').read()
#                print template_content1
                if re.search(r"NOXLS",template_content1) and len(touched_files) > 1:
                    open(file,"w").write(re.sub(r"\{[a-z0-9]+\}","",template_content1,99999999))
                    continue
                os.unlink(file)
                template_content1 = re.sub(r"\n\"[\n ]+\n","\n\"\n",template_content1,99999999)
                template_content1 = re.sub(r"\n-+\n","\n",template_content1,99999999)
                template_content1 = re.sub(r"\n *\n","\n",template_content1,99999999)
                template_content1 = re.sub(r"\n *\n","\n",template_content1,99999999)
                template_content1 = re.sub(r"\n\"[\n ]+\n","\n\"\n",template_content1,99999999)
                template_content1 = re.sub(",\"\s*([A-Za-z\_0-9]+)\: *",",\"\\1: ",template_content1,99999999)
                template_content1 = re.sub(",\"\n\"","",template_content1,99999999)
                template_content1 = re.sub(r"\\\"","",template_content1,99999999)
                cells             = re.split(r"\"|$",template_content1,99999999,flags=re.DOTALL)
                cells_count       = -1
                template_content1 = re.sub(r"\"(.*?)\"","---FIELD---",template_content1,99999999,flags=re.DOTALL)
                m = re.search(r"^(.*)\.(.*)$",file)
                if not m:
                    continue
                sheet_name = m.group(2)
                if not m.group(1) == "":
                    file = m.group(1) + ".xls"

#   ----------------------------------

                try:
                    wb0 = xlrd.open_workbook(file,formatting_info=True)
                except:
                    wb0 = None
                    
                if wb0:
                    wb1 = xlutils.copy.copy(wb0)
                else:
                    wb1 = xlwt.Workbook(encoding=self.local_enc)   #  open the new excel-workbook

#                oldsheets = []
#                opennew = False
#                zaehler = 0
#                sheets_idx = {}
#                for sheet in wb1._Workbook__worksheets:
#                    print sheet.name
#                    if sheet.name == sheet_name:                      TODO!!!
#                        opennew   = True
#                    else:
#                        oldsheets.append(sheet)
#                        sheets_idx[sheet.name] = zaehler
#                        zaehler = zaehler + 1
#                if opennew:
#                    wb1._Workbook__worksheets = oldsheets
#                    wb1._Workbook__worksheet_idx_from_name = sheets_idx
#                    wb1.save(file)
#                    wb  = xlrd.open_workbook(file,formatting_info=True)
#                else:
#                    wb = wb1

                wb = wb1

                wb.set_colour_RGB(51, 200, 255, 200)  #  green         0x51,
                xlwt.Style.add_palette_colour("ga",51)
                wb.set_colour_RGB(52, 100, 204, 100)  #                0x52,
                xlwt.Style.add_palette_colour("gb",52)
                wb.set_colour_RGB(53,  51, 153,  51)  #                0x53,
                xlwt.Style.add_palette_colour("gc",53)

                wb.set_colour_RGB(55, 255, 255, 200)  #  yellow        0x55,
                xlwt.Style.add_palette_colour("ya",55)
                wb.set_colour_RGB(56, 255, 255, 130)  #                0x56,
                xlwt.Style.add_palette_colour("yb",56)
                wb.set_colour_RGB(57, 255, 255,   0)  #                0x57,
                xlwt.Style.add_palette_colour("yc",57)

                wb.set_colour_RGB(60, 255, 200, 200)  #  red           0x60,
                xlwt.Style.add_palette_colour("ra",60)
                wb.set_colour_RGB(61, 255, 120, 120)  #                0x61,
                xlwt.Style.add_palette_colour("rb",61)
                wb.set_colour_RGB(62, 255,   0,   0)  #                0x62,
                xlwt.Style.add_palette_colour("rc",62)

                wb.set_colour_RGB(45, 200, 200, 250)  #  blue          0x45,
                xlwt.Style.add_palette_colour("ba",45)
                wb.set_colour_RGB(46, 100, 100, 200)  #                0x46,
                xlwt.Style.add_palette_colour("bb",46)
                wb.set_colour_RGB(47,  90,  90, 150)  #                0x47,
                xlwt.Style.add_palette_colour("bc",47)

                wb.set_colour_RGB(48, 220, 220, 220)  #  grey          0x48,
                xlwt.Style.add_palette_colour("ea",48)
                wb.set_colour_RGB(49, 180, 180, 180)  #                0x49,
                xlwt.Style.add_palette_colour("eb",49)
                wb.set_colour_RGB(50,   0,   0,   0)  #                0x50,
                xlwt.Style.add_palette_colour("ec",50)

                nr = None
#                print wb.__active_sheet
                if sheet_name in wb._Workbook__worksheet_idx_from_name:
                    nr = wb._Workbook__worksheet_idx_from_name[sheet_name]
                    del wb._Workbook__worksheet_idx_from_name[sheet_name]
                    wb._Workbook__worksheets[nr] = None
                newsheet = wb.add_sheet(sheet_name)
                if not nr == None:
                    wb._Workbook__worksheets[nr] = wb._Workbook__worksheets[-1]
                    wb._Workbook__worksheets     = wb._Workbook__worksheets[:-1]

                crows = 0
                for zeile in template_content1.split("\n"):
                    if re.search(r"^\s*$",zeile ):
                        break
                    ccols = 0
                    for cell_content in zeile.split(","):
                        while (0 == 0):
                            m = re.search(r"^(.*)(\{(.*)\})\{(.*)\}$",cell_content,re.DOTALL)
                            if not m:
                                break
                            cell_content = m.group(1) + m.group(2)
                        m = re.search(r"^(\-\-\-FIELD\-\-\-)(.*)$",cell_content,flags=re.DOTALL)
                        if m:
                            cells_count  = cells_count + 2
                            cell_content = cells[cells_count].strip() + m.group(2)
                        cellstyle = self.style_wb("")
                        m         = re.search(r"^(.*)\{(.*)\}$",cell_content,flags=re.DOTALL)
                        if not m:
                            m1 = re.search(r"^(.*)(\{.*\})$",zeile,flags=re.DOTALL)
                            if m1:
                                cell_content = cell_content + m1.group(2)
                                m = re.search(r"^(.*)\{(.*)\}$",cell_content,flags=re.DOTALL)
                        if m:
                            cellstyle    = self.style_wb(m.group(2))
                            cell_content = m.group(1)
                        newsheet.write(crows,ccols,cell_content,cellstyle)
                        if crows == 1:
                            m1 = re.search(r"^(\d+)",m.group(2))
                            if m1:
                                newsheet.col(ccols).width = 256*int(m1.group(1))
                        ccols = ccols + 1
                    crows = crows + 1

                wb.save(file)


        if not len(touched_files) == 1:
            return("")
            
        if not re.search(r"(^|,)REST($|,)",output_header):
            return("")
            
        if convert_to_xls:
            return("")

        return(list(touched_files.keys())[0])


#*************************************************************************


    def style_wb (self,style_marker):
       
       style_color = "w"
       style_size  = 12
       style_ftype = "n"
       style_pos   = "l"
       m = re.search(r"^(\d*)(c?)(.*?)(\d+)(\D?)$",style_marker)
       if m:
           style_pos    = m.group(2)
           style_color  = m.group(3)
           style_size   = m.group(4)
           style_ftype  = m.group(5)
           
       if re.search(r"^()$",style_ftype):
           style_ftype = "n"
       if re.search(r"^()$",style_pos):
           style_pos = "l"
       if style_color == "w":
           style_color = "white"
           
       style =  (
                  "font: bold " + {"b":"1","n":"0"}[style_ftype] + ", height " + str(int(style_size)*16) + "; " +
                  "pattern: pattern solid, fore_color " + style_color + "; " +
                  "borders: left thin, top thin, right thin, bottom thin; " +
                  "align: horiz " + {"c":"center","l":"left"}[style_pos] + ", vert center, wrap 1"
                )
                
       xlwt.easyxf(style)
       if not 'wbstyles' in vars(self):
           self.wbstyles = {}
       if not style in self.wbstyles:
           self.wbstyles[style] = xlwt.easyxf(style)
       return(self.wbstyles[style])


#*************************************************************************

    def merge_23way (self,entries1):      #   2 or 3 way merge
    
#        print(entries1)

        entries2 = {}
        
        origin = None
        if 'merge_files' in vars(self) and len(self.merge_files) == 3:   #  if we have 3 input files, then it is a 3 way merge with an common ancestor
            origins = []
            for entry in entries1:
#                print entry
                if entry['_FILE'] == self.merge_files[0]:
                    origins.append(entry)
            for origin in origins:
                entries1.remove(origin)
            if len(origins) > 1:
                return(entries1)
            if len(origins) == 1:
                origin = origins[0]

#        print self.merge_files
#        print origin
#        print len(entries1)

        allkeys      = {}
        for entry in entries1:
            for key in entry.keys():
                allkeys[key] = 1
                
        merged_entry = {}
        for key in allkeys:
#            print("KEY",key)
            for entry in entries1:
#                print entry['_FILE']
                if key in entry:
                    if not key in merged_entry or key[0] == "_" or key in ("MD5KEY","OBJID"):
                        merged_entry[key] = entry[key]         #  no problem to decide. key is not occupied yet
                        continue
                    if merged_entry[key] == entry[key]:
                        continue
                    if origin and key in origin:               #  another chance to decide by common ancestor
#                        print origin[key]
#                        print merged_entry[key]
#                        print entry[key]
                        if origin[key] == merged_entry[key]:  #  we take the change
                            merged_entry[key] = entry[key]
#                            print 123
                        elif origin[key] == entry[key]:  #  we take the change
                            pass
#                            print 124
                        else:
#                            print "NOT MERGED"
                            return(entries1)
                    else:
#                        print(key)
                        return(entries1)   #  merge not possible

        return([merged_entry])
                                
#*************************************************************************


    def mark_for_merge (self,entries):
    
        '''Rules out whether there are candidates for doublettes
        '''


        if len(entries) == 1:
            return(entries)

        diff_entry = {}

        for entry in entries:
            for k in entry:
                if k == "MD5KEY":
                    continue
                if k == "DEL":
                    continue
                if k in diff_entry:
                    if not diff_entry[k] == entry[k]:
                        diff_entry[k] = entry[k]
                        entry[k]      = "-->" + str(entry[k])
                    else:
                        diff_entry[k] = entry[k]
                else:
                    diff_entry[k] = entry[k]
        
#        entries.insert(-1,diff_entry)
#        print entries
        
        return(entries)
        
#*************************************************************************

    def xxtrack_tasks (self,pars):


        taskdir  = re.sub(r"\s","",os.popen('git config tasks.taskdir').read(),        99999999,flags=re.DOTALL)
        smtphost = re.sub(r"\s","",os.popen('git config tasks.smtphost').read(),       99999999,flags=re.DOTALL)
        sender   = re.sub(r"\s","",os.popen('git config tasks.sender').read(),         99999999,flags=re.DOTALL)
        cclist   = re.sub(r"\s","",os.popen('git config tasks.cclist').read(),         99999999,flags=re.DOTALL)
        gitroot  = re.sub(r"\s","",os.popen('git rev-parse --show-toplevel').read(),   99999999,flags=re.DOTALL)
        cwd      = os.getcwd()
        taskdir  = re.sub(r"^"+gitroot,"",cwd)
        
        try:
            name_of_tracker = pars[0]
        except:
            name_of_tracker = "ProcPy"

        self.output_text = ""


#  1.  Execute a query for all tasks where its _DIR differs from ASSIGN field (all moved tasks)

        
        changed_tasks = self.export_data(os.popen("ls */*.csv").readlines() +
                       ['not __DIR=ASSIGN','-_DIR-,-ASSIGN-,-_DIR-/-_FILE-,-OBJID-,x'],False)
        open("x--_DIR-___-_FILE-","w").write("-_DIR-,-xREST_ASSIGN\n")

        for zeile in changed_tasks.split("\n"):

            m = re.search(r"^(.*),(.*),(.*),(.*)$",zeile)
            if not m:
                continue
            newowner = m.group(1)
            oldowner = m.group(2)
            taskfile = m.group(3)
            taskid   = m.group(4)
            

#  2.  Add assigning informations to task text

            try:
                text = open(taskfile).read()
            except:
                continue
            text = re.sub(r"(HISTORY\:)(.*?)\"","\\1\\2\n" +
                          "assigned from " + oldowner + " to " + newowner +
                          " at " + time.asctime() + "\n\"",text,flags=re.DOTALL)
            open(taskfile,"w").write(text)
            

#  3.  Rename task file name if it has not yet OBJID information
            
            newfilename = re.sub(r"(.*)(^|[\\\/])(.*)$","\\1\\2"+taskid+"_\\3",zeile1[2])
            newfilename = re.sub(r"(^|[\\\/])"+taskid+"_"+taskid,"\\1"+zeile1[3],newfilename)
            if not newfilename == zeile1[2]:   #   wenn Umbenennung des Tasks noetig ist
                os.popen("mv " + zeile1[2] + " " + newfilename)
                print(("mv " + zeile1[2] + " " + newfilename))


#  4.  Check whether a notification should be sent

            try:
                toaddr = re.sub(r"\s","",open(newowner+"/.notification.txt").read(),   99999999,flags=re.DOTALL)
            except:
                print("No mail notification sent to " + newowner)
                continue
                

#  5.  Create the mailsender object if not yet done

            if not 'mailsender' in vars():
                import smtplib
                import email.mime.text
                mailsender = smtplib.SMTP()
                mailsender.connect(smtphost)


#  6.  Create the mail message
            
            mailmsg = email.mime.text.MIMEText("""
Hello """ + newowner + """,

The task """ + taskdir + "/" + newowner + "/" + newfilename + """
has been assigned to you by """ + oldowner + """

Please work on it via editing the HISTORY Section, and re-assign it to another person's folder in

          """ + taskdir + """
                    
The content of the task is:

---------------------------------------------------------------------
""" + text + """

---------------------------------------------------------------------
The """ + name_of_tracker + """ Tracker, """ + time.asctime() + """

Do not answer to this mail.
""")
            mailmsg['Subject'] = "Task Assignment " + newfilename
            mailmsg['Cc']      = cclist
            if not name_of_tracker.lower() == "dryrun":
                mailsender.sendmail(sender,[toaddr],mailmsg.as_string())
            print("Mail sent to " + toaddr + " for task " + newfilename)
                                          

#   7.. Finishing of the changed tasks: new column headers

        for zeile in self.export_data(os.popen("ls */*.csv").readlines()+['not __DIR=ASSIGN','x--_DIR-___-_FILE-'],False):
            taskfile = zeile.strip()
            try:
                text = open(taskfile).read()
            except:
                continue
            text = re.sub(r"_DIR,REST_ASSIGN","ASSIGN,REST",text)  #  <--- new column headers
            open(taskfile,"w").write(text)
            print(taskfile + " rewritten ...")

        os.unlink("x--_DIR-___-_FILE-")

#*************************************************************************

    def xxpostcommand (self,text):

        m = re.search(r"^(reassigntask|columnheaderstask),(.*)$",text)
        if m:
            exec("self."+m.group(1)+"("+m.group(2)+")")

#*************************************************************************
        
    def xxreassigntask (self,text):


        if not 'taskdir' in self:

            self.taskdir  = re.sub(r"\s","",os.popen('git config tasks.taskdir').read(),        99999999,flags=re.DOTALL)
            self.smtphost = re.sub(r"\s","",os.popen('git config tasks.smtphost').read(),       99999999,flags=re.DOTALL)  
            self.sender   = re.sub(r"\s","",os.popen('git config tasks.sender').read(),         99999999,flags=re.DOTALL)
            self.cclist   = re.sub(r"\s","",os.popen('git config tasks.cclist').read(),         99999999,flags=re.DOTALL)
            self.gitroot  = re.sub(r"\s","",os.popen('git rev-parse --show-toplevel').read(),   99999999,flags=re.DOTALL)
            self.cwd      = os.getcwd()
            self.taskdir  = re.sub(r"^"+gitroot,"",cwd)
        
        m = re.search(r"^(.*),(.*),(.*),(.*),(.*)$",text)
        newowner        = m.group(1)
        oldowner        = m.group(2)
        taskfile        = m.group(3)
        taskid          = m.group(4)
        name_of_tracker = m.group(5)
            

#  2.  Add assigning informations to task text

        try:
            text = open(taskfile).read()
        except:
            return()
        text = re.sub(r"(HISTORY\:)(.*?)\"","\\1\\2\n" +
                      "assigned from " + oldowner + " to " + newowner +
                      " at " + time.asctime() + "\n\"",text,flags=re.DOTALL)
        open(taskfile,"w").write(text)
            

#  3.  Rename task file name if it has not yet OBJID information
            
        newfilename = re.sub(r"(.*)(^|[\\\/])(.*)$","\\1\\2"+taskid+"_\\3",zeile1[2])
        newfilename = re.sub(r"(^|[\\\/])"+taskid+"_"+taskid,"\\1"+zeile1[3],newfilename)
        if not newfilename == zeile1[2]:   #   wenn Umbenennung des Tasks noetig ist
            os.popen("mv " + zeile1[2] + " " + newfilename)
            print(("mv " + zeile1[2] + " " + newfilename))


#  4.  Check whether a notification should be sent

        try:
            toaddr = re.sub(r"\s","",open(newowner+"/.notification.txt").read(),   99999999,flags=re.DOTALL)
        except:
            print("No mail notification sent to " + newowner)
            return()
                

#  5.  Create the mailsender object if not yet done

        if not 'mailsender' in self:
            import smtplib
            import email.mime.text
            self.mailsender = smtplib.SMTP()
            self.mailsender.connect(smtphost)


#  6.  Create the mail message
            
        mailmsg = email.mime.text.MIMEText("""
Hello """ + newowner + """,

The task """ + taskdir + "/" + newowner + "/" + newfilename + """
has been assigned to you by """ + oldowner + """

Please work on it via editing the HISTORY Section, and re-assign it to another person's folder in

          """ + taskdir + """
                    
The content of the task is:

---------------------------------------------------------------------
""" + text + """

---------------------------------------------------------------------
The """ + name_of_tracker + """ Tracker, """ + time.asctime() + """

Do not answer to this mail.
""")
        mailmsg['Subject'] = "Task Assignment " + newfilename
        mailmsg['Cc']      = cclist
        if not name_of_tracker.lower() == "dryrun":
            self.mailsender.sendmail(sender,[toaddr],mailmsg.as_string())
        print("Mail sent to " + toaddr + " for task " + newfilename)
                                          
#*************************************************************************

#   7.  Finishing of the changed tasks: new column headers

        for zeile in self.export_data(os.popen("ls */*.csv").readlines()+['not __DIR=ASSIGN','x--_DIR-___-_FILE-'],False):
            taskfile = zeile.strip()
            try:
                text = open(taskfile).read()
            except:
                continue
            text = re.sub(r"_DIR,REST_ASSIGN","ASSIGN,REST",text)  #  <--- new column headers
            open(taskfile,"w").write(text)
            print(taskfile + " rewritten ...")

        os.unlink("x--_DIR-___-_FILE-")

#*************************************************************************


if __name__ == "__main__":
#    print (sys.argv)
    db = DBConn({'type':'sqlite','name':sys.argv[1]})
    Xlsmanager.__dict__[sys.argv[2]](Xlsmanager(db),sys.argv[3:])
