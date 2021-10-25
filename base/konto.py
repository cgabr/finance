#  coding:  utf
import os,sys,re,glob,time,base64,hashlib,random,functools

#******************************************************************************

class Konto ():


#******************************************************************************

    def __init__ (self):


        self.t0         = 0
        self.max_months = 4   #  10^max_months Monate erlaubt in einem sum-file, 10^4/12 = 800 Jahre
                              #      (das sollte reichen)

#**********************************************************************************

    def mark (self,remark=""):
        
        t = time.perf_counter()
        if self.t0 > 0:
            print ( ("%9.2f" % ((t-self.t0)*1000)) + " ms for:  " + remark )
        self.t0 = t

#**********************************************************************************

    def add (self,sortieren=0,file="result"):

#       Diese Funktion teilt die Buchungssaetze in einer Transaktionsdatei auf die
#       einzelnen Teildateien auf

        if not os.path.isfile(file+".orig"):
            print("No result file.")
            return()

        self.mark("A. Close transaction.")

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
            print(zeitraum,startdate,enddate)
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

    def compute_salden (self,salden,buchung,ukto,betrag,datum):

        monat = int(datum[0:6])
        while (0 == 0):
            if not ukto in salden:
                salden[ukto]  = {}
                buchung[ukto] = {}
            if not monat in salden[ukto]:
                salden[ukto][monat]  = 0.00
            salden[ukto][monat]  = salden[ukto][monat] + betrag
            buchung[ukto][monat] = 1
            m = re.search(r"^(.*)\-(.+)$",ukto)
            if m:
                ukto = m.group(1)
            else:
                return()

#**********************************************************************************

    def sort_transaction (self,file):

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

    def split (self,pattern="",file="result"):

        if os.path.isfile(file+".orig"):
            self.add()
            return()

        split_pars = self.split1(pattern,file)
        self.split_subtract(split_pars,file)

#**********************************************************************************

    def split1 (self,pattern="",file="result"):

        self.mark("")
        pattern1 = re.sub(r"\^"," ",pattern,9999)
        (pattern1,interval,egrep) = self.parse_pattern(pattern1)

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
        
        open(file+".par","w").write(pattern+","+str(interval)+","+egrep+"\n")

        self.mark("B. Transaction file generated.")

        if len(glob.glob("*.acc")) == len(glob.glob("*.sum")):
            self.format_kto(pattern1,interval,pattern)
            self.mark("C. ... and formatted.")
        
        return([startdate,enddate,pattern1,interval,egrep])

#**********************************************************************************
        
    def split_subtract (self,pars,file="result"): 

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

    def parse_pattern (self,pattern=""):    #   parse the pattern

        interval = None
        egrep    = ""
        m        = re.search(r"^(.*)([\.\:])(.*)$",pattern)
            
        if m:

            pattern       = m.group(1)
            mode          = m.group(2)
            interval      = "20" + m.group(3)[0:2]
            months        = m.group(3)[2:]
            
            if   months == "A":
                months = "10"
            elif months == "B":
                months = "11"
            elif months == "C":
                months = "12"
            elif months == "I":
                months = "0[123]"
            elif months == "J":
                months = "0[456]"
            elif months == "K":
                months = "0[789]"
            elif months == "L":
                months = "1[012]"
            elif months == "M":
                months = "0[123456]"
            elif months == "N":
                months = "\\(07\\|08\\|09\\|10\\|11\\|12\\)" # "[01][789012]"
                egrep  = "e"
            elif months == "P":
                months = ""
            elif not months == "":
                months = "0" + months
        
            if mode == ":":
                intervals = []
                jahr      = "2000"
                while (0 == 0):
                    intervals.append(jahr)
                    jahr = str(int(jahr)+1)
                    if jahr == interval:
                        break
                month = "01"
                while (0 == 0):
                    intervals.append(jahr+month)
                    if month in (months,"12"):
                        break
                    month = "%02u" % (int(month) + 1)
                interval = "\\(" + "\\|".join(intervals) + "\\)"
                egrep    = "e"
            else:
                interval = interval + months

        return(pattern,interval,egrep)            
                
#**********************************************************************************

    def format_kto (self,pattern,interval,pattern0,file="result"):

        if interval:
            interval = "." + interval
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
                
        (ktotext,format_maxa,format_maxb,maxsaldo,ukto) = result
                
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
            elif maxsaldo == 0 or zeile[5] == 1:
#                print("hier")
                gesamt = gesamt + betrag
                saldo  = "%13.2f" % gesamt
            elif zeile[5] == 2:
#                saldo = "         ----"
                saldo  = "%13.2f" % gesamt

            dbl_z    = datum + " " + ("%13.2f" % betrag) + "  " + (format_maxa % ktoa) + "  " + (format_maxb % ktob)
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

        text_match1  = "" + ("%-50s"%(re.sub(r"\.$","",ukto+"."+interval))) + ("%13.2f"%gesamt) + "\n\n" + "\n".join(text_match1) + "\n"
        text_match2  = "\n".join(text_match2) + "\n"
        
        salden_text = self.format_salden(ukto,datum,datum0,"^"+ukto+"(-[^- ]+){0,99},")
        text_match1 = text_match1 + "\n" + re.sub(ukto+"(-| )","","\n".join(salden_text),99999999) + "\n\n" + text_match2
            
        open(file+".format","w").write(text_match1)
        open(file+".kto","w").write(text_match1)
        open(file+".orig","w").write("\n".join(orig_text_new_sorted)+"\n")
        
        if has_doublettes:
            print("Attention: Doublettes!")

#        exit()

#**********************************************************************************

    def parse_ktotext (self,ktotext,pattern):

        buchungen      = []
        unique_strings = {}
        pattern        = pattern.strip().upper()
        if len(pattern) > 0 and pattern[-1] == "-":
            pattern = pattern[:-1]
        maxa           = 10
        maxb           = 10
        maxc           = 0
        maxd           = 0
        maxsaldo       = 0

        ukto  = ""
        ukto0 = ""
        if pattern == "":
            ukto = None
            
        zaehler = -1
        vvv = re.compile(r"^(\d\d\d\d)(..)(\d\d) +(\S+) +(\S+) +(\S+) +(\-?\d+\.\d\d|\-+|\.+) +(.*?) *$")
        for zeile in ktotext:

            mm = vvv.search(zeile)
            if not mm:   #   Einlesen der Kontobezeichnungen
#                    buchungen.append(["00000000",zeile,"","","",-1])
                continue

            if mm.group(2) == "MM":
                monate = ["01","02","03","04","05","06","07","08","09","10","11","12"]
            else:
                monate = [mm.group(2)]

            for monat in monate:

                datum  = mm.group(1) + monat + mm.group(3)
                try:
                    betrag = "%3.2f" % eval(mm.group(4))
                except:
                    print(mm.group(4))
                    exit()

                remark = mm.group(8)
                uniqu  = []
                ktoa   = "^" + mm.group(5)
                ktob   = "^" + mm.group(6)

#                    ktoa = self.parse_ktotext_compute_kto(m.group(5),self.ukto,uniqu)
#                    ktob = self.parse_ktotext_compute_kto(m.group(6),self.ukto,uniqu)

                if ktoa > ktob:
                    o      = ktoa    #  um Eindeutigkeit zu schaffen. Sonst kann es durch
                    ktoa   = ktob    #  Hin- und Herschwingen zu Endlos-Loops kommen
                    ktob   = o
                    betrag = re.sub(r"^--","","-"+betrag)

                if not ktoa[1] == "-" and not ktoa.upper().startswith(pattern) and pattern in ktob.upper():
                    o      = ktoa    #  um das gefundene Konto an den Anfang zu stellen
                    ktoa   = ktob
                    ktob   = o
                    betrag = re.sub(r"^--","","-"+betrag)

                saldo = 0
                if not ukto == None:
                    
                    if ukto == "":
                        if pattern in ktoa.upper() and not ktoa[1] == "-":
                            ukto = ktoa
                    for kto in (ktoa,ktob):
                        if pattern in kto.upper() and not kto[1] == "-":
                            while (0 == 0):
                                if kto.startswith(ukto):
                                    break
                                m = re.search(r"^(.*)\-(.*)$",ukto)
                                if m:
                                    ukto = m.group(1)
                                else:
                                    ukto = ""
                                print("           fit ukto: " + ukto.replace("^",""))
                            if not pattern in ukto.upper():
                                ukto = None
                                print("No ukto found.")
                                salden = None
                            break

                if ukto:
                    while (0 == 0):
                        m = re.search(r"^(.*)\-(.*)$",ukto)
                        if not m or not pattern in m.group(1).upper():
                            break
                        ukto  = m.group(1)
                        ukto0 = re.sub(r"\^","",ukto)
                

                if ukto or ktoa[1] == "-":
                    saldo = ( int( ukto and ktoa.startswith(ukto) or ktoa[1] == "-") +
                              int( ukto and ktob.startswith(ukto) or ktob[1] == "-") )
                    
                if uniqu == []:
                    uniqu = [ktoa,ktob]

                maxsaldo = max(maxsaldo,saldo)
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
                    maxc = max(maxc,len(ktoa))
                else:
                    maxa = max(maxa,len(ktoa))

                if ktob[0] == "-":
                    maxd = max(maxd,len(ktob))
                else:
                    maxb = max(maxb,len(ktob))

                buchungen.append([datum,betrag,ktoa,ktob,remark,saldo,zeile])

        if ukto == None:
            ukto = ""
        ukto = ukto.replace("^","")

        if maxc > 0:
            maxa = max(maxa,len(ukto)+maxc)
        if maxd > 0:
            maxb = max(maxb,len(ukto)+maxd)

        format_maxa = "%-" + str(maxa) + "s"
        format_maxb = "%-" + str(maxb) + "s"

        return(buchungen,format_maxa,format_maxb,str(maxsaldo),ukto)

#*************************************************************************

    def xxapply_patch (self,file,patch,offset=0):  #  verbessern! Kann der patch Befehl auch direkt auf result.txt angewendet werden?

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
        

#**********************************************************************************

    def format_salden (self,kto0,datum,start_datum="00000000",ktoparse="^[^- ]+-[^- ]+ "):

        faktor = 1
        kto    = kto0
        if kto0 and kto0[0] == "-":
            faktor = -1
            kto    = kto0[1:]

        if int(start_datum) == 0:
            start_datum = datum
        if int(start_datum) == 1:
            start_datum = "00000000"
            
#        print(kto,datum,start_datum,ktoparse)

        datum       = (datum      +"99999999")[0:6]
        start_datum = (start_datum+"00000000")[0:6]
        
        if datum[4:6] > "12":
            datum = datum[0:4] + "12" 

        ktofiles1 = glob.glob("*.sum")
        ktofiles1.sort()
        ktofiles  = []

        for ktofile in ktofiles1:
            m = re.search(r"(.*)\.sum$",ktofile)
            if len(ktofiles) < 2:
                if (m.group(1) + "000000")[0:6] < start_datum:
                    ktofiles = []
            if (m.group(1) + "000000")[0:6] > datum:
                break
            else:
                ktofiles.append(ktofile)

#        print(ktofiles)
        ktotexts = []
        for ktofile in ktofiles:  #  alle relevanten Zeilen in den Salden-Files werden per grep gefunden:
            ktotexts.append([])
#            print("grep -P '" + ktoparse + "' " + ktofile)
            for zeile in os.popen("grep -P '" + ktoparse + "' " + ktofile).read().split("\n")[:-1]:
#                print(zeile)
                ktotexts[-1].append(zeile.split(","))

        salden_aktuell = []
        
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

#            if kto[0:2] == "13":
#                print("KTO",kto)
            if len(ktotexts[0]) > 0 and kto == ktotexts[0][0][0]:   #  im ersten Salden-File die genaue Monatsspalte finden
                zeile  = ktotexts[0][0][1:]  #  nicht entfernen!
                datum0 = zeile.pop(0)
                if start_datum >= datum0:
                    datpos = 12*( int(start_datum[0:4]) - int(datum0[0:4]) ) + int(start_datum[4:6]) - int(datum0[4:6]) - 1
                    if datpos < 0:
                        betrag = 0.00
                        nr     = 0
                    elif datpos >= len(zeile):
                        betrag = betrag - float(zeile[-1][:-self.max_months])
                        nr     = nr     - int(zeile[-1][-self.max_months:])
                    else:
                        betrag = betrag - float(zeile[datpos][:-self.max_months])
                        nr     = nr     - int(zeile[datpos][-self.max_months:])
#                    if kto == "13":
#                        print("DATPOS1",zeile[datpos],datum,datpos,kto,betrag,nr)
#                        print(zeile)
                
            if len(ktotexts[-1]) > 0 and kto == ktotexts[-1][0][0]:   #  im letzten Salden-File die genaue Monatsspalte finden
#                zeile  = ktotexts[-1][0][1:]  #  nicht entfernen!
                zeile  = ktotexts[-1].pop(0)[1:]
                datum0 = zeile.pop(0)
#                print(datum,datum0)
                if datum >= datum0:
                    datpos = 12*( int(datum[0:4]) - int(datum0[0:4]) ) + int(datum[4:6]) - int(datum0[4:6])
                    if datpos >= len(zeile):
                        betrag = betrag + float(zeile[-1][:-self.max_months])
                        nr     = nr     + int(zeile[-1][-self.max_months:])
                    else:
                        betrag = betrag + float(zeile[datpos][:-self.max_months])
                        nr     = nr     + int(zeile[datpos][-self.max_months:])

#                    if kto == "13":
#                        print("DATPOS2",zeile[datpos],start_datum,datpos,kto,betrag,nr)

                
            for ktotext in ktotexts[:-1]:   #  nur bei sum-up Werten relevant
                if len(ktotext) > 0 and ktotext[0][0] == kto:
                    zeile  = ktotext.pop(0)
                    betrag = betrag + float(zeile[-1][:-self.max_months])
                    nr     = nr     + int(zeile[-1][-self.max_months:])

            if nr > 0:
                kto_ordnung = max(0,len(re.sub("[^\-]","",kto)))
                kto_ordnung = "%-" + ("%2u"%(20+kto_ordnung*4)) + "s"
                salden_aktuell.append( (kto_ordnung % kto) + "  " + ("%13.2f" % (faktor*betrag) ) )

        return(salden_aktuell)

#**********************************************************************************

    def kto (self,pattern=""):

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
            pattern0 = re.sub(r"^(\S*) (.*)$","\\1",ktotext[0:50])
        else:
            ktodir   = re.sub(r"[\\\/]$","",os.path.abspath("."))

        while (0 == 0):
            x = glob.glob("2*.acc")
            if len(x) > 0:
                y = glob.glob("2*.sum")
                break
            os.chdir("..")
            
            
#        os.system("ls")

        if os.path.isfile("result.orig"):
            hkey = os.popen("md5sum result.kto").read()[0:12]
            if hkey + ".kto" == ktofile:
                open("result.kto","w").write(ktotext)
                    
        udir = None
        if ktofile:
#            print("P0 P1",pattern0,pattern)
            udir = ktodir
            if pattern == "":
                pattern = pattern0
            else:
                m = re.search(r"^(.*)\.(.*)",pattern0)
                if m:
                    p0 = m.group(1)
                    i0 = m.group(2)
                else:
                    p0 = pattern0
                    i0 = None
                m = re.search(r"^(.*)\.(.*)",pattern)
                if m:
                    p1 = m.group(1)
                    i1 = m.group(2)
                else:
                    p1 = pattern
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

                pattern = p2 + "." + i1
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
            open(udir+"/"+hkey+".kto","w").write(ktotext)

        os.chdir(ktodir)

            
            
#**********************************************************************************

if __name__ == "__main__":
        
    Konto.__dict__[sys.argv[1]](Konto(),*sys.argv[2:])
