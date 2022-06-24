#  coding:  utf                     
import os,sys,re,glob,time,base64,hashlib,random,functools,hashlib,json

#******************************************************************************

class Konto ():


#******************************************************************************

    def __init__ (self,ktotyp=None):


        self.t0              = 0
        self.digits          = 5
        self.dformat         = "%0" + str(self.digits) + "u" 
                            
        self.len_hkey_str    = "12"
        self.len_hkey_nr     = int(self.len_hkey_str)

        self.acc_line_parser = re.compile(r"^(\d\d\d\d)(..)(\d\d) +(\S+) +(\S+) +(\S+) +(\-?\d+\.\d\d|\-+|\.+) +(.*?) *$")

        self.sortieren       = 1
        self.max_offset      = 5

        self.salden_expand   = "(-[^- ]+){0,99},"

        self.dataset         = {}
        
        self.ktotyp          = ktotyp

        ktodir   = os.path.abspath(".")
        
        self.base_dir = ""   #  Search for a base directory with acc and sum files
        pwd0          = ""
        while (0 == 0):      #  check if we are in a directory with acc files
            acc_files = glob.glob("2*.acc") + glob.glob("base/*.acc") + glob.glob(".base/*.acc") + glob.glob("??_ktobase/*.acc")
            if len(acc_files) > 0:
                m = re.search(r"^(.*[\\\/])(.*)$",os.path.abspath(acc_files[0]))
                if m:
                    self.base_dir = m.group(1) 
                break
            pwd = os.path.abspath(".")
            if pwd0 == pwd:
                break
            pwd0 = pwd
            os.chdir("..")

        if not self.base_dir == "":
            self.base_dir = re.sub(r"//$","/",self.base_dir + "/")

        self.mark("---")
        os.chdir(ktodir)

#**********************************************************************************

    def read_config (self,dir=""):

        if dir == "":
            dir = self.base_dir + "/*.data"


        for config_file in glob.glob(dir):
        
#            print(config_file)
            config1 = open(config_file).read()
#            print(config1)

            try:
                dataset  = json.loads(config1)
            except:
                dataset = None
            
#            print(dataset)
            if dataset:   #   json files
                for o in dataset.keys():
#                    print(o)
                    self.dataset[ o.replace("-","").lower() ] = dataset[o]
                    
            else:         #   proprietary pseudo csv files
                felder = config1.split("\n")
                for zeile in felder:
                    m = re.search(r"^(\S+)\: *(.*?)\"",zeile)
                    if m and not m.group(1).lower() in self.dataset:
                        self.dataset[ m.group(1).lower() ] = m.group(2)
        
        return(self.dataset)


#**********************************************************************************

    def mark (self,remark=""):
        
        t = time.perf_counter()
        if self.t0 > 0:
            print ( ("%9.2f" % ((t-self.t0)*1000)) + " ms for:  " + remark )
        self.t0 = t

#**********************************************************************************

    def kto (self,pattern=None):

        ktodir   = os.path.abspath(".")

        if self.base_dir == "":
            print("No accounting base dir found.")
            return("Error 135")

        if pattern == "SORT":     #   Sortieren aller acc und sum files. Dies ist sinnvoll fuer das syncen
        
            for acc_file in glob.glob(self.base_dir+"*.acc") + glob.glob(self.base_dir+"*.sum"):
                file_text = re.sub(r"\n+$","",open(acc_file).read()).split("\n")
                file_text.sort()
                open(acc_file,"w").write("\n".join(file_text) + "\n")
                return("Accounting base files sorted.")

        ktofile = glob.glob("*.kto")
        if len(ktofile) == 1:
            ktofile = ktofile[0]
        else:
            ktofile = None
            

        pattern0 = None
#        print(pattern,pattern0)
        if ktofile:
            ktodir   = re.sub(r"^(.*[\\\/])(.*).kto$","\\1",os.path.abspath(ktofile))
            ktotext  = open(ktodir+"/"+ktofile).read()
            m        = re.search(r"^(\.|)(\S+)",ktotext)
            if m:
                if len(m.group(1)) > 0:
                    pattern0 = m.group(2)
                else:
                    pattern0 = "^" + m.group(2)
        else:
            ktotext  = ""
            ktodir   = os.path.abspath(".")

#        print(pattern,pattern0)

        self.udir   = ""
        self.stable = 0

        if pattern and len(pattern) > 0 and pattern[0] in ("-",":","."):
            if len(pattern) > 1 and pattern[1] in ("-",":","."):
                pattern = pattern[1:]
                self.stable = 1
            self.udir = pattern[1:]
            if pattern[0] == ":":
                self.udir = "__" + self.udir
            elif pattern[0] == ".":
                self.udir = "_" + self.udir
            if pattern0:
                pattern  = pattern0 + pattern
            else:
                return()

        if not pattern:
            pattern = pattern0

        if not self.udir == "":

            print("UDIR",self.udir)
            try:
                os.mkdir(self.udir)
            except:
                pass
            os.chdir(self.udir)

#        if False and pattern0 and self.udir == "":
#
#            udir = ktodir
#
#            if pattern == None:
#                pattern = pattern0   #  wenn kein pattern angegeben, nimm das pattern aus dem ktofile
#            else:
#
##                if pattern[0] == ".":
##                    pattern = pattern[1:]
##                elif pattern[0] == "-":
##                    pattern = "^" + pattern
#
#                m = re.search(r"^(.*)([\.\:])(.*)",pattern0)
#                if m:
#                    p0 = m.group(1)
#                    m0 = m.group(2)
#                    i0 = m.group(3)
#                else:
#                    p0 = pattern0
#                    m0 = None
#                    i0 = None
#
#                m = re.search(r"^(.*)([\.\:])(.*)",pattern)
#                if m:
#                    p1 = m.group(1)
#                    m1 = m.group(2)
#                    i1 = m.group(3)
#                else:
#                    p1 = pattern
#                    m1 = None
#                    i1 = None
#
#                if not i1:
#                    i1 = i0
#                    m1 = m0
#                    
#                if not i1:
#                    i1 = ""
#                    m1 = ""
#                    
#
#                self.udir = ""
#
#                print("PPP",p1,p0,i1,i0)
#                exit()
#                
#                pattern = p1 + m1 + i1
#                pattern = re.sub(r"\.$","",pattern)

#        print("PATTERN",pattern)
        
        if not pattern:
            return()

        self.update_konto(pattern)
        
        if not self.udir == "":
            if not self.stable:
                while (0 == 0):
                    text1 = open( glob.glob("*.kto")[0] ).read()
                    os.system("joe *.kto")
                    text2 = open( glob.glob("*.kto")[0] ).read()
                    if text1 == text2:
                        for o in glob.glob("*.kto*"):
                            os.unlink(o)
                        os.chdir("..")
                        try:
                            os.rmdir(self.udir)
                        except:
                            pass
                        return()
                    self.update_konto(pattern)


#**********************************************************************************

    def update_konto (self,search_pattern,salden_expand=None):  #  Updates an actual konto
        
        self.search_pattern = search_pattern
        if not salden_expand == None:
            self.salden_expand = salden_expand

        self.parse_pattern()
        
#        print(self.search_pattern,self.grep_pattern)


        self.mark("B. Pattern parsed.")

#        self.list_of_sum_files = glob.glob(base_dir+".*sum)
#
#        if not len(self.list_of_acc_files) == len(self.list_of_sum_files):
#            print("Kto database not proper.")
#            return("Error 207.")


        kto_file          = None
        konto_files_found = glob.glob("*.kto")
        #print(konto_files_found,os.path.abspath("."))
        
        if len(konto_files_found) > 1:
            print("More than one kto file found.")
            return("Error 120.")

        self.mark("C. Existing ktofiles searched.")

        self.extract_account_lines()   #   Prepare formatted konto and salden
        self.mark("D. Extract lines.")
        
        self.format_kto()
        self.mark("E. ktofile formatted.")

        change_acc_files = 0
        while len(konto_files_found) == 1:
        
            kto_file           = konto_files_found[0]
            text               = open(kto_file).read()
            self.processed_acc = text.split("\n")
            m                  = re.search("^.*? ([0123456789abcdef]{"+self.len_hkey_str+"}) ",text)
        
            if not m:
                break
                
            if not m.group(1) == self.hkey:   #  the key which is found in the existing kto-file allows to change the result of the computed sub account
                break                         #  so we take the chance
             
            m = re.search("^(.*?)\n *\n(.*\n\d\d\d\d\d\d\d\d +\-?\d+\.\d\d +\S+ .*?\n)",text,re.DOTALL)   #  Check whether processed file has changed
                
            self.mark("F. Processed ktofile hashkey.")
            if m:
                relevant_text_in_ktofile = m.group(2)
#                print(relevant_text_in_ktofile)
                actual_hkey = hashlib.md5(relevant_text_in_ktofile.encode("utf-8")).hexdigest()[0:self.len_hkey_nr]
                if actual_hkey == self.hkey:
                    return("No change.")        #  Nothing changed at all in the account lines, so do not do anything.
            
            print("... fits.")
            res = self.replace_accountings()    #  the diffs between formatted_acc and processed_acc will be applied to extracted_acc.
            self.mark("G. Replace accounting lines.")
            if res == "null":
                print("-> No action needed.")
                break
            
            self.format_kto(1)               #  make a new formatted_acc from the extracted_acc again.
            self.mark("H. Ktofile formatted again.")
  
            change_acc_files = 1
            break
      
        self.mark("I. Compute salden.")
                    
        if len(konto_files_found) == 0 or re.search(r"([0123456789abcdef]{"+self.len_hkey_str+"})\.kto",kto_file):
            kto_file = self.hkey + ".kto"
            
        
        if len(konto_files_found) == 1 and not kto_file == konto_files_found[0]:
            os.unlink(konto_files_found[0])

        self.mark("J. Write result file.")
                    
        open(kto_file,"w").write( self.title + "\n\n" + "\n".join(self.formatted_acc) + "\n\n" )

        if change_acc_files:

            self.list_of_acc_files = glob.glob(self.base_dir+"*.acc")
#            print(self.list_of_acc_files)
            self.list_of_acc_files.sort()
            
            self.subtract_account_lines()     #  delete the former lines of the search
            self.mark("K. Delete former accounting lines.")
            self.add_account_lines(kto_file)  #  add the new ones
            self.mark("L. Add changed accounting lines.")
            self.update_sum_files()           #  also update the sumfiles
            self.mark("M. Update sum files.")
            self.extract_account_lines()      #   Prepare formatted konto and salden
            self.mark("N. Reload kto file.")
            self.format_kto()
            self.mark("O. ktofile formatted again.")
            open(kto_file,"w").write( self.title + "\n\n" + "\n".join(self.formatted_acc) + "\n\n" )

        self.format_salden()
        open(kto_file,"a").write( "\n".join(self.salden_aktuell) + "\n" )

#**********************************************************************************

    def read_saldo (self,search_pattern,salden_expand=None):
        
        self.mark("read saldo " + search_pattern)
        self.search_pattern = "^" + search_pattern
        if not salden_expand == None:
            self.salden_expand = salden_expand

        self.parse_pattern()
#        print(self.ukto)
        
#        print(self.grep_pattern)
        
        if self.grep_pattern[0] == " ":
            self.ukto = self.grep_pattern[1:]
            self.ukto = re.sub(r"-$","",self.ukto)
            
        self.startdatum = (self.startdatum + "00000000")[0:8]
        self.enddatum   = (self.enddatum   + "99999999")[0:8]

        salden_liste = self.format_salden()

        if len(salden_liste) == 0:
            return(0.00)

        return(float(salden_liste[0][2]))

#        print(self.startdatum,self.enddatum,self.ukto)
        
#**********************************************************************************

    def salden_text (self):
        return("\n".join(self.salden_aktuell)+"\n")

#**********************************************************************************

    def extract_account_lines (self):
    
#    This function extracts the matching lines of a request into a sorted array

#        self.mark("A. Compute query for transaction file " + pattern1 + " " + str(interval)[0:40] + " ...")

#        print("111",self.interval_long,"--"+self.grep_pattern+"--")
        
        if not self.interval_long == "":
            if self.grep_pattern == "":
                self.extracted_acc = os.popen(self.egrep + "grep -h -i ^" + self.interval_long + " " + self.base_dir + "*.acc").read().split("\n")
            else:
                self.extracted_acc = os.popen(self.egrep + "grep -h -i ^" + self.interval_long + " " + self.base_dir + "*.acc | grep -h -i '" + self.grep_pattern + "'").read().split("\n")
        else:
            if self.grep_pattern == "":
                self.extracted_acc = os.popen("less " + self.base_dir + "*.acc").read().split("\n")
            else:
                self.extracted_acc = os.popen(self.egrep + "grep -h -i '" + self.grep_pattern + "' " + self.base_dir + "*.acc").read().split("\n")

        self.extracted_acc.sort()        

#**********************************************************************************

    def parse_pattern (self):    #   parse the search pattern

        self.grep_pattern     = re.sub(r"\^"," ",self.search_pattern,9999)
        self.interval_long    = ""
        self.interval_short   = ""
        self.egrep            = ""
        self.mode             = ""
        self.startdatum       = "00000000"
        self.enddatum         = "99999999"

        m                     = re.search(r"^(.*)([\.\:])(.*)$",self.grep_pattern)
            
        if m:

            self.grep_pattern   = m.group(1)
            self.mode           = m.group(2)
            self.interval_long  = "20" + m.group(3)[0:2]
            months              = m.group(3)[2:]
            self.interval_short = m.group(3)
            
            if   months == "A":
                months  = "10"
                first_m = "10"
                last_m  = "10"
            elif months == "B":
                months  = "11"
                first_m = "11"
                last_m  = "11"
            elif months == "C":
                months  = "12"
                first_m = "12"
                last_m  = "12"
            elif months == "I":
                months  = "0[123]"
                first_m = "01"
                last_m  = "03"
            elif months == "J":
                months  = "0[456]"
                first_m = "04"
                last_m  = "06"
            elif months == "K":
                months  = "0[789]"
                first_m = "07"
                last_m  = "09"
            elif months == "L":
                months  = "1[012]"
                first_m = "10"
                last_m  = "12"
            elif months == "M":
                months  = "0[123456]"
                first_m = "01"
                last_m  = "06"
            elif months == "N":
                months  = "\\(07\\|08\\|09\\|10\\|11\\|12\\)" # "[01][789012]"
                first_m = "07"
                last_m  = "12"
                egrep   = "e"
            elif months == "P" or months == "":
                months  = ""
                first_m = "01"
                last_m  = "12"
            elif not months == "":
                months  = "0" + months
                first_m = months
                last_m  = months
       
            if self.mode == ":":
                intervals = []
                jahr      = "2000"
                while (0 == 0):
                    intervals.append(jahr)
                    jahr = str(int(jahr)+1)
                    if jahr == self.interval_long:
                        break
                if last_m == "12":
                    intervals.append(jahr)
                else:
                    month = "01"
                    while (0 == 0):
                        intervals.append(jahr+month)
                        if month in (last_m,"12"):
                            break
                        month = "%02u" % (int(month) + 1)
                self.interval_long = "\\(" + "\\|".join(intervals) + "\\)"
                self.egrep = "e"
                self.startdatum = intervals[0]
                self.enddatum   = intervals[-1]
                

            else:
                self.startdatum    = self.interval_long + first_m + "00"
                self.enddatum      = self.interval_long + last_m  + "99"
                self.interval_long = self.interval_long + months

#        print(self.startdatum,self.enddatum)



                
#        if self.search_pattern[0] == "^":
#            self.start_kto    = re.sub(r"[\^ ]",""self.grep_pattern,9999)
#        else:
#            self.start_kto    = None


#**********************************************************************************

    def format_kto (self,mode=0):
        
        self.parse_ktotext()
                
#   ktotext:   datum  betrag   kto1   kto2   saldo   bemerkung   original_line
                
        if self.ukto == "":
            self.buchungen.sort(key=lambda x:x[0]+str(x[1])+x[3]+x[4])
        else:
            print("UKTO: " + self.ukto)
#            ktotext.sort(key=lambda x:str(x[5]+1)+x[0])
            self.buchungen.sort(key=lambda x:x[0]+str(x[5]+1)+x[2]+x[3]+x[4])
            

        gesamt              = 0.00
        self.startdatum     = "00000000"
        self.enddatum       = "00000000"
        dbl_marks           = {}
        self.formatted_acc  = []
        self.extracted_acc  = []    #  das orig-File muss in der neuen Sortierung auch neu geschrieben werden,
                                    #  damit man am Ende den Patch auf das formatierte Konto-File anwenden kann.

        has_doublettes = 0
        datum          = ""
        for zeile in self.buchungen:   #   step through all accounting lines
                
            ust = ""
            if "v.H." in zeile[4]:
                ust = "   "

            betrag = zeile[1]
            ktoa   = zeile[2]
            ktob   = zeile[3]
            datum  = zeile[0]
            
            if not ktoa.startswith(self.ukto):
                o      = ktoa   
                ktoa   = ktob   
                ktob   = o
                betrag = re.sub(r"^--","","-"+betrag)
            
            if mode == 0 and not ktoa.startswith(self.ukto) and self.grep_pattern[0] == " ":
                print("SKIP: ",self.ukto,zeile)
                continue
                
#            print(ukto,zeile)
            betrag = float(betrag)

            if self.ukto == "":
                gesamt = gesamt + betrag
                saldo  = "%13.2f" % gesamt
            else:
                if zeile[5] == 0:            #  zeile[5]: the number of matching ukto in ktoa or ktob
                    if mode == 0:
                        saldo = "         ...."
                    else:
                        saldo = "         0.00"   #  for uploading into acc-files
#                    saldo  = "%13.2f" % gesamt
                elif self.maxsaldo == 0 or zeile[5] == 1:
                    gesamt = gesamt + betrag
                    saldo  = "%13.2f" % gesamt
                elif zeile[5] == 2:
                    saldo  = "%13.2f" % gesamt

            dbl_z    = datum + " " + ("%13.2f" % betrag) + "  " + (self.format_maxa % ktoa) + "  " + (self.format_maxb % ktob)
            rem_z    = ust + re.sub(r" +"," ",zeile[4],9999)
            zeile1   = dbl_z + " " + saldo + "  " + rem_z

            dbl_mark = dbl_z + rem_z   #  wenn Doubletten gefunden werden, diese eindeutig markieren
            if not dbl_mark in dbl_marks:
                dbl_marks[dbl_mark] = 0
            else:
                dbl_marks[dbl_mark] = dbl_marks[dbl_mark] + 1
                zeile1 = zeile1 + " DOUBLETTE " + str(dbl_marks[dbl_mark])
                has_doublettes = 1
            
            self.extracted_acc.append(zeile[6])
            self.formatted_acc.append(zeile1)
            if self.startdatum == "00000000":
                self.startdatum = datum

        if not datum == "":
            self.enddatum = datum

        if self.ukto == "":
            self.ukto = "." + self.search_pattern
            interval  = ""
        else:
            interval  = self.mode + self.interval_short
            
        if self.grep_pattern[-1] == "-":
            add_minus = "-"
        else:
            add_minus = ""


        self.hkey   = "\n".join(self.formatted_acc) + "\n"
        self.hkey   = hashlib.md5(self.hkey.encode("utf-8")).hexdigest()[0:12]
        self.title  = ("%-50s"%(re.sub(r"\.$","",self.ukto+add_minus+interval))) + " " + self.hkey + "       " + ("%13.2f"%gesamt)
#        print(self.title)


        if has_doublettes:
            print("Attention: Doublettes!")

#**********************************************************************************

    def parse_ktotext (self):

        self.buchungen      = []
        unique_strings      = {}
        self.maxa           = 10
        self.maxb           = 10
        self.maxc           = 0
        self.maxd           = 0
        self.maxsaldo       = 0
        self.ukto           = ""
        ukto0               = ""
        pattern             = self.grep_pattern.strip().upper()
        
        if self.grep_pattern[0] == " ":
            self.ukto = self.grep_pattern[1:]
            self.ukto = re.sub(r"-$","",self.ukto)
        
        if len(pattern) > 0 and pattern[-1] == "-":
            pattern = pattern[:-1]

        zaehler = -1
        vvv = re.compile(r"^(\d\d\d\d)(..)(\d\d) +(\S+) +(\S+) +(\S+) +(\-?\d+\.\d\d|\-+|\.+) +(.*?) *$")
        for zeile in self.extracted_acc:

            mm = vvv.search(zeile)
            if not mm:   #   Einlesen der Kontobezeichnungen
#                    self.buchungen.append(["00000000",zeile,"","","",-1])
                continue

#            if self.start_kto:
#                if mm.group(5).startswith(self.start_kto) or mm.group(6).startswith(self.start_kto) ):
#                    new_extracted_acc.append(zeile)
#                else:
#                    self.remaining_acc.append(zeile)
#                    continue

            if mm.group(2) == "MM":
                monate = ["01","02","03","04","05","06","07","08","09","10","11","12"]
            else:
                monate = [mm.group(2)]

            for monat in monate:

                datum  = mm.group(1) + monat + mm.group(3)
                try:
                    betrag = "%3.2f" % eval(mm.group(4))
                except:
                    exit()

                remark   = mm.group(8)
                uniqu    = []
                ktoa     = mm.group(5)
                ktob     = mm.group(6)
                
                if "--" in ktoa or "--" in ktob:
                    continue
                
                turn_kto = 0

#                    ktoa = self.parse_ktotext_compute_kto(m.group(5),self.ukto,uniqu)
#                    ktob = self.parse_ktotext_compute_kto(m.group(6),self.ukto,uniqu)

                if ktoa > ktob:     #  to avoid swing back anf forth
                    o      = ktoa   
                    ktoa   = ktob   
                    ktob   = o
                    betrag = re.sub(r"^--","","-"+betrag)
                    turn_kto = 1 - turn_kto
                    
                if not ktoa.upper().startswith(pattern):
                    o      = ktoa   
                    ktoa   = ktob   
                    ktob   = o
                    betrag = re.sub(r"^--","","-"+betrag)

                saldo = 0
                if not self.grep_pattern[0] == " " and not self.ukto == None:   #  find self.ukto dynamically
                    
                    if self.ukto == "":
                        if pattern in ktoa.upper():
                            self.ukto = ktoa
                            
                    for kto in (ktoa,ktob):
                        if pattern in kto.upper():
                            while (0 == 0):
                                if not pattern in self.ukto:
                                    break
                                if kto.startswith(self.ukto):
                                    break
                                m = re.search(r"^(.*)\-(.*)$",self.ukto)
                                if m:
                                    self.ukto = m.group(1)
                                else:
                                    self.ukto = ""
                                print("           fit ukto: " + self.ukto.replace("^",""))
                            if not pattern in self.ukto.upper():
                                self.ukto = None
                                print("No ukto found.")
                                salden = None
                            break

                if self.ukto:
                    while (0 == 0):
                        m = re.search(r"^(.*)\-(.*)$",self.ukto)
                        if not m or not pattern in m.group(1).upper():
                            break
                        self.ukto  = m.group(1)
                        ukto0 = re.sub(r"\^","",self.ukto)
                

                if self.ukto:
                    saldo = ( int( self.ukto and ktoa.startswith(self.ukto)) +
                              int( self.ukto and ktob.startswith(self.ukto)) )
                    
                if uniqu == []:
                    uniqu = [ktoa,ktob]

                self.maxsaldo = max(self.maxsaldo,saldo)
                uniqu1  = []
                for k in uniqu:
                    uniqu1.append(re.sub(r"\-\d\d\d\d\d$","-BETRAG",k))
                uniqu   = uniqu1

                betrag1 = re.sub("\-","",betrag) + ","
                remark1 = "," + re.sub(r"[\+\- ]","",remark,9999)
                uniqu   = betrag1 + ",".join(uniqu) + remark1

#                if datum in unique_strings:  #  to avoid double entries
#                    if uniqu in unique_strings[datum]:
#                        continue  #  der Eintrag mit diesem unique-String existiert schon, daher nicht nochmal nehmen
#                    else:
#                        unique_strings[datum].append(uniqu)
#                else:
#                    unique_strings[datum] = [uniqu]

                ktoa = ktoa.replace("^","")
                ktob = ktob.replace("^","")

                if ktoa[0] == "-":
                    self.maxc = max(self.maxc,len(ktoa))
                else:
                    self.maxa = max(self.maxa,len(ktoa))

                if ktob[0] == "-":
                    self.maxd = max(self.maxd,len(ktob))
                else:
                    self.maxb = max(self.maxb,len(ktob))

                self.buchungen.append([datum,betrag,ktoa,ktob,remark,saldo,zeile])

        if self.ukto == None:
            self.ukto = ""
        self.ukto = self.ukto.replace("^","")

        if self.maxc > 0:
            self.maxa = max(self.maxa,len(self.ukto)+self.maxc)
        if self.maxd > 0:
            self.maxb = max(self.maxb,len(self.ukto)+self.maxd)

        self.format_maxa = "%-" + str(self.maxa) + "s"
        self.format_maxb = "%-" + str(self.maxb) + "s"
        self.maxsaldo    = str(self.maxsaldo)


#*******************************************************************************************

    def format_salden (self):

        faktor              = 1
#        kto                 = self.ukto

        self.salden_aktuell = []

        ktofiles1 = glob.glob(self.base_dir+"*.acc")
        ktofiles1.sort()
        ktofiles  = []
        
#        print(self.base_dir)

#        self.mark("A")
        for ktofile in ktofiles1:

#            print(ktofile  + " ...")
            ktofile_sum = ktofile[:-4] + ".sum"
            if not os.path.isfile(ktofile_sum):
                self.mark("    " + ktofile + " not found, so retrieve it:")
                self.update_sum_files(ktofile)
            
            m = re.search(r"(\d+)\.acc$",ktofile)
            if len(ktofiles) < 2:
                if (m.group(1) + "000000")[0:6] < self.startdatum:
                    ktofiles = []
            if (m.group(1) + "000000")[0:6] > self.enddatum:
                break
            else:
                ktofiles.append(ktofile_sum)

#        self.mark("B")
        if not self.ukto == None and not self.ukto == "" and self.ukto[0] in ("-","."):
            return()
#            faktor = -1
#            kto    = kto0[1:]

        ktoparse = "^" + self.ukto + self.salden_expand
#        print(ktoparse)
            
        self.enddatum   = (self.enddatum   + "99999999")[0:6]
        self.startdatum = (self.startdatum + "00000000")[0:6]

        if self.enddatum[4:6] > "12":
            self.enddatum = self.enddatum[0:4] + "12" 

        ktotexts = []
#        print("KTOPARSE",ktoparse)
        for ktofile in ktofiles:  #  retrieving of the relevant lines via grep
#            print(ktofile)
            ktotexts.append([])
            for zeile in os.popen("grep -P '" + ktoparse + "' " + ktofile).read().split("\n")[:-1]:
                ktotexts[-1].append(zeile.split(","))

#        for o in ktotexts[0]:
#            print(o)


        salden_liste    = []
        max_offset      = self.max_offset
        max_kto_ordnung = 0
        len_ukto        = len(self.ukto) + 1
        
        kto0 = " "
        while (0 == 0):   #   alle konten-Salden gleichzeitig nach vorne schieben, dabei auf luecken achten
            kto = None
            for ktotext in ktotexts:
                if len(ktotext) == 0:
                    continue
                if kto == None:
                    kto = ktotext[0][0]
                else:
                    kto = min(ktotext[0][0],kto)
            if kto == None:
                break
                
            betrag = 0.00
            nr     = 0

            if len(ktotexts[0]) > 0 and kto == ktotexts[0][0][0]:   #  in the first line there is the kto. Find in the first file the position
                zeile  = ktotexts[0][0][1:]  #  nicht entfernen!
                datum0 = zeile.pop(0)
                if self.startdatum >= datum0:
                    datpos = 12*( int(self.startdatum[0:4]) - int(datum0[0:4]) ) + int(self.startdatum[4:6]) - int(datum0[4:6]) - 1
#                    print("START",self.startdatum,datum0,kto,datpos)
                    if datpos < 0:
                        betrag = 0.00
                        nr     = 0
                    elif datpos >= len(zeile):
#                        print(kto,zeile)
                        if zeile[-1][-self.digits-1] == "/":
                            betrag = betrag - float(zeile[-1][:-self.digits-1])
                            nr     = nr     - int(zeile[-1][-self.digits:])
                        else:
                            ind    = zeile[-1].index("/")
                            betrag = betrag - float(zeile[-1][:ind-1])
                            nr     = nr     - int(zeile[-1][ind:])
                    else:
                        if zeile[datpos][-self.digits-1] == "/":
                            betrag = betrag - float(zeile[datpos][:-self.digits-1])
                            nr     = nr     - int(zeile[datpos][-self.digits:])
                        else:
                            ind    = zeile[datpos].index("/")
                            betrag = betrag - float(zeile[datpos][:ind-1])
                            nr     = nr     - int(zeile[datpos][ind:])
                
#            print("        ",kto,nr,datpos)

            if len(ktotexts[-1]) > 0 and kto == ktotexts[-1][0][0]:   #  im letzten Salden-File die genaue Monatsspalte finden
#                zeile  = ktotexts[-1][0][1:]  #  nicht entfernen!
                zeile  = ktotexts[-1].pop(0)[1:]
                datum0 = zeile.pop(0)
                if self.enddatum >= datum0:
                    datpos = 12*( int(self.enddatum[0:4]) - int(datum0[0:4]) ) + int(self.enddatum[4:6]) - int(datum0[4:6])

                    if datpos >= len(zeile):
                        if zeile[-1][-self.digits-1] == "/":
                            betrag = betrag + float(zeile[-1][:-self.digits-1])
                            nr     = nr     + int(zeile[-1][-self.digits:])
                        else:
                            ind    = zeile[-1].index("/")
                            betrag = betrag + float(zeile[-1][:ind-1])
                            nr     = nr     + int(zeile[-1][ind:])
                    else:
                        if zeile[datpos][-self.digits-1] == "/":
                            betrag = betrag + float(zeile[datpos][:-self.digits-1])
                            nr     = nr     + int(zeile[datpos][-self.digits:])
                        else:
                            ind    = zeile[datpos].index("/")
                            betrag = betrag + float(zeile[datpos][:ind-1])
                            nr     = nr     + int(zeile[datpos][ind:])

#            print("        ",kto,nr,datpos)
                
            for ktotext in ktotexts[:-1]:   #  nur bei sum-up Werten relevant (Zwischen-sum-Files)
                if len(ktotext) > 0 and ktotext[0][0] == kto:
                    zeile  = ktotext.pop(0)
                    
                    if zeile[-1][-self.digits-1] == "/":
                        betrag = betrag + float(zeile[-1][:-self.digits-1])
                        nr     = nr     + int(zeile[-1][-self.digits:])
                    else:
                        ind    = zeile[-1].index("/")
                        betrag = betrag + float(zeile[-1][:ind-1])
                        nr     = nr     + int(zeile[-1][ind:])
                    
            if nr > 0:
                
                betrag          = "%3.2f" % (faktor*betrag)
                kto             = kto[len_ukto:]
                kto_ordnung     = max(0,len(re.sub("[^\-]","",kto)))
                if kto == "":
                    kto_ordnung = -1
                max_offset      = max(max_offset,len(kto) + len(betrag) - 4*kto_ordnung)
                max_offset      = max(max_offset,len_ukto)
                max_kto_ordnung = max(max_kto_ordnung,kto_ordnung)
                salden_liste.append([kto,kto_ordnung,betrag])
                

        for salden_zeile in salden_liste:
        
            kto = salden_zeile[0]
            if not self.ktotyp == None:
                bed = 0
                if not "-" in kto:
                    bed = 1
                else:
                    for ktyp in self.ktotyp:
                        if re.search("^"+ktyp+r"-[^\-]+$",kto):
                            bed = 1
                            break
                if bed == 0:
                    continue

            kto_ordnung = salden_zeile[1]
            betrag      = salden_zeile[2]
            kto_spacing = "%-" + ("%2u"% (max_offset+kto_ordnung*4-len(betrag)+2) ) + "s"
            if kto_ordnung == 0 and max_kto_ordnung > 0:   #   additional spacing
                self.salden_aktuell.append("")
            self.salden_aktuell.append( (kto_spacing%kto) + betrag )
            if kto_ordnung == -1 and max_kto_ordnung < 1:
                self.salden_aktuell.append("")
                
        return(salden_liste)


#        print(max_kto_ordnung)
#        print(self.salden_aktuell)

#**********************************************************************************

    def replace_accountings (self):
    
#   Here we create the array add_lines (lines which are added in processed_acc), del_lines (lines which
#   are deleted in processed_acc), line_numbers_of_deleted (the line numbers in the array of the original
#   formatted_acc which have been deleted in  processed_acc).

        self.differences_to_consider()

        if len(self.add_lines) + len(self.del_lines) == 0:
            return("null")
        
#   Now we apply these changes to the original raw file  extracted_acc :

        new_extracted_acc = self.add_lines[:]     #  new version of the text of  extracted_acc. We start with the added lines

#   Deleted lines:
#   Because the line-by-line correspondency of  extracted_acc  and formatted_acc  we can apply the numbers in  line_numbers_of_deleted
#   directly to extracted_acc (by considering an offset of 2 because of the both additional header lines made from the formatting)

        self.dates_of_deleted_lines     = []            #  we collect all months of all lines which have been deleted for later purposes

        zaehler = 0 
        for zeile in self.extracted_acc:
            if zaehler in self.line_numbers_of_deleted:
                if not zeile[0:6] in self.dates_of_deleted_lines:
                    self.dates_of_deleted_lines.append(zeile[0:6])
            else:
                new_extracted_acc.append(zeile)
            zaehler = zaehler + 1
                    
        self.extracted_acc = new_extracted_acc
        self.extracted_acc.sort()
        
#**********************************************************************************

    def differences_to_consider (self):
    
        set_of_formatted_lines = set( self.formatted_acc )
        set_of_processed_lines = set( self.processed_acc )

#       First, we determine the vice versa differences of the sets of lines in formatted_acc and processed_acc:

        set_of_added_lines     = set_of_processed_lines.difference(set_of_formatted_lines)
        set_of_deleted_lines   = set_of_formatted_lines.difference(set_of_processed_lines)
 
#       Changes which may consist simply by changing spaces or the sum in the fith column of an account set
#       should be skipped. So we calculate now all these normalisations and map it to the original line.
#       Also lines which are not an account entry should be skipped.

#       (Actually, we could do it one-step by normalize all the lines in formatted_acc and processed_acc. But it is
#       costly to normalize all this lines, even, if these are not affected by changes. So it is waste of ressources.
#       Hence, it makes sense firstly make a raw difference  set_of_added_lines  and  set_of_deleted_lines  which
#       afterwards can be reduced by normalization.)

        set_of_normalized_added_lines,   dict_of_normalized_added_lines_to_orig_added_lines     = self.normalize_acc_line_set(set_of_added_lines)
        set_of_normalized_deleted_lines, dict_of_normalized_deleted_lines_to_orig_deleted_lines = self.normalize_acc_line_set(set_of_deleted_lines)
        
#        print(dict_of_normalized_added_lines_to_orig_added_lines)
#        print(dict_of_normalized_deleted_lines_to_orig_deleted_lines)


#       The sets of the normalized added and deleted reduced lines sets are calculated by deleted elements common to both of this sets

        reduced_set_of_normalized_added_lines   = set_of_normalized_added_lines.difference(set_of_normalized_deleted_lines)
        reduced_set_of_normalized_deleted_lines = set_of_normalized_deleted_lines.difference(set_of_normalized_added_lines)

#        print(reduced_set_of_normalized_added_lines)
#        print(reduced_set_of_normalized_deleted_lines)


#       As a last step, we find back the original lines by the both dictionaries:

        self.add_lines               = []
        for normalized_line in reduced_set_of_normalized_added_lines:
            orig_zeile = dict_of_normalized_added_lines_to_orig_added_lines[ normalized_line ]
            self.add_lines.append( orig_zeile )

        self.del_lines               = []
        self.line_numbers_of_deleted = []
        for normalized_line in reduced_set_of_normalized_deleted_lines:
            orig_zeile = dict_of_normalized_deleted_lines_to_orig_deleted_lines[ normalized_line ]
            self.del_lines.append("-" +  orig_zeile )
            self.line_numbers_of_deleted.append( self.formatted_acc.index( orig_zeile ) )

#********************************************************************************************        

    def normalize_acc_line_set (self,line_set):
        
        normalized_lines                    = []
        dict_normalized_lines_to_orig_lines = {}
        
        for zeile in line_set:          #  ueber Aequivalenzbeziehung weitere uebereinstimmende Zeilen herausfinden
            m = self.acc_line_parser.search(zeile)
            if m:
                zeile1 = m.group(1) + m.group(2) + m.group(3) + "  " + ("%3.2f"%eval(m.group(4))) + "  " + m.group(5) + "  " + m.group(6) + "  0.00  " + m.group(8)
            else:
                continue      #  nur Buchungszeilen sind zu beruecksichtigen
            normalized_lines.append(zeile1)
            dict_normalized_lines_to_orig_lines[zeile1] = zeile
        
        return(set(normalized_lines),dict_normalized_lines_to_orig_lines)
        
#*******************************************************************************************

    def impacts_acc_file(self,ktofile,mode=0):

        m = re.search(r"(\D|^)(\d+)\.acc",ktofile)
        if not m:
            return(False)
        zeitraum = m.group(2)

        if mode == 1:
            return(zeitraum)

        if zeitraum < self.startdatum[0:len(zeitraum)]:
            return(False)
        if zeitraum > self.enddatum[0:len(zeitraum)]:
            return(False)

        return(zeitraum)

#*******************************************************************************************
        
    def subtract_account_lines (self): 

#   This function deletes accounting lines from the acc-files due to a pattern

        for ktofile in self.list_of_acc_files:

            if not self.impacts_acc_file(ktofile):
                continue

            if not self.interval_long == "":
                if self.grep_pattern == "":
                    os.system(self.egrep + "grep -i -v ^" + self.interval_long + " " + ktofile + " > " + ktofile + "__")
                else:
                    os.system(self.egrep + "grep -i -v ^" + self.interval_long + " " + ktofile + " > " + ktofile +  "__")
                    os.system(self.egrep + "grep -i ^" + self.interval_long + " " + ktofile + " | grep -i -v '" + self.grep_pattern + "' >> " + ktofile + "__")
            else:
                if self.grep_pattern == "":
                    os.system(" > __" + self.base_dir + ktofile)
                else:
                    os.system(self.egrep + "grep -i -v '" + self.grep_pattern + "' "  + ktofile + " > " + ktofile + "__")
                    
            os.system("mv " + ktofile + "__ " + ktofile)

        self.mark("D. Subtract old accounting entries from acc files.")
                
#********************************************************************************************        

    def add_account_lines (self,kto_file):

        for acc_file in self.list_of_acc_files:

            zeitraum = self.impacts_acc_file(acc_file)
            if zeitraum:

                os.system("grep ^" + zeitraum + " " + kto_file + " >> " + acc_file)
                if self.sortieren == 1:    #   hier die acc-Files wieder sortieren
                    file_text = re.sub(r"\n+$","",open(acc_file).read()).split("\n")
                    file_text.sort()
                    open(acc_file,"w").write("\n".join(file_text) + "\n")
#                    self.mark("C. " + ktofile + " sorted.")
#                    os.system("sort " + ktofile + " > " + "__" + ktofile)
#                    os.system("mv __" + ktofile + " " + ktofile)
                
#*************************************************************************

    def update_sum_files (self,acc_file=None):
    
        salden_files = []
        
        if acc_file:
            list_of_changed_lines = open(acc_file).read().split("\n")
            mode                  = 1
            list_of_acc_files     = [acc_file]
        else:
            list_of_changed_lines = self.add_lines + self.del_lines
            mode                  = 0
            list_of_acc_files     = self.list_of_acc_files
#        print("\n".join(list_of_changed_lines))

        for acc_file in list_of_acc_files:

            abschnitt = self.impacts_acc_file(acc_file,mode)
            if not abschnitt:
                continue

            diff_salden          = {}
            buchung_im_lfd_monat = {}

            salden_file  = acc_file[0:-4] + ".sum"
            salden_files.append(salden_file)

            salden_text = []
            if os.path.isfile(salden_file):    
                salden_text = open(salden_file).read().strip().split("\n")   #  update der salden_files

            update_salden = 0
            for diff_buchung in ( list_of_changed_lines ):
#                print("DD",diff_buchung)
                m = re.search("^(\-?)(\d\d\d\d\d\d\d\d) +(\S+) +(\S+) +(\S+) +(\-?\d+\.\d\d|\.+)",diff_buchung)
                if m:
                    if update_salden == 0:
                        update_salden = 1
                        self.mark("--> Check " + acc_file + ".")
                    datum  = m.group(2)
                    if datum.startswith(abschnitt):
                        betrag = eval(m.group(3))
                        ktoa   = m.group(4)
                        ktob   = m.group(5)
                        add_buchung = 1
                        if m.group(1).startswith("-"):
                            betrag      = -betrag
                            add_buchung = -1
                        self.compute_salden(diff_salden,buchung_im_lfd_monat,ktoa, betrag,add_buchung,datum) 
                        self.compute_salden(diff_salden,buchung_im_lfd_monat,ktob,-betrag,add_buchung,datum)


            kto_to_del    = []
            update_salden = 0

            for kto in list(diff_salden.keys()):

                if update_salden == 0:
                    update_salden = 1
                    self.mark("--> Diff salden computed.")
                    
                interval0 = -1   # suchen, ob es schon eine gueltige Zeile gibt
                interval1 = len(salden_text)
                while (0 == 0):
                    if interval0 + 1 == interval1:  #  not found
                        interval9 = -1
                        break
                    interval9 = interval0 + int((interval1 - interval0)/2)
#                    print(interval0,interval9,interval1,kto)
#                    time.sleep(0.01)
                    if salden_text[interval9].startswith(kto+","):
                        break
                    if (kto + ",") > salden_text[interval9]:
                        interval0 = interval9
                    else:
                        interval1 = interval9
                                    
                if interval9 > -1:   #   wenn es schon eine Konto-Zeile im Salden-File gibt, diese integrieren

                    werte = salden_text[interval9].split(",")
                    werte.pop(0)
                    if len(werte) > 0:
                        monat   = int(werte.pop(0))
                        betrag0 = 0.00
                        nr0     = 0
                        for betrag in werte:
                            if betrag[-self.digits-1] == "/":
                                nr     = int(betrag[-self.digits:])
                                betrag = float(betrag[:-self.digits-1])
                            else:
#                                print(kto,betrag)
                                ind    = betrag.index("/")
                                betrag = int(m.group(1))
                                nr     = float(m.group(2))
                            if not monat in diff_salden[kto]:
                                diff_salden[kto][monat]           = 0.00
                                buchung_im_lfd_monat[kto][monat]  = 0
                            diff_salden[kto][monat]          = diff_salden[kto][monat]          + betrag - betrag0
                            buchung_im_lfd_monat[kto][monat] = buchung_im_lfd_monat[kto][monat] + nr     - nr0
                            betrag0 = betrag
                            nr0     = nr
                            monat   = monat + 1
                            if str(monat)[4:6] == "13":
                                monat = int(str(int(str(monat)[0:4]) + 1) + "01")
                            
                monate   = list(diff_salden[kto].keys())
                monat    = min(monate)
                mmax     = max(monate)
                zeile    = kto + ","
                betraege = []
                sum      = 0.00    #   @@@@
                nr       = 0
                
                while (0 == 0):
#                    nr = 0
                    if monat in diff_salden[kto]:
                        sum = sum + diff_salden[kto][monat]
                        nr  = nr  + buchung_im_lfd_monat[kto][monat]
                    if len(betraege) > 0:
                        betraege.append(("%3.2f"%sum)+"/"+(self.dformat%nr))
                    elif abs(sum) > 0.000001 or nr > 0:    #  just start when something interesting started
                        betraege.append(("%3.2f"%sum)+"/"+(self.dformat%nr))
                        zeile = zeile + str(monat) + ","
                    monat   = monat + 1
                    if str(monat)[4:6] == "13":
                        monat = int(str(int(str(monat)[0:4]) + 1) + "01")
                    if monat > mmax:
                        break

#                while (0 == 0):    #   truncate the tail if there is nothing interesting anymore
#                    if len(betraege) < 2:
#                        break
#                    if not betraege[-1] == betraege[-2]:
#                        break
#                    betraege.pop()

                if len(betraege) == 0:
                    kto_to_del.append(kto)
                else:
                    zeile = zeile + ",".join(betraege)
                    if len(kto_to_del) > 0 and kto in kto_to_del:
                        kto_to_del.remove(kto)

                if interval9 > -1:
                    salden_text[interval9] = zeile   #  update line
                else:
                    salden_text.insert(interval1,zeile)   #  line was not existing, so enter it
                
            if update_salden == 1:
                self.mark("F. Salden list updated.")
                if len(kto_to_del) == 0:
                    salden_text = "\n".join(salden_text) + "\n"
                else:
                    salden_text = "\n" + "\n".join(salden_text) + "\n"
                    self.mark("   ---")
                    for delkto in kto_to_del:
                        ind         = salden_text.index("\n"+delkto+",")
                        salden_text = salden_text[:ind] + salden_text[ind+len(delkto)+2:]
                    salden_text = salden_text[1:]
#                    self.mark("   .... kto s deleted from sum-file:\n" + "\n".join(kto_to_del))
                open(salden_file,"w").write(salden_text)   #  update der salden_files

#**********************************************************************************

    def compute_salden (self,salden,buchung,ukto,betrag,add_buchung,datum):   #  Splits the accounting entry and
                                                                              #  and computes the cahnges for every
        monat = int(datum[0:6])                                               #  sub-account
        while (0 == 0):
            if not ukto in salden:
                salden[ukto]  = {}
                buchung[ukto] = {}
            if not monat in salden[ukto]:
                salden[ukto][monat]  = 0.00
                buchung[ukto][monat] = 0
            salden[ukto][monat]  = salden[ukto][monat]  + betrag
            buchung[ukto][monat] = buchung[ukto][monat] + add_buchung
            m = re.search(r"^(.*)\-(.+)$",ukto)
            if m:
                ukto = m.group(1)
            else:
                return()

#*************************************************************************
        
    def test_extract_lines (self,basedir,pattern):
    
        self.update_konto(basedir,pattern)
#        print("\n".join(self.formatted_acc)+"\n")
#        print("\n".join(self.salden_aktuell)+"\n")
        
#******************************************************************************

    def sort (self,pattern,file=None):
    
        if file == None:
            files = glob.glob("*.kto")
            if len(files) == 1:
                file = files[0]
            else:
                return()

        if pattern == "..":
            self.sort_numbers(file)
            return()

        if pattern == "kto":
            self.sort_numbers1(file)
            return()

        text = open(file).read()
        text_match = []
        text_rest  = []
        
        for zeile in text.split("\n"):
            if re.search(pattern,zeile,re.IGNORECASE):
                text_match.append(zeile)
            else:
                text_rest.append(zeile)
                
        text = "\n".join(text_rest) + "\n" + "\n".join(text_match) + "\n"
        if os.path.isfile(file+"~"):
            os.unlink(file+"~")
#        os.rename(file,file+"~")
        open(file,"w").write(text)

#******************************************************************************

    def sort_numbers (self,file):
    
        text = open(file).read()
        text_match = []
        text_rest  = []
        
        for zeile in text.split("\n"):
            m = re.search(r"\d\d\d\d\d\d\d\d +\-?(\d+\.\d\d) ",zeile)
            if m:
                text_match.append([zeile,float(m.group(1))])
            else:
                text_rest.append(zeile)
                
        text_match.sort(key=lambda x:x[1])
        text_match1 = []
        for tt in text_match:
            text_match1.append(tt[0])

        text = "\n".join(text_rest) + "\n" + "\n".join(text_match1) + "\n"
        if os.path.isfile(file+"~"):
            os.unlink(file+"~")
#        os.rename(file,file+"~")
        open(file,"w").write(text)

#******************************************************************************

    def sort_numbers1 (self,file):
    
        text = open(file).read()
        text_match = []
        text_rest  = []
        
        for zeile in text.split("\n"):
            m = re.search(r"(\d\d\d\d\d\d\d\d) +\-?(\d+\.\d\d) +(\d+?)\-(\S+?)\-(\S+) ",zeile)
            if m:
                text_match.append([zeile,m.group(5)])
            else:
                text_rest.append(zeile)
                
        text_match.sort(key=lambda x:x[1])
        text_match1 = []
        for tt in text_match:
            text_match1.append(tt[0])

        text = "\n".join(text_rest) + "\n" + "\n".join(text_match1) + "\n"
        if os.path.isfile(file+"~"):
            os.unlink(file+"~")
#        os.rename(file,file+"~")
        open(file,"w").write(text)

#*************************************************************************
        
    def xxggg (self):
        
        diff_salden              = {}
        dates_of_deleted_entries = []  #  das wird eine Liste aus Monaten, in denen gar keine Buchungen mehr stehen


#   ----  1.  Vergleich zwischen dem originalen result.format und result.kto

        add_lines       = []
        del_lines       = []

        if os.path.isfile(file+".format") and os.path.isfile(file+".kto"):   

            sortierte_zeilen   = open(file + ".format").read().split("\n")
            text0              = set(open(file + ".kto").read().split("\n"))

            diff_sort_z        = set(sortierte_zeilen).difference(text0)  #  erstmal die Differenzen ohne Aequivalenzbildung berechnen
            diff_text0         = text0.difference(set(sortierte_zeilen))
            
            equivalent_zeilen  = {}
            diff_sort_z_reduce = []
            diff_text0_reduce  = []
            
            vvv = re.compile(r"^(\d\d\d\d)(..)(\d\d) +(\S+) +(\S+) +(\S+) +(\-?\d+\.\d\d|\-+|\.+) +(.*?) *$")  #  zweiter Schritt:
            for zeile in diff_sort_z:          #  ueber Aequivalenzbeziehung weitere uebereinstimmende zeilen herausfinden
                m = vvv.search(zeile)
                if m:
                    zeile1 = m.group(1) + m.group(2) + m.group(3) + "  " + ("%3.2f"%eval(m.group(4))) + "  " + m.group(5) + "  " + m.group(6) + "  0.00  " + m.group(8)
                else:
                    continue      #  nur Buchungszeilen sind zu beruecksichtigen
                equivalent_zeilen[zeile1] = zeile
                diff_sort_z_reduce.append(zeile1)
            diff_sort_z_reduce = set(diff_sort_z_reduce)
            for zeile in diff_text0:
                m = vvv.search(zeile)
                if m:
                    zeile1 = m.group(1) + m.group(2) + m.group(3) + "  " + ("%3.2f"%eval(m.group(4))) + "  " + m.group(5) + "  " + m.group(6) + "  0.00  " + m.group(8)
                else:
                    continue      #  nur Buchungszeilen sind zu beruecksichtigen
                diff_text0_reduce.append(zeile1)
            diff_text0_reduce = set(diff_text0_reduce)
                
            diff_sort_z_reduce_diff = diff_sort_z_reduce.difference(diff_text0_reduce)
            diff_text0_reduce_diff  = diff_text0_reduce.difference(diff_sort_z_reduce)

#            print(diff_sort_z_reduce_diff)
#            print(diff_text0_reduce_diff)

            
            #  In diff_sort_z_reduce_diff stehen die reduzierten Zeilen aus der result.format, die geloescht werden muessen
            
            lines_to_delete = []
            for zeile1 in diff_sort_z_reduce_diff:
                zeile = equivalent_zeilen[zeile1]
                lines_to_delete.append(sortierte_zeilen.index(zeile)-2)
                del_lines.append("< " + zeile)

            #  Jetzt die neue result.orig schreiben:
            
#            print(lines_to_delete)

            result_orig = []
            zaehler     = 0
            del_datum   = {}
            for zeile in open(file+".orig").read().split("\n"):
                if zaehler in lines_to_delete:
#                    print("DEL",zeile)
                    del_datum[zeile[0:6]] = 1
                else:
                    result_orig.append(zeile)
                zaehler = zaehler + 1

            for zeile in diff_text0_reduce_diff:
                add_lines.append("> " + zeile)
                result_orig.insert(-1,zeile)
           
            result_orig = "\n".join(result_orig)
                                       
            dates_of_deleted_entries = []

            for ddatum in del_datum.keys():
                if re.search(r"^\d\d\d\d\d\d$",ddatum):
                    if "\n" + ddatum in result_orig:
                        continue
                    if result_orig.startswith(ddatum):
                        continue
                    dates_of_deleted_entries.append(ddatum)
        
            if len(del_lines) > 0 or len(add_lines) > 0:
                open(file+".orig","w").write(result_orig)
            else:
                os.unlink(file+".orig")
                os.unlink(file+".par")
                return()

#            print("-----------")
#            print(result_orig)
#            print("-----------")


#  ---  2. Jetzt zusammensetzen


        (startdate,enddate) = self.sort_transaction(file+".orig")
        if os.path.isfile(file+".par"):
            m = re.search(r"(\S*?),(\S*?),(\S*?)",open(file+".par").read())
            if m:                           #  In der result.par stehen die urspruenglichen Request-Daten.
                pattern   = m.group(1)      #  Diese Abfrage wiederholen, und die erhaltenen Buchungssaetze aus
                interval  = m.group(2)      #  den acc-Dateien ABZIEHEN
                egrep     = m.group(3)
                if interval == "None":
                    interval = None       
                self.split_subtract([startdate,enddate,pattern,interval,egrep],file)
        
        list_of_files = glob.glob("*.acc")
        list_of_files.sort()
        for ktofile in list_of_files:     #  hier die geaenderte result.orig auf die acc-Files richtig verteilen

            salden_file = re.sub(r"\.acc$",".sum",ktofile)
            abschnitt   = re.sub(r"\.acc$","",ktofile)

            m = re.search(r"^(\d+)\.acc",ktofile)
            if not m:
                continue

            zeitraum = m.group(1)
#            print(zeitraum,startdate,enddate)
            if os.path.isfile(salden_file):
                if zeitraum < startdate[0:len(zeitraum)]:
                    continue
                if zeitraum > enddate[0:len(zeitraum)]:
                    continue

            os.system("grep ^" + m.group(1) + " " + file + ".orig >> " + ktofile)
            if sortieren == 1:    #   hier die acc-Files wieder sortieren
                file_text = re.sub(r"\n+$","",open(ktofile).read()).split("\n")
                file_text.sort()
                open(ktofile,"w").write("\n".join(file_text) + "\n")
                self.mark("C. " + ktofile + " sorted.")
#                os.system("sort " + ktofile + " > " + "__" + ktofile)
#                os.system("mv __" + ktofile + " " + ktofile)
                

#       ------ 3.  Jetzt die Salden-Files nachziehen:

            diff_salden = {}
            is_buchung  = {}
            init_salden = ""
            salden_text = []
            if os.path.isfile(salden_file):    
                salden_text = open(salden_file).read().strip().split("\n")   #  update der salden_files
            else:
                init_salden = open(ktofile).read()

            update_salden = 0
            for diff_buchung in ( init_salden.split("\n") + add_lines + del_lines ):
                m = re.search("^([\<\>] +|)(\d\d\d\d\d\d\d\d) +(\S+) +(\S+) +(\S+) +(\-?\d+\.\d\d|\.+)",diff_buchung)
                if m:
                    if update_salden == 0:
                        update_salden = 1
                        self.mark("D. Update " + ktofile + ".")
                    datum  = m.group(2)
                    if datum.startswith(abschnitt):
                        betrag = eval(m.group(3))
                        ktoa   = m.group(4)
                        ktob   = m.group(5)
                        if m.group(1).startswith("<"):
                            betrag = -betrag
                        self.compute_salden(diff_salden,is_buchung,ktoa, betrag,datum) 
                        self.compute_salden(diff_salden,is_buchung,ktob,-betrag,datum)

            tt = 0
#            tt = 1

#            if tt == 1:
#                for kt in list(diff_salden.keys()):
#                    for monat in diff_salden[kt]:
#                        if "ger-LOHN-AN" in kt:
#                            print(kt,monat,diff_salden[kt][monat])

            salden_text.sort()
            salden_text1  = []
            del_element   = []
            update_salden = 0
            for kto in list(diff_salden.keys()):

#                if tt == 1:
#                    print(kto)
                if update_salden == 0:
                    update_salden = 1
                    self.mark("E. Diff salden computed.")
                    
                interval0 = 0   # suchen, ob es schon eine gueltige Zeile gibt
                interval1 = len(salden_text) - 1
                while (0 == 0):
                    if interval0 > interval1:
                        interval9 = -1
                        break
                    interval9 = interval0 + int((interval1 - interval0)/2)
#                    if tt == 1:
#                        print(interval0,interval9,interval1,kto)
#                    if tt == 1:
#                        print("    ",salden_text[interval9])
#                    print(kto)
                    if salden_text[interval9].startswith(kto+","):
                        break
                    if (kto + ",") > salden_text[interval9]:
                        interval0 = interval9 + 1
                    else:
                        interval1 = interval9 - 1
                                    
                if interval9 > -1:   #   wenn es schon eine Konto-Zeile im Salden-File gibt, diese integrieren
#                    if tt == 1:
#                        print(salden_text[interval9])
                    werte = salden_text[interval9].split(",")
#                    if tt == 1:
#                        print(werte)
                    werte.pop(0)
                    if len(werte) > 0:
                        monat   = int(werte.pop(0))
                        betrag0 = 0.00
                        nr0     = 0
                        for betrag in werte:
                            nr     = int(betrag[-self.max_months:])
                            betrag = float(betrag[:-self.max_months])
                            if not monat in diff_salden[kto]:
                                diff_salden[kto][monat] = 0.00
                                is_buchung[kto][monat]  = 0
                            diff_salden[kto][monat] = diff_salden[kto][monat] + betrag - betrag0
                            if monat in dates_of_deleted_entries:
                                is_buchung[kto][monat]  = 0
                            else:
                                is_buchung[kto][monat]  = 1
                            betrag0 = betrag
                            nr0     = nr
                            monat   = monat + 1
                            if str(monat)[4:6] == "13":
                                monat = int(str(int(str(monat)[0:4]) + 1) + "01")
                            
                monate   = list(diff_salden[kto].keys())
                monat    = min(monate)
                mmax     = max(monate)
                zeile    = kto + "," + str(monat) + ","
                betraege = []
                sum      = 0.00
                nr       = 0
                while (0 == 0):
                    if monat in diff_salden[kto]:
                        sum = sum + diff_salden[kto][monat]
                        nr  = nr  + is_buchung[kto][monat]
                    betraege.append(("%3.2f"%sum)+("%04u"%nr))
                    monat   = monat + 1
                    if str(monat)[4:6] == "13":
                        monat = int(str(int(str(monat)[0:4]) + 1) + "01")
                    if monat > mmax:
                        break
                while (0 == 0):
                    if len(betraege) < 2:
                        break
                    if not betraege[-1] == betraege[-2]:
                        break
                    betraege.pop()
                zeile = zeile + ",".join(betraege)
                if len(betraege) == 1 and float(betraege[0][:-self.max_months]) == 0.00:
                    if interval9 > -1:
                        salden_text[interval9] = "---DELETE---"   #  loesche die Zeile
                    else:
                        pass                                      #  Zeile ist Null, gar nicht erst eintragen
                else:
                    if interval9 > -1:
                        salden_text[interval9] = zeile   #  Zeile updaten
                    else:
                        salden_text1.append(zeile)       #  Zeile existierte nicht, also eintragen
                
            if update_salden == 1:
                self.mark("F. Salden list updated.")
     
#            while len(del_element) > 0:
#                salden_text.pop( del_element.pop() )

            salden_text = salden_text + salden_text1
            salden_text.sort()
            salden_text = "\n".join(salden_text) + "\n"
            salden_text = re.sub(r"---DELETE---\n","",salden_text,99999999)
            open(salden_file,"w").write(salden_text)   #  update der salden_files

        os.system("mv " + file + ".orig " + file + ".old")
        self.mark("G. ... closed.")

#**********************************************************************************

    def xxsort_transaction (self,file):

        os.system("sort " + file + " > " + "__" + file)
        os.system("mv __" + file + " " + file)
        startdate = os.popen("head -n 1 " + file).read()[0:8]
        enddate   = os.popen("tail -n 1 " + file).read()[0:8]
        if not re.search(r"^\d\d\d\d\d\d\d\d$",startdate):
            startdate = "00000000"
        if not re.search(r"^\d\d\d\d\d\d\d\d$",enddate):
            enddate = "99999999"

        return(startdate,enddate)
        
#**********************************************************************************

    def xxsplit (self,pattern="",file="result"):

        if os.path.isfile(file+".orig"):
            self.add()
            return()

        split_pars = self.split1(pattern,file)
        self.split_subtract(split_pars,file)

#**********************************************************************************

    def xxsplit1 (self,pattern="",file="result"):

        self.mark("")
        pattern1 = re.sub(r"\^"," ",pattern,9999)
        (pattern1,interval,egrep,interval0) = self.parse_pattern(pattern1)

        self.mark("A. Compute query for transaction file " + pattern1 + " " + str(interval)[0:40] + " ...")
        if interval:
            if pattern1 == "":
                os.system(egrep + "grep -h -i ^" + interval + " *.acc > " + file + ".orig")
            else:
                os.system(egrep + "grep -h -i ^" + interval + " *.acc | grep -h -i '" + pattern1 + "' > " + file + ".orig")
        else:
            if pattern1 == "":
                os.system("less *.acc > " + file + ".orig")
            else:
                os.system(egrep + "grep -h -i '" + pattern1 + "' *.acc > " + file + ".orig")
                

        (startdate,enddate) = self.sort_transaction(file + ".orig")


#        text0 = open(file+".orig").read().split("\n")   #   Doubletten-Vermeidung
#        if len(text0) > len(set(text0)):
#            print("Attention: Doublettes!")
#            text0.sort()
#            zeile0  = "-----"
#            text1   = []
#            zaehler = 0
#            for zeile in text0:
#                if len(zeile) == 0:
#                    continue
#                zeile1 = zeile.replace(" ","")
#                if zeile1 == zeile0:
#                    zaehler = zaehler + 1
#                    text1.append(zeile + " DOUBLETTE " + str(zaehler))
#                else:
#                    text1.append(zeile)
#                    zaehler = 0
#                    zeile0  = zeile1
#            open(file+".orig","w").write("\n".join(text1)+"\n")
        
        open(file+".par","w").write(pattern1+","+str(interval)+","+egrep+"\n")

        self.mark("B. Transaction file generated.")

        if len(glob.glob("*.acc")) == len(glob.glob("*.sum")):
            self.format_kto(pattern1,interval0,pattern)
            self.mark("C. ... and formatted.")
        
        return([startdate,enddate,pattern1,interval,egrep])

#**********************************************************************************
        
    def xxsplit_subtract (self,pars,file="result"): 

        startdate = pars[0]
        enddate   = pars[1]
        pattern   = pars[2]
        interval  = pars[3]
        egrep     = pars[4]

        pattern1  = re.sub(r"\^"," ",pattern,9999)


        list_of_files = glob.glob("*.acc")
        for ktofile in list_of_files:

            m = re.search(r"^(\d+)\.acc",ktofile)
            if not m:
                continue
            zeitraum = m.group(1)
            if zeitraum < startdate[0:len(zeitraum)]:
                continue
            if zeitraum > enddate[0:len(zeitraum)]:
                continue

            if interval:
                if pattern1 == "":
                    os.system(egrep + "grep -i -v ^" + interval + " " + ktofile + " > __" + ktofile)
                else:
                    os.system(egrep + "grep -i -v ^" + interval + " " + ktofile + " > __" + ktofile)
                    os.system(egrep + "grep -i ^" + interval + " " + ktofile + " | grep -i -v '" + pattern1 + "' >> __" + ktofile)
            else:
                if pattern1 == "":
                    os.system(" > __" + ktofile)
                else:
                    os.system(egrep + "grep -i -v '" + pattern1 + "' " + ktofile + " > __" + ktofile)
                    
            os.system("mv __" + ktofile + " " + ktofile)

        self.mark("D. Clear acc files.")
                
#**********************************************************************************

    def xxxxformat_kto (self,pattern,interval,pattern0,file="result"):

        if interval:
            interval = interval
        else:
            interval = ""

        try:
            text = open(file+".orig").read()
        except Exception as e:
            print(e)
            return()

        result = self.parse_ktotext(text.split("\n"),pattern)
        if not result:
            return(None)
                
        (ktotext,self.format_maxa,self.format_maxb,self.maxsaldo,ukto) = result
                
#        print("UKTO: " + ukto)
        if False and ukto == "":
            ktotext.sort(key=lambda x:x[0]+str(x[1])+x[3]+x[4])
        else:
#            ktotext.sort(key=lambda x:str(x[5]+1)+x[0])
            ktotext.sort(key=lambda x:x[0]+str(x[5]+1)+x[2]+x[3]+x[4])

        text_match1  = []
        text_match2  = []
        result_match = []
        gesamt       = 0.00
        datum        = "00000000"
        datum0       = "00000000"

        orig_text_new_sorted = []   #  das orig-File muss in der neuen Sortierung auch neu geschrieben werden,
                                    #  damit man am Ende den Patch auf das formatierte Konto-File anwenden kann.
        dbl_marks = {}

        has_doublettes = 0
        for zeile in ktotext:
                
            ust = ""
            if "v.H." in zeile[4]:
                ust = "   "

            ktoa   = zeile[2]
            ktob   = zeile[3]
            datum  = zeile[0]
            
            
#            print(ukto,zeile)
            betrag = float(zeile[1])
            if ukto == "" or zeile[5] == 0:
                saldo = "         ...."
#                saldo  = "%13.2f" % gesamt
            elif self.maxsaldo == 0 or zeile[5] == 1:
#                print("hier")
                gesamt = gesamt + betrag
                saldo  = "%13.2f" % gesamt
            elif zeile[5] == 2:
#                saldo = "         ----"
                saldo  = "%13.2f" % gesamt

            dbl_z    = datum + " " + ("%13.2f" % betrag) + "  " + (self.format_maxa % ktoa) + "  " + (self.format_maxb % ktob)
            rem_z    = ust + re.sub(r" +"," ",zeile[4],9999)
            zeile1   = dbl_z + " " + saldo + "  " + rem_z

            dbl_mark = dbl_z + rem_z   #  wenn Doubletten gefunden werden, diese eindeutig markieren
            if not dbl_mark in dbl_marks:
                dbl_marks[dbl_mark] = 0
            else:
                dbl_marks[dbl_mark] = dbl_marks[dbl_mark] + 1
                zeile1 = zeile1 + " DOUBLETTE " + str(dbl_marks[dbl_mark])
                has_doublettes = 1
            
#            print(zeile1)

            if True or zeile[5] == 1:
                text_match1.append(zeile1)
            else:
                text_match2.append(zeile1)
            if datum0 == "00000000":
                datum0 = datum

            orig_text_new_sorted.append(zeile[6])

#        text_match1  = "" + ("%-50s"%(pattern0)) + ("%13.2f"%gesamt) + "\n\n" + "\n".join(text_match1) + "\n"
        text_match1  = "" + ("%-50s"%(re.sub(r"\.$","",ukto+interval))) + ("%13.2f"%gesamt) + "\n\n" + "\n".join(text_match1) + "\n"
        text_match2  = "\n".join(text_match2) + "\n"
        
        salden_text = self.format_salden(ukto,datum,datum0,"^"+ukto+"(-[^- ]+){0,99},")
        text_match1 = text_match1 + "\n" + re.sub(ukto+"(-| )","","\n".join(salden_text),99999999) + "\n\n" + text_match2
            
        open(file+".format","w").write(text_match1)
        open(file+".kto","w").write(text_match1)
        open(file+".orig","w").write("\n".join(orig_text_new_sorted)+"\n")
        
        if has_doublettes:
            print("Attention: Doublettes!")

#        exit()


    def xxxxapply_patch (self,file,patch,offset=0):  #  verbessern! Kann der patch Befehl auch direkt auf result.txt angewendet werden?

        text0     = open(file).read()
        text0     = re.sub("\n","--CR--\n",text0,99999999)
        text      = text0.split("\n")

        del_datum = {}
        nr        = -1
        bed       = False

        for zeile in open(patch).read().split("\n"):
            if len(zeile) == 0:
                continue
            if zeile[0] == ">" and nr < len(text):                #  Zeile einzufuegen
                if len(zeile) > 9 and not " " in zeile[2:10]:     #  das ist tatsaechlich eine Buchungszeile,
                    bed = True                                    #  denn sie faengt mit einem Datum an        
                text[nr] = text[nr] + zeile[2:] + "--CR--"
            elif zeile[0] == "<":                                 #  Zeile zu loeschen
                if len(zeile) > 9 and not " " in zeile[2:10]:     #  das ist tatsaechlich eine Buchungszeile,
                    bed = True                                    #  denn sie faengt mit einem Datum an
                del_datum[zeile[2:8]] = 1                         #  vormerken, dass in diesem Monat eine Buchung geloescht wurde
                continue
            else:
                m = re.search(r"^(\d+)(,\d+|)([acd])",zeile)  #  eine Zeile, in der eine Update-Information steht,
                if m:                                         #  (diese Info wirkt sich dann aus auf die naechsten Zeilen)
#                    print(zeile)
                    act = m.group(3)
                    nr1 = int(m.group(1)) - 1 - offset
                    nr2 = nr1
                    if len(m.group(2)) > 0:
                        nr2 = int(m.group(2)[1:]) - 1 - offset
                    if act in "ac":
                        nr = max(0,min(nr1,len(text)-1))
                    if act in "dc":   #  Zeilen entfernen
                        while (nr1 < len(text)):
#                            print("ZZZ",zeile,nr1)
#                            print("DDD",text[nr1],nr1)
                            text[nr1] = ""
                            nr1 = nr1 + 1
                            if nr1 > nr2:
                                break

        text = "".join(text)
        text = re.sub(r"--CR--","\n",text,99999999)
        text = re.sub(r"\n$","",text,re.DOTALL)

        if not bed:
            return(None)

        dates_of_deleted_entries = []
        for ddatum in del_datum.keys():
            if re.search(r"^\d\d\d\d\d\d$",ddatum):
                if "\n" + ddatum in text:
                    continue
                if text.startswith(ddatum):
                    continue
                dates_of_deleted_entries.append(ddatum)
        
        open(file,"w").write(text)

        return(dates_of_deleted_entries)   #  die Monate, in denen jetzt gar keine Buchungen mehr sind, werden zurueckgegeben
        
#****************************************************************************************************************

    def xxkto (self,pattern=""):

        ktodir = os.path.abspath(".")

        if pattern == "SORT":     #   Sortieren aller acc und sum files. Dies ist sinnvoll fuer das syncen
        
            for acc_file in glob.glob("*.acc") + glob.glob("*.sum"):
                file_text = re.sub(r"\n+$","",open(acc_file).read()).split("\n")
                file_text.sort()
                open(acc_file,"w").write("\n".join(file_text) + "\n")
                return()

        ktofile = []
        for kfile in glob.glob("*.kto"):
            if not ".db." in kfile and "result.kto" not in kfile:
                ktofile.append(kfile)
        
        if len(ktofile) > 1:
            print("More than one ktofile.")
            return()

        if len(ktofile) == 1:
            ktofile = ktofile[0]
        else:
            ktofile = None

        if ktofile:
            ktodir   = re.sub(r"^(.*)[\\\/](.*).kto$","\\1",os.path.abspath(ktofile))
            ktotext  = open(ktodir+"/"+ktofile).read()
            pattern0 = "^" + re.sub(r"^(\S*) (.*)$","\\1",ktotext[0:50])
        else:
            ktotext  = ""
            ktodir   = re.sub(r"[\\\/]$","",os.path.abspath("."))


        while (0 == 0):   #  check if we are in a directory with acc files
            x = glob.glob("2*.acc") + glob.glob("base/*.acc") + glob.glob(".base/*.acc")
            if len(x) > 0:
                y = glob.glob("2*.sum") + glob.glob("base/*.sum") + glob.glob(".base/*.sum")
                m = re.search(r"^(.*)[\\\/](.*)$",x[0])
                if m:
                    os.chdir(m.group(1))
                break
            os.chdir("..")
            
#        os.system("ls")

        if os.path.isfile("result.orig"):
            hkey = os.popen("md5sum result.kto").read()[0:12]
            if hkey + ".kto" == ktofile or hkey in ktotext[0:200]:
                open("result.kto","w").write(ktotext)
                    
        udir = None
        if ktofile:
            udir = ktodir
            if pattern == "":
                pattern = pattern0   #  wenn kein pattern angegeben, nimm das pattern aus dem ktofile
            else:
                m = re.search(r"^(.*)([\.\:])(.*)",pattern0)
                if m:
                    p0 = m.group(1)
                    m0 = m.group(2)
                    i0 = m.group(3)
                else:
                    p0 = pattern0
                    m0 = None
                    i0 = None
                m = re.search(r"^(.*)([\.\:])(.*)",pattern)
                if m:
                    p1 = m.group(1)
                    m1 = m.group(2)
                    i1 = m.group(3)
                else:
                    p1 = pattern
                    m1 = None
                    i1 = None
                if not i1:
                    i1 = i0
                if not i1:
                    i1 = ""
                if p1 in p0:
                    p1 = ""
                p2 = re.sub(r"-$","",p0 + "-" + p1)
                if p0 == "" or not p2[1:] in ktotext:
                    p2 = p1
                if len(p0) > 0 and p2.startswith(p0):
                    udir = ktodir + "/" + p1
#                    p2   = "^" + p2
                    print("UDIR",udir)
                    try:
                        os.mkdir(udir)
                    except:
                        pass

                if m0 == m1:
                    if not m1:
                        m1 = ""
                    pattern = p2 + m1 + i1
                pattern = re.sub(r"\.$","",pattern)

        print("PATTERN",pattern)

        if os.path.isfile("result.orig"):
            if pattern == "":
                self.add(1)
            else:
                self.add()
            if os.path.isfile("result.kto"):
                os.unlink("result.kto")
                
        if pattern == "":
            os.chdir(ktodir)
            return()
            

        split_pars = self.split1(pattern)

        if os.path.isfile(ktodir+"/result.orig"):
            os.chdir(ktodir)
            return()

        if os.path.isfile("result.orig"):
            
            if udir:
                for kfile in glob.glob(udir+"/*.kto"):
                    os.unlink(kfile)
            else:
                udir = ktodir

            hkey = os.popen("md5sum result.kto").read()[0:12]
            
            ktotext = open("result.kto").read()
            ktotext = re.sub(r"^(\S+  )( +\S+)","\\1 " + hkey + "\\2",ktotext)
            if ktofile == None or re.search(r"^[abcdef0123456789]{12}\.kto$",ktofile):
                open(udir+"/"+hkey+".kto","w").write(ktotext)
            else:
                open(udir+"/"+ktofile,"w").write(ktotext)

        os.chdir(ktodir)


#
            
            
#**********************************************************************************

if __name__ == "__main__":
        
#    Konto.__dict__[sys.argv[1]](Konto(),*sys.argv[2:])

    if len(sys.argv) > 1 and sys.argv[1].startswith("test"):
        Konto.__dict__[sys.argv[1]](Konto(),*sys.argv[2:])
    elif len(sys.argv) > 1 and sys.argv[1] == "sort":
        Konto.__dict__["sort"](Konto(),*sys.argv[2:])
    elif len(sys.argv) > 1 and sys.argv[1] == "saldo":
        print(Konto.__dict__["read_saldo"](Konto(),*sys.argv[2:]))
    else:
        Konto.__dict__["kto"](Konto(),*sys.argv[1:])
