#  coding:  utf8

import os,sys,re,glob,time

try:
    from konto_custom import config
except:
    from konto.base import config


#*********************************************************************************

class Meldung (object):

    def __init__ (self,dir="."):
        self.dir     = dir
        self.ktoa    = config.KTO_KRANKENKASSEN     
        self.ktob    = config.KTO_BEITRAGSNACHWEISE 
        self.kkmap   = re.sub(r"\s","",config.MAP_KRANKENKASSEN,99999999).split(",")

    
#*********************************************************************************

    def mark (self,remark=""):

        t = time.perf_counter()
        if 't0' in vars(self):
            print ( ("%9.2f" % ((t-self.t0)*1000)) + " ms for:  " + remark )
        self.t0 = t

#********************************************************************************

    def parse_sv_meldungen (self,*pars):

        kkdatum            = {}
        self.betriebsnr_kk = {}
        
        sv_meldungen = glob.glob(self.dir+"/*.pdf")
        sv_meldungen.sort()
        
        dir = os.path.abspath(".")
#        print(dir)
        m = re.search(r"^(.*)[\\\/]([a-z]+)([\\\/]|$)",dir)
        if m:
            person = m.group(2)

#   Sozialversicherungsmeldungen

        for sv_meldung in sv_meldungen:
        
            if "_orig." in sv_meldung:
                continue

            m = re.search(r"_MODE(\d+)_",sv_meldung)
            mode = 0
            if m:
                mode = int(m.group(1))
            
            text = ""
            if "pdf" in sv_meldung.lower():
                os.system("pdftotext -layout " + sv_meldung + " __xx.txt")
                text = open("__xx.txt").read()
            
            if len(text) < 10:
                continue

            text = self.normalize_text(text)

            m = re.search('Einzugsstelle.*Betriebsnummer +(\d+)(.*?)Name +([^\n ]+)', text, re.DOTALL)
            if not m:
                continue

            kknr   = m.group(1)
            remark = m.group(3) + ' ' + m.group(1)
            remark = re.sub('[\\n-]/', ' ', remark, 9999, re.DOTALL)
            remark = re.sub('^(.*?) +(.*?) .*? (\d+)$', '\\1 \\2 \\3', remark)

            ind    = self.kkmap.index(kknr)
            kkid   = self.kkmap[ind+1]
            kkname = self.kkmap[ind+2]

            m = re.search('TAN +(\d\d\d\d\d\d\d\d\d)\D', text)
            if not m:
                continue
            tan = m.group(1)
 
            m = re.search('Betriebsnummer +(\d\d\d\d\d\d\d\d)\D', text)
            if not m:
                continue
            betriebsnummer = m.group(1)
 

            m = re.search('Sendedatum\\:? +(\d\d)\.(\d\d)\.(\d\d)(\d\d)\D', text)
            if not m:
                continue
            sendedatum =  m.group(4) + m.group(2) + m.group(1)


            m = re.search('Grund +der +Abgabe. *(.*)', text)
            if not m:
                continue
            grund = m.group(1)

            if re.search('Storn.*Ja', text):
                storniert = "_storniert"
            else:
                storniert = ""

            print(sv_meldung)

            text = re.sub('(.*) +ohne +Sozialausgleich(.*)', '', text, 9999)  # wegen doppelt eingetragener Betraege

            m = re.search('gung +von +(\d+)\.(\d+)\.(\d+)', text, re.DOTALL)
            if not m:
                continue
            meldejahr = m.group(3)

            newname = meldejahr + '.' + grund + "_" + sendedatum + "_" + tan + "_" + kkid + "_" + kkname + '_' + person + storniert 
            newname = self.normalize_text(newname)
            newname = re.sub(r"[ \(\)\=]","_",newname,99999999) 
            newname = re.sub(r"__","_",newname,99999999) 
            newname = re.sub(r"__","_",newname,99999999) 
            newname = re.sub(r"__","_",newname,99999999) 
#            print(newname)

            m = re.search('^(.*)\.(.*?)$',sv_meldung)  #  renaming the original files
            filename = m.group(1)
            if not filename[2:] == newname and not filename == newname:
                print(sv_meldung, newname + '.' + m.group(2))
                os.rename(sv_meldung, newname + '.' + m.group(2))

        #   Lohnsteuermeldungen

        for sv_meldung in sv_meldungen:
        
            if "_orig." in sv_meldung:
                continue

            text = ""
            if "pdf" in sv_meldung.lower():
                os.system("pdftotext -layout " + sv_meldung + " __xx.txt")
                text = open("__xx.txt").read()
            
            if len(text) < 10:
                continue

            text = self.normalize_text(text)

            m = re.search('Lohnsteuerbesch(.*?)f(.*?) +(\d\d\d\d)', text, re.DOTALL)
            if not m:
                continue
            meldejahr = m.group(3)

            m = re.search('Transferticket(.*?)(\d+) +(\d\d)\.(\d\d)\.(\d\d)(\d\d)', text, re.DOTALL)
            if not m:
                m = re.search('Transferticket(.*?) +([a-z0-9]+)', text, re.DOTALL)
                if not m:
                    continue
                tan = m.group(2)
                m = re.search('Datum(.*?) +(\d\d)\.(\d\d)\.(\d\d)(\d\d)', text, re.DOTALL)
                if not m:
                    continue
                sendedatum = m.group(5) + m.group(3) + m.group(2)
            else:
                tan        = m.group(2)
                sendedatum = m.group(6) + m.group(4) + m.group(3)

            print(sv_meldung)
#            print("T",tan)
#            print("S",sendedatum)
 
 
            m = re.search('Steuernummer(.*?)\D(\d\d\d\D\d\d\d\D\d\d\d\d\d)\D', text,re.DOTALL)
            if not m:
                continue
            steuernummer = self.normalize_text(m.group(2),"1")
 
            m = re.search('(Name|Anschrift) (.*?)\n(\S.+?)(\n|   )', text,re.DOTALL)
            if not m:
                continue
            company = self.normalize_text(m.group(3),"1")
            grund = "01_Lohnsteuerjahresbescheinigung"

            if re.search('Storn.*Ja', text):
                storniert = "_storniert"
            else:
                storniert = ""


            newname = meldejahr + '.' + grund + "_" + person + "__" + company + "__" + steuernummer + "__" + sendedatum + "__" + tan + storniert 
#            print(newname)
            newname = self.normalize_text(newname)
#            newname = re.sub(r"[ \(\)\=]","_",newname,99999999) 
#            newname = re.sub(r"__","_",newname,99999999) 
#            newname = re.sub(r"__","_",newname,99999999) 
#            newname = re.sub(r"__","_",newname,99999999) 
#            print(newname)

            m = re.search('^(.*)\.(.*?)$',sv_meldung)  #  renaming the original files
            filename = m.group(1)
            if not filename[2:] == newname and not filename == newname:
                print(sv_meldung, newname + '.' + m.group(2))
                os.rename(sv_meldung, newname + '.' + m.group(2))

        os.unlink("__xx.txt")



#************************************************************************************************************

    def normalize_text (self,text,extended=""):
    
        text = re.sub(r"ä",   "ae",text,99999999)
        text = re.sub(r"ö",   "oe",text,99999999)
        text = re.sub(r"ü",   "ue",text,99999999)
        text = re.sub(r"Ä",   "Ae",text,99999999)
        text = re.sub(r"Ö",   "Oe",text,99999999)
        text = re.sub(r"Ü",   "Ue",text,99999999)
        text = re.sub(r"ß",   "ss",text,99999999)
        text = re.sub(r"a\"", "ae",text,99999999)
        text = re.sub(r"o\"", "oe",text,99999999)
        text = re.sub(r"u\"", "ue",text,99999999)
        text = re.sub(r"A\"", "Ae",text,99999999)
        text = re.sub(r"O\"", "Oe",text,99999999)
        text = re.sub(r"U\"", "Ue",text,99999999)
        text = re.sub(r"s\"", "ss",text,99999999)
        text = re.sub(r"&",   "u", text,99999999)
        text = re.sub(r"\t",  "  ",text,99999999)
        text = re.sub(chr(13),"",  text,99999999)
        
        if not extended == "":
            text = re.sub(r"[\+\-\. \;\:\,\(\)\[\]\\\/]","_",  text,99999999)
            text = re.sub(r" ",   "_", text,99999999)

        return(text)

#************************************************************************************************************


    def xxxx ():



        for zeile in ktotext.split('\n'):
#            if not re.search('^\d\d\d\d\d\d\d\d +\-?\d+\.\d\d.* (.*?-\d\d\d\d|)-meldung', zeile):
            if not re.search('^\d\d\d\d\d\d\d\d +\-?\d+\.\d\d.*-meld(ung|ZUS).*-meld(ung|ZUS)', zeile):
                text.append(zeile)
                continue

        ktotext = '\n'.join(text) + '\n'
        files.sort()
        for file in files:

                buchungen = []
                text = open(file).read()

                jahr    = m.group(3)
                monat   = m.group(2)
                newname = newname + '_' + (kk + '______')[0:6] + '__' + jahr + '_' + monat
                newname = re.sub('KNAPPS', 'MINIJO', newname)
                text = re.sub('(\d)\.(\d+\,\d\d)', '\\1\\2', text, 9999)
                m = re.search('Einzugsstelle.*Betriebsnummer +(\d+)(.*?)Name +([^\n ]+)', text, re.DOTALL)
                if not m:
                    continue
                self.betriebsnr_kk[kknr] = m.group(1)
                remark = m.group(3) + ' ' + m.group(1)
                remark = re.sub('[\\n-]/', ' ', remark, 9999, re.DOTALL)
                remark = re.sub('^(.*?) +(.*?) .*? (\d+)$', '\\1 \\2 \\3', remark)
                buchungen1 = []
                o = kknr + ',' + jahr + monat
                if o in kkdatum:
                    kkdatum[o] = kkdatum[o] + 1
                else:
                    kkdatum[o] = 20
                datum = jahr + monat + '%02u' % kkdatum[o]
                new_addtext = False
                stornofaktor = 1.0
                remarkadd    = ""
                if "Storno " in text:
                    stornofaktor = -1.0
                    remarkadd    = "manuell storniert - "
                if re.search(r"Stornierung +(JA|Ja|ja)",text):
                    stornofaktor = st
                    print("STS",jahr+monat,st)
                    remarkadd    = "Stornierung - "

                while (0 == 0):
                    m = re.search('^(.*\n)(.*?Pausch\S*|Storno|Beitrae?\"?ge? [a-z]\S*|Zusatzb\S*|Umlage\S*) ([^\n]*?) *(\-?\d+)\,(\d\d)', text, re.IGNORECASE + re.DOTALL)
                    if not m:
                        break
                    text = m.group(1)
                    remark1 = remark + ', ' + m.group(2) + ' ' + m.group(3)
                    remark1 = re.sub('\n', ' ', remark1, 9999, re.DOTALL)
                    ktoa = None
                    ktob = '10-1510-' + kknr + '-meldung-' + datum[6:8]
                    if 'Storno' in remark1:
                        continue
                    elif re.search(', Beitr.*Krankenvers.*ohne|, Beitr.*Krankenvers.*geringf', remark1):
                        ktoa = '11-' + kknr + '-KV-meldung'
                    elif re.search(', Zusatzbeitr.*Krankenvers|, Beitr.*Krankenvers.*erm.*igt', remark1):
                        ktoa = '11-' + kknr + '-KV-meldZUS'
                    elif ' Arbeitsfoerderung' in remark1 or 'Arbeitslosen' in remark1:
                        ktoa = '11-' + kknr + '-AV-meldung'
                    elif ' Rentenversicherung' in remark1:
                        ktoa = '11-' + kknr + '-RV-meldung'
                    elif ' Krankenversicherung' in remark1:
                        ktoa = '11-' + kknr + '-KV-meldung'
                    elif ' Pflegeversicherung' in remark1:
                        ktoa = '11-' + kknr + '-PV-meldung'
                    elif ' Krankheitsaufwendungen' in remark1:
                        ktoa = '11-' + kknr + '-U1-meldung'
                    elif ' Mutterschaftsaufwendungen' in remark1:
                        ktoa = '11-' + kknr + '-U2-meldung'
                    elif ' Insolvenzgeldversicherung' in remark1:
                        ktoa = '11-' + kknr + '-U3-meldung'
                    elif re.search('inheitliche *P', remark1):
                        ktoa = '11-' + kknr + '-ST-meldung'
#                    elif ' Storno' in remark1:
#                        ktoa = '11-' + kknr + '-ZZ-meldung'
                    elif ' UST' in remark1:
                        ktoa = '11-' + kknr + '-xxUSTxx-meldung'
                    elif ' einzubehaltene' in remark1:
                        ktoa = '11-' + kknr + '-LS-meldung'
                    elif ' pauschal' in remark1:
                        ktoa = '11-' + kknr + '-PL-meldung'
                    elif ' Solidarit' in remark1:
                        ktoa = '11-' + kknr + '-SZ-meldung'
                    elif ' Kirchensteuer roem' in remark1:
                        ktoa = '11-' + kknr + '-KR-meldung'
                    elif ' Kirchensteuer evan' in remark1:
                        ktoa = '11-' + kknr + '-KE-meldung'
                    elif ' Kirchensteuer altk' in remark1:
                        ktoa = '11-' + kknr + '-KA-meldung'
                    elif ' Kirchensteuer isra' in remark1:
                        ktoa = '11-' + kknr + '-KB-meldung'
                    elif re.search(' Sae?umn| Mahn|gebuehr', remark1):
                        ktoa = '11-' + kknr + '-saeumn'
                    elif re.search(' Beitrae?g| Betriebspr', remark1):
                        ktoa = '11-' + kknr + '-beitrag'
                    elif re.search(' Umbuchung +Leistung+ U1', remark1):
                        ktoa = '11-' + kknr + '-umbuchung'
#                    elif 'Storno' in remark1:
#                        ktoa = '11-' + kknr + '-ZZ-meldung'
                    else:
                        continue
                    if stornofaktor < -1.1:
                        betrag1 = - (abs( float(m.group(4) + '.' + m.group(5)) ))
                    else:
                        betrag1 = stornofaktor * float(m.group(4) + '.' + m.group(5))
                    if abs(betrag1) > 0.0001:
                        buchungen1.append([datum, '%3.2f' % betrag1, ktoa, ktob, '0.00', remarkadd + remark1])
                        continue

                buchungen = buchungen + buchungen1
                
                m = re.search('^(.*)\.(.*?)$', file)  #  renaming the original files
                filename = m.group(1)
                if not filename == newname:
                    print('rename file ' + file + ' to ' + newname + "." + m.group(2))
                    os.rename(file, newname + '.' + m.group(2))
                    if os.path.isfile(filename + '.pdf'):
                        os.rename(filename + '.pdf', newname + '.pdf')

                zeilen = []
                for buchung in buchungen:
                    zeilen.append('  '.join(buchung))

                if buchungen:
                    ktotext = ktotext + '\n' + '\n'.join(zeilen) + '\n'

        return(ktotext)  

#********************************************************************************
#*********************************************************************************

    def to_kto (self):     # open the csv and kto files and prepare for processing
    
        csv_files = glob.glob(self.dir+"/*.csv")
        csv_files.sort()
        
        for csv_file in csv_files:

            text   = open(csv_file).read()
            text1  = ""
            zeile0 = ""
            bed    = 0
            for zeile in text.split("\n"):    #  erase additional line breaks
                zeile = zeile.strip()
                if re.search(r"^\"?\d\d\.\d\d\.\d\d\d\d\"?",zeile):
                    text1  = text1 + zeile0 + "\n"
#                    buchungen.append(text1.strip().split(";"))
                    zeile0 = zeile
                else:
                    zeile0 = zeile0 + zeile
            text1 = text1 + zeile0
            text1 = text1.strip() + "\n"
            text1 = text1.replace("\"\"","\";\"",99999999)
            if not text == text1:            
                open(csv_file+"~","w").write(text)
                open(csv_file,"w").write(text1)
                
        ktofile = glob.glob(self.dir+"/*.kto")
        
        if len(ktofile) > 1:
            print("More than one kto-file.")
            return()
        elif len(ktofile) == 0:
            print("No ktofile found.")
            return()
            
        erg = self.analyse_ktofile(open(ktofile[0]).read())
        if not erg == "":
            print(erg)
            return()

        for csv_file in csv_files:
            print(csv_file)
            erg = self.merge_with_ktofile_0(open(csv_file).read())
            if not erg == "":
                print(erg)
                return()

        erg = self.merge_with_ktofile()
        if not erg == "":
            print(erg)
            return()

        self.assign_contra_accounts()

        self.combine_ktofile()

        open(ktofile[0],"w").write(  "\n".join(self.kto_text) + "\n")



#*********************************************************************************
        
    def analyse_ktofile (self,kto_text0):  #  creates the pattern-to-counter-account map and the account pattern

        self.ukto             = None
        self.kto_text         = kto_text0.split("\n")
        self.equivalent_acc   = {}
        self.ktolines         = {}
        self.new_lines        = []
        self.csvlines         = {}
        self.undef_acc        = []


        ktotext1              = self.kto_text[:]
        ktotext1.sort()
        
        zaehler = -1
        for zeile in self.kto_text:
            zaehler = zaehler + 1

            m = re.search(r"^(\d\d\d\d\d\d\d\d) +(\-?\d+\.\d\d) +(\S+) +(\S+) +(\-?\d+\.\d\d) +(.*)$",zeile)
            if not m:
                continue
                
            datum    = m.group(1)
            betrag   = m.group(2)
            kto1     = m.group(3)
            kto2     = m.group(4)
            remark   = m.group(6)
            
            if kto2 == config.STANDARD_CONTRA_ACCOUNT:
                self.undef_acc.append(zaehler)

            patterns = self.extract_patterns_from_remark(remark)

            if not patterns == "":
                if not patterns in self.equivalent_acc:
                    self.equivalent_acc[patterns] = []
                self.equivalent_acc[patterns].append(zeile)
                
                if kto2 == config.STANDARD_CONTRA_ACCOUNT:
                    zaehler1 = zaehler
                    while zaehler1 > 0:
                        zaehler1 = zaehler1 - 1
                        zeile1   = self.kto_text[zaehler1]
                        erg      = self.check_patterns(patterns,"","",zeile1)
                        if erg:
                            m1 = re.search(r"^(\d\d\d\d\d\d\d\d) +(\-?\d+\.\d\d) +(\S+) +(\S+) +(\-?\d+\.\d\d) +(.*)$",zeile1)
                            if m1:
                                kto02 = m1.group(4)
                                if not kto02 == config.STANDARD_CONTRA_ACCOUNT:
                                    self.equivalent_acc[patterns][-1] = zeile1
                                    break
                    
                
                    
#            print(self.ukto)
            if self.ukto == None:
                self.ukto = kto1
            else:
                while 0 == 0:
                    if self.ukto.startswith(kto1):
                        self.ukto = kto1
                        break
                    m = re.search(r"^(.*)\-(.*)$",kto1)
                    if m:
                        kto1 = m.group(1)
                    else:
                        return("No account pattern found.")
                        
            self.add_ktoline(datum,betrag,{ 'ZAEHLER' : zaehler, 'ZEILE' : zeile, 'REMARK' : remark})
                    
        return("")
                                
#*********************************************************************************

    def add_ktoline (self,datum,betrag,entry):
    
        absbetrag = re.sub(r"---","",betrag)
        if not datum in self.ktolines:
            self.ktolines[datum] = {}
        if not absbetrag in self.ktolines[datum]:
            self.ktolines[datum][absbetrag] = []
        
        self.ktolines[datum][absbetrag].append(entry)                    

#*********************************************************************************

    def add_csvline (self,datum,betrag,entry):
    
        absbetrag = re.sub(r"---","",betrag)
        if not datum in self.csvlines:
            self.csvlines[datum] = {}
        if not absbetrag in self.csvlines[datum]:
            self.csvlines[datum][absbetrag] = []
        
        self.csvlines[datum][absbetrag].append(entry)                    

#*********************************************************************************
        
    def extract_patterns_from_remark (self,remark):

        patterns = []
        while 0 == 0:
            m = re.search(r"^(.*?)\#(.*?)\#(.*)$",remark)
            if not m:
                break
            patterns.append(m.group(2))
            remark = m.group(3)
        patterns = ",".join(patterns)
        return(patterns)

#*********************************************************************************

    def merge_with_ktofile_0 (self,csv_text):

        self.csvline = {}

        for zeile in csv_text.split("\n"):
#            print(zeile)
            bed = 1
            for ausschlusspattern in config.EXCLUDE_CSV_LINES.split(","):
                if ausschlusspattern.upper() == ausschlusspattern and ausschlusspattern.lower() in zeile.lower() or ausschlusspattern in zeile:
                    bed = 0
                    continue
            if bed == 0:
                continue
                
#            print(zeile)
            erg       = self.create_buchung(zeile)
#            print(erg)
            if erg == None:
                continue
            datum     = erg['DATUM']
            betrag    = erg['BETRAG']
            remark    = erg['REMARK']
            absbetrag = re.sub(r"---","",betrag)

            self.add_csvline(datum,absbetrag,erg)
            
        return("")

#*********************************************************************************

    def merge_with_ktofile (self):

        for datum in self.csvlines:
            for absbetrag in self.csvlines[datum]:
                for erg in self.csvlines[datum][absbetrag]:

                    remark    = erg['REMARK']

                    if not datum in self.ktolines or not absbetrag in self.ktolines[datum]:
                        self.append_to_konto(erg)

                    else:
#                        print("-----")                        
#                        print("VVV",datum,absbetrag,remark)
#                        #  es gibt also mindestens einen Eintrag mit gleichem Datum und gleichen Absolutbetrag
                        #  Alle diese Eintrage durchgehen, fuer jedes moegliche Pattern in der CSV-Remark:

                        for pattern in (remark.split(";")):
                            pattern = re.sub(r"\"?(.*?)\"?","\\1",pattern)
                            if pattern == "":
                                continue
#                            print(self.no_umlaute(pattern))
                            anzahl_ziel    = 0
                            anzahl_zeilen  = 0
                            matching_entry = self.ktolines[datum][absbetrag][0]
                            for entry in self.ktolines[datum][absbetrag]:
#                                print("WW",pattern)
#                                print("VV",entry['REMARK'])
                                if self.no_umlaute(pattern) in self.no_umlaute(entry['REMARK']):
                                    matching_entry = entry
                                    anzahl_zeilen  = anzahl_zeilen + 1
                                    if anzahl_zeilen > 1:
                                        break
                                if anzahl_zeilen > 1:
                                    break
                            if anzahl_zeilen == 1:
                                for entry1 in self.csvlines[datum][absbetrag]:
                                    if pattern in entry1['REMARK']:
                                        anzahl_ziel = anzahl_ziel + 1
                                    if anzahl_ziel > 1:
                                        break
                                if anzahl_ziel < 2:
                                    break

                        if anzahl_zeilen > 1:
                            return("More than one matching line found for " + entry['ZEILE'] + ".")

                        remark_orig = matching_entry['REMARK']
                        remark1     = re.sub(r"^[\+\-]{2}","",remark_orig)
                        remark1     = remark1.replace("#","",9999)
#                        print(remark)
#                        print(datum,"    ",remark1)
                        if not remark.replace("#","",9999) == remark1:           #  only if the remark is changed
#                            print(12345)
                            zaehler = matching_entry['ZAEHLER']                  #  we replace it by the CSV, but keep the markers!
                            zeile1  = matching_entry['ZEILE']
                            m = re.search(r"^(\d\d\d\d\d\d\d\d +\-?\d+\.\d\d +\S+ +\S+ +\-?\d+\.\d\d +[\+\-]*)(.*)$",zeile1)
                            if m:
                                patterns_orig = self.extract_patterns_from_remark(remark_orig)
                                for pattern in patterns_orig:    #  save the patterns by transferring them into new remark
                                    remark.replace(pattern,"#"+pattern+"#")
                                self.kto_text[zaehler] = m.group(1) + remark
                                
                        
        return("")


#******************************************************************************

    def no_umlaute (self,text):
    
        text = text.replace("ü","ue",99999999)
        text = text.replace("ä","ae",99999999)
        text = text.replace("ö","oe",99999999)
        text = text.replace("Ü","Ue",99999999)
        text = text.replace("Ä","Ae",99999999)
        text = text.replace("Ö","Oe",99999999)
        text = text.replace("ß","ss",99999999)
        text = text.replace("#",""  ,99999999)
        text = text.replace(" ","",99999999)
        text = text.replace("+","",99999999)
        text = text.replace("-","",99999999)
        text = text.replace("  "," ",99999999)
        text = text.replace("  "," ",99999999)
        text = text.replace("  "," ",99999999)
        text = text.replace("  "," ",99999999)
        return(text)

#******************************************************************************

    def create_buchung (self,buchungstext):
    
        datum    = ""
        betrag   = ""
        soll     = ""
        patterns = []

        m = re.search(r"^(\d\d\d\d\d\d\d\d) +(\-?\d+\.\d\d) +(\S+) +(\S+) +(\-?\d+\.\d\d) +(.*)$",buchungstext)
        if m:
            return({ 'DATUM': m.group(1), 'BETRAG' : m.group(2), 'REMARK' : m.group(6), 'ZEILE' : buchungstext})

        buchungstext = re.sub(r"\"\"","\";\"",buchungstext,99999999)

        for pattern in buchungstext.split(";"):
            pattern = re.sub(r"^\"?(.*?)\"?$","\\1",pattern)
            m = re.search(r"^(\d\d)\.(\d\d)\.(\d\d\d\d)$",pattern)
            if m:
                if datum == "":
                    datum = m.group(3) + m.group(2) + m.group(1)
                continue
            m = re.search(r"^(\-?)([\.0123456789]+)[,\.](\d\d)(\-?)$",pattern)
            if m:
                betrag = m.group(1) + m.group(4) + re.sub(r"\.","",m.group(2),9999) + "." + m.group(3)
                continue
            if pattern == "S":
                soll = "-"
                continue
            if pattern == "H":
                continue
            if pattern == "EUR":
                continue
            if pattern == "":
                continue
            patterns.append(pattern)
            
        betrag = soll + betrag
        if len(patterns) < 2:
            patterns.append("xxx")
        remark = ";".join(patterns)

#        print(betrag)
        try:
            if not type(eval(betrag)) == type(0.1):
                return(None)
        except:
            return(None)
            
        if not re.search(r"^\d\d\d\d\d\d\d\d$",datum):
            return(None)
        
        return({ 'DATUM': datum, 'BETRAG' : betrag, 'REMARK' : remark, 'ZEILE' : buchungstext})
            
#******************************************************************************
            
    def append_to_konto (self,entry):
    
        datum  = entry['DATUM']
        betrag = entry['BETRAG']
        remark = entry['REMARK']

        print(datum,betrag,self.ukto)
        zeile  = datum + "  " + betrag + "  " + self.ukto + "  " + config.STANDARD_CONTRA_ACCOUNT + "  0.00  " + remark


#        print("XX",zeile)

        self.new_lines.append(zeile)

#******************************************************************************

    def combine_ktofile (self):
    
        for line in self.new_lines:
            print(line)
            self.kto_text.append(line)

#******************************************************************************

    def assign_contra_accounts (self):
    
        used_numbers1    = []
        used_numbers2    = []
        self.check_cache = {}

        for patterns in self.equivalent_acc:   #  run through all patterns, these
                                               #  define equivalence classes of accounts

            print(patterns)
            kto1 = ""
            kto2 = ""
            
            for zeile in self.equivalent_acc[patterns]:
            
                print(zeile)
                m = re.search(r"^(\d\d\d\d\d\d\d\d) +(\-?\d+\.\d\d) +(\S+) +(\S+) +(\-?\d+\.\d\d) +(.*)$",zeile)
                if m:
                    kto1 = m.group(3)
                    if kto2 == "" or kto2 == m.group(4):
                        kto2 = m.group(4)
                    else:
                        kto2 = ""
                        print("Ambiguous pattern in lines:")
                        print(zeile0)
                        print(zeile)
                        break
                zeile0 = zeile
                
            for nr1 in self.undef_acc:
                if nr1 in used_numbers1:
                    continue
                x = self.check_patterns(patterns,kto1,kto2,self.kto_text[nr1])
                if x: 
                    self.kto_text[nr1] = x
                    used_numbers1.append(nr1)
                    
            nr2 = 0
            while nr2 < len(self.new_lines):                
                if nr2 in used_numbers2:
                    continue
                x = self.check_patterns(patterns,kto1,kto2,self.new_lines[nr2])
                if x: 
                    self.new_lines[nr2] = x
                nr2 = nr2 + 1
                    
#******************************************************************************

    def check_patterns (self,patterns,ktoa,ktob,zeile):
                            
        if not zeile in self.check_cache:
            m = re.search(r"^(\d\d\d\d\d\d\d\d) +(\-?\d+\.\d\d) +(\S+) +(\S+) +(\-?\d+\.\d\d) +(.*)$",zeile)
            if m:
                erg = [ m.group(1),m.group(2),m.group(3),m.group(4),m.group(5),m.group(6)]
                self.check_cache[zeile] = erg   #  Caching, can be disabled by disabling this line
            else:
                return(None)
        else:
            erg = self.check_cache[zeile]
            
        datum   = erg[0]
        betrag  = erg[1]
        kto1    = erg[2]
        kto2    = erg[3]
        remark  = erg[5]
        remark1 = remark.replace("#","",9999)
        
        for pattern in patterns.split(","):
            m = re.search("^(.*?)"+pattern+"(.*)$",zeile)
            if not m:
                return(None)
            remark1 = m.group(2)
            
        zeile = datum + "  " + betrag + "  " + ktoa + "  " + ktob + "  0.00  " + remark
        
        return(zeile)
            

#******************************************************************************

    def xxcsv (self,multiline,ktotext,texts,gegenkonto,datumsfeld,betragsfeld,*bemerkungsfelder):
        
        self.is_einnahmenkonto = 0
        if gegenkonto[0] == "-":
            gegenkonto = gegenkonto[1:]
            self.is_einnahmenkonto = 1

        text = ""

        for text0 in texts:   #  fuer Quittungen
            m = re.search(r"^([a-z]+[\\\/]|)(\d\d\d\d\d\d)\.(qq_|qw_|)(\d+)\_(\d\d)\_+(.*?)\.ocr$",text0)
            if m:
                datum    = m.group(2)
                ust      = re.sub(r"_","",m.group(3))
                betrag1  = m.group(4) + "," + m.group(5)
                betrag   = "-" + betrag1
                remark   = m.group(1) + m.group(6)
                text1    = datum[4:6] + "." + datum[2:4] + "." + datum[0:2] + ";" + betrag + ";" + ust + remark  + "\n"
                if not m.group(1) == "":
                    text1  = text1 + ( datum[4:6] + "." + datum[2:4] + "." + datum[0:2] + ";" +
                                betrag1 + ";Beleg " + re.sub(r"^[\+\-]+","",remark)  + "\n" )
            else:
                text1 = text0
            text = text + "\n\"---SEPARATOR---\"\n" + text1
        
        if multiline == 1:
            text = re.sub(r'\n',"",text,99999999,re.DOTALL)
            text = re.sub(r'""','"\n"',text,99999999,re.DOTALL)
            text  = re.sub(r"\"\"","\"\n\"",text,99999999,re.DOTALL)
        self.csv_ist_fuehrend = (multiline == 2)

        text  = re.sub(r"\"",'',text,99999999,flags=re.DOTALL)
        text  = re.sub(r"ä","ae",text,99999999)
        text  = re.sub(r"ö","oe",text,99999999)
        text  = re.sub(r"ü","ue",text,99999999)
        text  = re.sub(r"Ä","Ae",text,99999999)
        text  = re.sub(r"Ö","Oe",text,99999999)
        text  = re.sub(r"Ü","Ue",text,99999999)
        text  = re.sub(r"ß","ss",text,99999999)
        text0 = {}

        zaehler = "0000"
        for zeile in text.split("\n"):          #   die csv-Datei-Zeilen in einem Hash speichern, um Doubletten zu vermeiden
#            print(zeile)
            if zeile == "---SEPARATOR---":
                zaehler = ("%04u" % (int(zaehler) + 1) )
            else:
                zeile1        = zaehler + ";" + re.sub(r"\"","",zeile,99999999)
                text0[zeile1] = zeile1.split(";")
            
        self.bemerkungsfelder = list(bemerkungsfelder)
        self.datumsfeld   = datumsfeld
        self.betragsfeld1 = int(betragsfeld)
        self.betragsfeld2 = int ( 100 * ( betragsfeld - int(betragsfeld) + 0.005 ) )
        self.feldanzahl = max ( self.bemerkungsfelder + [self.datumsfeld,self.betragsfeld1,self.betragsfeld2] )

        zeilencsv = []
        zeilenkto = {}
        intervals = {}
        
        zeilen = list(text0.values())
        zeilen.sort(key=lambda x: x[0]+x[1])

        for zeile in zeilen:   #  jetzt alle eindeutigen zeilen der csv-dateien durchgehen

            if len(zeile) - 1 < self.feldanzahl:
                continue

            datum = zeile[self.datumsfeld]
            
            m     = re.search(r"(\d\d)\.(\d\d)\.(\d?\d?\d\d)",datum)
            if m:
                datum = m.group(3) + m.group(2) + m.group(1)
            if len(datum) == 6:
                datum = "20" + datum
            if not len(datum) == 8:
                continue
            
            betrag = zeile[self.betragsfeld1]
            if self.betragsfeld2 > 0:
                betrag = betrag + zeile[self.betragsfeld2]
            betrag = re.sub(r"\.","",betrag,9999)
            betrag = re.sub(r",",".",betrag)

            m      = re.search(r"^(.+)([-SH])(.*)$",betrag)
            if m:
                if m.group(2) == "H":
                    betrag = m.group(1) + m.group(3)
                else:
                    betrag = "-" + m.group(1) + m.group(3)
            
            betrag = re.sub(r"^-0\.00$","0.00",betrag)
            bemerkung = []
            for bfeld in self.bemerkungsfelder:
                bemerkung.append(zeile[bfeld])
            remark = " ".join(bemerkung)
            remark = re.sub(r"[\"\'\?]","",remark,9999)
            remark = re.sub(r"^ *(.*?) *$","\\1",remark)
            if len(remark) == 0:
                remark = "Betrag " + str(betrag)
            try:
                float(betrag)
            except:
                continue


            zeile_ist_ausserhalb_aller_csv_dateien = True
            for nr in intervals:  #  das letzte in Bearbeitung stehende 
                if not zeile[0] == nr:  #   Interval nicht beruecksichtigen
                    interval = intervals[nr]
                    if interval[0] <= datum < interval[1]:
                        zeile_ist_ausserhalb_aller_csv_dateien = False
                        continue   #   um nochmals Dopplungen bei sich ueberlappenden csv-Dateien zu vermeiden
            if not zeile_ist_ausserhalb_aller_csv_dateien:
                continue

            betrag = re.sub(r"^\+","",betrag)
            remark = re.sub(r" +"," ",remark,9999)
            zeilencsv.append([datum,betrag,remark])
            if not zeile[0] in intervals:
                intervals[zeile[0]] = [datum,datum]
            else:
                intervals[zeile[0]][0] = min( intervals[zeile[0]][0], datum )
                intervals[zeile[0]][1] = max( intervals[zeile[0]][1], datum )

#        print(intervals)
                
#        for zeile in zeilencsv:
#            print (zeile)

        return( self.kto_parser (zeilencsv,ktotext,intervals,gegenkonto) )

#****************************************************************************

    def xxabschreibung (self,ktotext,abschreibungskonto,weitere_abschreibungskonten={}):

        text         = []
        inventarlist = {}
        ab_kto       = {}
        for zeile in ktotext.split('\n'):
            m = re.search('^(\d\d\d\d\d\d\d\d) +(\-?\d+\.\d\d) +(\S+?) +(\S+) +(\-?\d+\.\d\d) +(.*)', zeile)
            if not m:
                text.append(zeile)
                continue
            betrag = float(m.group(2))
            m1     = re.search(r"^(.*)\-AN$",m.group(3))
            m2     = re.search(r"^(.*?)-([^\-]+)",m.group(4))
            if not m1:
                m1 = re.search(r"^(.*)\-AN$",m.group(4))
                m2 = re.search(r"^(.*?)\-([^\-]+)",m.group(3))
            if m1:
                text.append(zeile)
                inventar = m1.group(1)
                if not inventar in inventarlist:
                    inventarlist[inventar] = betrag
                else:
                    inventarlist[inventar] = inventarlist[inventar] + betrag
                if m2 and betrag > 0.0:
                    ab_kto[inventar] = "-" + m2.group(2) + "-"
     
        for inventar in inventarlist:
            m = re.search(r"^(.*\-)(\d\d)([123456789ABC])\_(\d+)(.*?)$",inventar)
            if m:
                abschreibungsjahr   = m.group(2)
                kaufmonat           = m.group(3)
                abschreibungsanteil = int(m.group(4))
                betrag              = inventarlist[inventar]
                ktoa = m.group(1) + m.group(2) + m.group(3) + '_' + m.group(4) + m.group(5) + '-AS'
            else:
                continue
            if kaufmonat in 'ABC':
                kaufmonat = {'A': '10', 'B': '11', 'C': '12'}[kaufmonat]
            teilabschreibung = 13 - int(kaufmonat)
            if abschreibungsanteil == 1:
                teilabschreibung = 12
            restwert = betrag
            jahr = int('20' + abschreibungsjahr)
            zaehler = 1
            while (0 == 0):
                datum1 = '%04u' % jahr + '1228'
                erstjahresanteil = float(teilabschreibung) / 12.0
                abschreibungsbetrag = -float('%3.2f' % min(erstjahresanteil * betrag / abschreibungsanteil, restwert))
                restwert = float('%3.2f' % restwert) + float('%3.2f' % abschreibungsbetrag)
#                if float(restwert) / float(betrag) < 0.01 * abschreibungsanteil:
                if float(restwert) < 0.01 * float(betrag) / float(abschreibungsanteil) or abs(restwert) < 1.00:
                    abschreibungsbetrag = abschreibungsbetrag - restwert
                    restwert            = 0.0
                
                betrag1 = '%3.2f' % abschreibungsbetrag
                abschreibungskonto1 = re.sub("-xxx-",ab_kto[inventar],abschreibungskonto)
                if int(abschreibungsanteil) in weitere_abschreibungskonten:
                    abschreibungskonto1 = abschreibungskonto1[0:-4] + str(weitere_abschreibungskonten[abschreibungsanteil])

                if abs(restwert) < 0.001:
                    text.append(datum1 + '  ' + betrag1 + '  ' + ktoa + '  ' +
                                abschreibungskonto1 +
                                '  0.00  ' + 'Rest-Abschreibung, Kaufwert: ' + '%3.2f' % betrag)
                    break
                else:
                    remark1 = 'Abschreibung'
                    if teilabschreibung < 12:
                        remark1 = remark1 + ' (' + str(teilabschreibung) + '/12)*'
                    remark1 = remark1 + ', ' + str(zaehler) + '. Teil-Abschreibung (1/' + str(abschreibungsanteil) + ')'
                    remark1 = remark1 + ', Kaufwert: ' + '%3.2f' % betrag
                text.append(datum1 + '  ' + betrag1 + '  ' + ktoa + '  ' + abschreibungskonto1 + '  0.00  ' + remark1)
                jahr = jahr + 1
                zaehler = zaehler + 1
                teilabschreibung = 12

        ktotext = '\n'.join(text) + '\n'
        return(ktotext)

#*********************************************************************************

    def xxconnect_to_accounting (self,ktotext):   #   ,buchhaltung=""):
    
        ktotext1 = ""
        zeilen   = {}
        ukto     = ""
        ukto1    = ""
        
        if len(ktotext) == 2:  #  wenn es ein Zielfile gibt, dieses untersuchen und die passenden Zeilen so lassen
            m     = re.search(r"^(\S+) +\(\S\S\S\S\S\S\) ",ktotext[1].split("\n")[0])
            if not m:
                return(None)
            ukto1 = m.group(1)

        for zeile in ktotext[0].split("\n"):  #  erst das Quellfile aufbereiten
            print("::::",zeile)
            m = re.search('^(\d\d\d\d\d\d\d\d) +(\-?\d+\.\d\d) +'+ukto+'\-(\S+?) +(\S+) +(\-?\d+\.\d\d) +(.*)', zeile)
            if not ukto == "" and m:
                zeile1    = m.group(1) + "  " + re.sub(r"--","","-"+m.group(2)) + "  " + ukto1 + "-" + m.group(4) + "  " + m.group(3)
                zeile_key = zeile1
                zeile1    = zeile1 + "  " + re.sub(r"--","","-"+m.group(5)) + "  " + m.group(6)
                zeile_key = re.sub(r" ","",zeile_key+m.group(6),99999999)
#                print(":::",zeile_key)
                zeilen[ zeile_key ] = zeile1  # dessen Zeilen werden in einem Hash gespeichert, dessen Keys die Zeile
                                              # ohne Leerzeichen und Saldofeld sind
            elif ukto == "":
                m = re.search('^(\S+)\-(\S+) +\(.*?\)',zeile)
                if m:
                    ukto  = m.group(1) + "-" + m.group(2)
                else:
                    return(None)

        if len(ktotext) == 2:  #  Zielfile untersuchen und die passenden Zeilen so lassen
            for zeile in ktotext[1].split("\n"):
                m = re.search('^(\d\d\d\d\d\d\d\d +\-?\d+\.\d\d +\S+? +\S+) +(\-?\d+\.\d\d) +(.*)', zeile)
                if m:
                    zeile_key = re.sub(r" ","",m.group(1)+m.group(3),99999999)
#                    print("-->",zeile_key)
                    if zeile_key in zeilen:   #  Zeile gibt es schon im Zielfile
                        ktotext1 = ktotext1 + zeile + "\n"   # Zeile genau an dieser Stelle auch lassen
                        zeilen[ zeile_key ] = ""             # und aus dem Zeilen-Hash loeschen
                else:
                    ktotext1 = ktotext1 + zeile + "\n"

        for zeile in zeilen.values():  #  die nicht wiedergefundenen Zeilen beim Zielfile unten anhaengen
            if not zeile == "":
                ktotext1 = ktotext1 + zeile + "\n"
                
        return(ktotext1)

#*********************************************************************************

    def xxconsors (self,ktotext,texts,gegenkonto):
        
        zeilencsv = []
        self.csv_ist_fuehrend  = False
        self.is_einnahmenkonto = 0

        for text in texts:

            for zeile in text.split("\n"):

                zeile1 = zeile.split(";")   #   lesen von Vorab-CSVs
                if len(zeile1) > 2:
                    datum  = zeile1[1].split(".")
                    if len(datum) == 3:
                        betrag = re.sub(r"\.","",zeile1[7],999)
                        betrag = re.sub(r",",".",betrag)
                        remark = zeile1[5] + " " + zeile1[2] + " " + zeile1[3] + " " + zeile1[4] + " " + zeile1[5] + " " + zeile1[6]
                        remark = re.sub(r"[\(\)]","",remark,9999)
                        remark = re.sub(r" +"," ",remark,9999)
                        remark = self.normalize_text(remark)
                        remark = re.sub(r"CHI.*?V.*?ID.COM","CLFCK.COM",remark)
                        zeilencsv.append([datum[2]+datum[1]+datum[0],betrag,remark])

        for text in texts:

            buchungen = []
            text      = text + "   \n   \n"
            text      = re.sub(chr(12),"",text,99999999)
            text      = re.sub(r"BONIFIKATION","< x > BONIFIKATION",text,99999999)
            text      = re.sub(r"\n +VISA","    < x > VISA",text,99999999,re.DOTALL)

            m     = re.search(r"Datum +\d\d\.(\d\d)\.(\d\d)",text)
            if m:
                monat = int(m.group(1))
                jahr1 = "20" + m.group(2)
                jahr0 = "%04u" % (int(jahr1)-1)

        
            while (0 == 0):

                m = re.search(r"^(.*?)\n(\S+ *\S*) +(\d\d)\.(\d\d)\. +(\d\d\d\d) +\d\d\.\d\d\. +([\d\.]+,\d\d)([\-\+]?)\n +([^\n]*?)\s+\< *([^\n]+?) *\> +(.*?)(\n *\S.*$)",text,flags=re.DOTALL)
                if not m:
                    break
                    
                jahr  = jahr1
                if int(m.group(4)) > monat:
                    jahr = jahr0
                text = m.group(1) + m.group(11)
                buchungen.append( [jahr + m.group(4) + m.group(3), re.sub(r",",".",
                                      re.sub(r"[\.\+]","",m.group(7)+m.group(6),99) ),
                                      re.sub(r" +"," ",m.group(2) + " " + m.group(8),99)
                                      + " " + m.group(9) + " IBAN " + re.sub("\s+"," ",m.group(10),9999) ] )

            while (0 == 0):

                m = re.search(r"^(.*?)\n(ABSCHLUSS|GEBUEHREN) +(\d\d)\.(\d\d)\. +(\d\d\d\d) +\d\d\.\d\d\. +([\d\.]+,\d\d)([\-\+]?) *\n(.*$)",text,flags=re.DOTALL)
                if not m:
                    break
                    
                jahr  = jahr1
                if int(m.group(4)) > monat:
                    jahr = jahr0
                text = m.group(1) + m.group(8)
                buchungen.append( [jahr + m.group(4) + m.group(3), re.sub(r",",".",
                                   re.sub(r"[\.\+]","",m.group(7)+m.group(6),99) ),
                                   m.group(2) + " Kontogebuehren und Zinsen"] )

            for buchung in buchungen:
                zeilencsv.append(buchung)
                
        return( self.kto_parser (zeilencsv,ktotext,{"0001": ["00000000","99999999"] },gegenkonto ) )

#******************************************************************************

    def xxkto_parser (self,zeilencsv,ktotext,intervals,gegenkonto):

#   Wir haben jetzt in zeilencsv alle Eintraege aus den csv-Dateien als Arrays der Form: Datum,Betrag,Bemerkung

        self.hilfseintraege = []   #   um die fehlenden csv-Eintraege rueckwaerts zu konstruieren


#        for z in zeilencsv:
#            print(z)


        ukto = ""
        
        ktotext1   = []
        ktotext2   = []
        doubletten = []
        for zeile0 in ktotext.split("\n"):   #   jetzt die ursprunegliche Kontodatei durchgehen

            if ukto == "":
                m = re.search(r"^\^?(\S+) +\(.*?\)",zeile0)
                if not m:
                    m = re.search(r"^\^?(\S+)",zeile0)
                if m:
                    ukto = m.group(1)
                else:
                    print("No ukto could be identified. There should be a ^pattern inside.")
                    return(ktotext)

            zeile = re.sub(r"( MANQX| XX) *$","",zeile0)        #  bereinigen
                
            mwst  = ""
#            m = re.search(r"^(.*)  (\+\+|\+\-|qq|qw)(.*)",zeile)
#            if m:
#                zeile = m.group(1) + "  " + m.group(3)
#                mwst  = m.group(2)
            zeile = re.sub(r" -0\.00 ","  0.00 ",zeile)
            m = re.search(r"^(\d\d\d\d\d\d\d\d) +(\S+) +(\S*) +(\S+) +(\-?\d+\.\d\d) +(\+\+|\+\-|qq|qw|)(.*)$",zeile)
            if m:
                datum  = m.group(1)
                betrag = m.group(2)
                ktoa   = m.group(3)
                ktob   = m.group(4)
                saldo  = m.group(5)
                mwst   = m.group(6)
#                if mwst == "++":
#                    mwst = "qq"
#                if mwst == "+-":
#                    mwst = "qw"
                remark = m.group(7)
                id     = [datum,betrag,remark]
                if id in doubletten:
                    continue
                    print(id)
                elif not ktob == gegenkonto:
                   doubletten.append(id)

                if id in zeilencsv:
                    if ktob == gegenkonto:  #  wenn eh nur das Gegenkonto gefunden wsurde, lieber die csv-Zeile lassen
                        continue            #  und die Kontozeile wegwerfen
                    zeilencsv.remove(id)
                    if not self.csv_ist_fuehrend:   #   wenn der Kontoeintrag schon in einer
                        ktotext1.append(zeile)      #   csv-Zeile vorkommt, diese loeschen
                    else:
                        id.append(ktob)  #  der Gegenkontoeintrag ist trotzdem interessant, den mitnehmen
                        id.append(mwst)  #  der Mwsteintrag ist auch interessant, den auch mitnehmen
                        id.append(ktoa)
                        zeilencsv.append(id)
                else:   #   wenn nicht in einer csv-Zeile gefunden, dann kann es noch sein, dass Eintraege mit
                    entries = []    #   gleichem Datum und Betrag existieren
                    for id in zeilencsv:
                        if self.is_einnahmenkonto == 0:
                            if id[0] == datum and id[1] == betrag: 
                                entries.append(id)
                        else:
                            if id[0] == datum and id[1][1:] == betrag:  #  ohne Minuszeichen
                                entries.append(id)
                    if len(entries) == 0 and not self.csv_ist_fuehrend:  #  es gibt keinen Eintrag in einer csv-Zeile, der passen koente.
                        zeile_ist_ausserhalb_aller_csv_dateien = True
                        for interval in list(intervals.values()):   #   wenn das Datum im Datumsbereich einer csv-Zeile liegt,
                            if interval[0] <= datum <= interval[1]:  #   dann ist das ein falscher Eintrag, den dann loeschen
                                zeile_ist_ausserhalb_aller_csv_dateien = False
                                break
                        if zeile_ist_ausserhalb_aller_csv_dateien:
                            try:
                                self.datumsfeld
                            except:
                                print ("ATTENTION: This line should be wrong: " + zeile0)
                            hilfseintrag = [""] * self.feldanzahl   #  wir machen uns daraus eine csv-Zeile
                            hilfseintrag[self.datumsfeld-1] = m.group(1)
                            hilfseintrag[self.betragsfeld1-1] = re.sub("\.",",",m.group(2))
                            hilfseintrag[self.bemerkungsfelder[0]-1] = m.group(6)
                            hilfseintrag = '"' + "\";\"".join(hilfseintrag) + '"'
                            self.hilfseintraege.append(hilfseintrag)
                            ktotext1.append(zeile)
                    if len(entries) > 1:
                        print(entries)
                            
                    elif len(entries) == 1:   #  es gibt ein genau identifizierbares Pendant in einer csv-Zeile
                        id     = entries[-1]
                        zeile1 = datum + "  " + betrag + "  " + ktoa + "  " + ktob + "  " + saldo + "  " + mwst + remark
                        #   hier wird jetzt geklaert, ob der Eintrag aus der CSV-Datei genommen werden soll,
                        #   oder der aus der Kontodatei
                        if self.csv_ist_fuehrend:
                            id.append(ktob)  #  der Gegenkontoeintrag ist trotzdem interessant, den mitnehmen
                            id.append(mwst)  #  der Mwsteintrag ist auch interessant, den auch mitnehmen
                            id.append(ktoa)
                        else:
                            ktotext1.append(zeile1)
                            zeilencsv.remove(id)
                    else:
                        if self.csv_ist_fuehrend and (
                                       re.search(r"-qu-(\d\d\d\d\d) +13-",zeile) or
                                       re.search(r"-qu-(\d\d\d\d\d) +10-.*?-13-",zeile) or
                                       re.search(r"-([a-z][a-z0-9][a-z0-9][a-z0-9][a-z0-9]) +12-",zeile) or
                                       re.search(r"-qu-(\d\d\d\d\d) +10-.*?-10-",zeile)):
                            pass
                        else:
                            ktotext1.append(zeile)
            else:
                ktotext2.append(zeile) 
                
        for zeile in zeilencsv:   #   die uebriggebliebenen csv-zeilen als Buchungen hinzufuegen
            remark = zeile[2]
            mwst0  = ""
            mwst   = ""
            m      = re.search(r"^(qq|qw|\+\+|\+\-)(.*)$",remark)
            if m:
                if m.group(1) == "qq":
                    mwst0 = "++"
                else:
                    mwst0 = "+-"
            konto1 = ""
            if len(zeile) == 6:
                gegenkonto1 = zeile[3]
                mwst        = zeile[4]
                konto1      = zeile[5]
            else:
                gegenkonto1 = gegenkonto
            if len(mwst0) > 0:
                mwst = mwst0
            remark = re.sub(r"^(qq\_?|qw\_?)","",remark)
            remark = re.sub(r" +"," ",remark,9999)
            if self.csv_ist_fuehrend:
                o = "  " + ukto + "-qu-12345  "
                m = re.search(r"\-([a-z][a-z0-9][a-z0-9][a-z0-9][a-z0-9])$",konto1)
                if m:
                    o = "  " + ukto + "-" + m.group(1) + "  "
            else:
                o = "  " + ukto + "  "            
            if mwst == "qq":
                mwst = "++"
            if mwst == "qw":
                mwst = "+-"
            if self.is_einnahmenkonto == 1:
                zeile[1] = re.sub(r"^\-","",zeile[1])
            ktotext1.append(zeile[0] + "  " + zeile[1] + o + gegenkonto1 + "  0.00  " + mwst + remark)

        ktotext1.sort(key=lambda x: x[0:8])
        self.hilfseintraege = "\n".join(self.hilfseintraege) + "\n"        

        return("\n".join(ktotext2+ktotext1)+"\n")

#******************************************************************************

    def xxfixpoint (self,ktotext,patterns):

        compiled_patterns = {}
        for pattern in patterns:
            compiled_patterns[pattern] = re.compile("(20\d\d)(\d\d)\d\d +(\-?\d+\.\d\d) +(\S*)"+patterns[pattern])
            
        ktotext0 = ""
        results  = []
        zaehler  = 1
        while (0 == 0):
            if ktotext0 == ktotext:
                break

            results0 = results
            results  = {}
            ktotext0 = ktotext
            ktotext  = ""
                        
            for zeile in ktotext0.split("\n")[:-1]:
#                print(zeile)
                m0 = re.search("^(\d\d\d\d\d\d\d\d) +(\-?\d+\.\d\d) +(.*)$",zeile)
                if m0:
                    for pattern in compiled_patterns:
                        m = compiled_patterns[pattern].search(zeile)
                        if m:
                            if "[" in pattern:
                                expr = pattern.replace("[","results0[\"")
                                expr = expr.replace(".JJ]","."+m.group(1)+"]")
                                expr = expr.replace(".JJMM]","."+m.group(1)+m.group(2)+"]")
                                expr = expr.replace(".MM]","."+m.group(2)+"]")
                                expr = expr.replace("]","\"]")
                                try:
                                    val  = eval(expr)
                                except:
                                    val = 0.01 * float(random.randint(1,999999))
                                    val = 0.00
                                zeile = m0.group(1) + "  " + ("%3.2f" % val) + "  " + m0.group(3)
                            else:
                                patternj  = pattern + "." + m.group(1)
                                patternjm = pattern + "." + m.group(1) + m.group(2)
                                patternm  = pattern + "." + m.group(2)
                                if not pattern in results:
                                    results[pattern] = 0.00
                                if not patternj in results:
                                    results[patternj] = 0.00
                                if not patternjm in results:
                                    results[patternjm] = 0.00
                                if not patternm in results:
                                    results[patternm] = 0.00
                                results[pattern]   = results[pattern]   + float(m0.group(2))
                                results[patternj]  = results[patternj]  + float(m0.group(2))
                                results[patternjm] = results[patternjm] + float(m0.group(2))
                                results[patternm]  = results[patternm]  + float(m0.group(2))
                
                ktotext = ktotext + zeile + "\n"
            
            print(str(zaehler) + ". round.")
            zaehler = zaehler + 1
                
        return(ktotext)
                                
#*********************************************************************************

    def xxassign_ausgaben (self,ktotext,tmpkto,idbuch0):    #   Ordnet Ausgabenkonten automatisch zu
    

        buchgrp = {}  #  Hier werden die Buchhaltungsgruppen gehalten
        zeilen  = []
        idbuch  = []
        
        for o in re.sub(r"\n",",",idbuch0,9999,re.DOTALL).split(","):
            if not o.strip() == "":
                idbuch.append(o)

        self.mark("W1")
        for zeile in ktotext.split("\n"):
            if '#' not in zeile:
                continue
            addinfo = []
            while (0 == 0):
                m = re.search(r"^(.*?)\#(.*?)\#(.*)$",zeile)
                if not m:
                    break
                addinfo.append(m.group(2))
                zeile = m.group(3)
            idbuch.append( ".*".join(addinfo) )
            print(idbuch[-1])
        self.mark("W2")

        ktoa_s =  {}
        zeilennr = 0
        for zeile in ktotext.split("\n"):
            zeilen.append(zeile)
            m = re.search(r"^(\d\d\d\d\d\d\d\d) +(\-?\d+\.\d\d) +(\S*) +(\S+) +(\-?\d+\.\d\d) +(.*)$",zeile)
            if m:
                id1   = None
                parts = None
                for id in idbuch:
                    m1 = re.search(id,zeile,re.IGNORECASE)
                    if m1:
                        id1     = id
                        parts   = []
                        zaehler = 0
                        while (0 == 0):
                            zaehler = zaehler + 1
                            try:
                                parts.append(m1.group(zaehler))
                            except:
                                break
                        break
                if id1 == None:
                    parts = []
                    id1   = re.sub(r"[\+\-\. ]","",m.group(1)+m.group(2)+m.group(6),9999)
                if not id1 in buchgrp:
                    buchgrp[id1] = []
               
                buchgrp[id1].append(
                       { 'DATUM': m.group(1), 'BETRAG': m.group(2), 'KTOA': m.group(3), 'KTOB': m.group(4),
                         'REMARK': m.group(6), 'ZEILENNR': zeilennr, 'CHANGED': 0, 'PARTS': parts } )
                ktoa_s[ m.group(3) ] = 1

            zeilennr = zeilennr + 1
            
        ust = {}
        for id in buchgrp:
            ust[id] = {}
            for entry in buchgrp[id]:
                m = re.search(r"^(\+\+|\+\-)",entry['REMARK'])
                if m:
                    ust[id][m.group(1)] = 1
            o = list(ust[id].keys())
            if len(o) == 1:
                ust[id] = o[0]
            else:
                ust[id] = ""

        zweiter_durchgang_erforderlich = False


        for id in buchgrp:

            alle_gegenkonten = {}  #  erstmal ueberhaupt alle gegenkonten zusammensammeln
            for entry in buchgrp[id]:
                o = re.sub(r"\-\d\d\d\d\d$","-BETRAG",entry['KTOB'])
                alle_gegenkonten[o] = 1
            ag = list( alle_gegenkonten.keys() )
            alle_gegenkonten = []
            for o in ag:
                if not o[0:7] == "10-1291":
                    alle_gegenkonten.append(o)
            alle_gegenkonten.sort()
            if len(alle_gegenkonten) > 2:
                print ("ALLE",alle_gegenkonten,id)
                if not idbuch0 == "":
                    zweiter_durchgang_erforderlich = True
            if len(alle_gegenkonten) > 1 and tmpkto in alle_gegenkonten:  #  wenn es mehrere gegenkonto gibt
                alle_gegenkonten.remove(tmpkto)       #  neben dem tmpkto, dann den gemeinsamen Start-String berechnen
                common_start = alle_gegenkonten[0]
                for o in alle_gegenkonten:
#                    print ("COMMON",common_start,o)
                    ul           = min(len(common_start),len(o))
                    common_start = common_start[0:ul]
                    o            = o[0:ul]
                    while (0 == 0):
                        if common_start == o:
                            break
                        common_start = common_start[:-1]
                        o            = o[:-1]
                        
#                print ("COMMON",common_start)
                if not len(alle_gegenkonten) == 1:
                    for entry in buchgrp[id]:   #  ueberpruefen, ob die Theorie stimmt, nach der die Gegenkonten gemacht sind
                        if not entry['KTOB'] == tmpkto:  #  bei allen schon zugeordneteten Konten
                            o1 = ""
                            if not len(alle_gegenkonten) == 1:
                                o1 = "".join( entry['PARTS'] )
                            if not entry['KTOB'] == common_start + o1:
                                common_start = None
                                break

                if common_start == None:
                    continue

                for entry in buchgrp[id]:  #  wenn die Theorie stimmt, dann mit den unbestimmenten Gegenkonten
                    if entry['KTOB'] == tmpkto:    #  genauso verfahren und zuordnen
                        o = ""
                        if not re.search(r"^(\,+\+|\+\-)",entry['REMARK']):
                            o = ust[id]
                        ktob = common_start
                        if not len(alle_gegenkonten) == 1:
                            ktob = ktob + "".join( entry['PARTS'] )
                        m = re.search(r"^(.*)(\-BETRAG$)",ktob)
                        if m:
                            betrag = ("%8.7f" % float(entry['BETRAG'])).strip()
                            betrag = re.sub(r"[\-\.]","",betrag)[0:5]
                            ktob   = m.group(1) + "-" + betrag
                        zeilen[ entry['ZEILENNR'] ] = (
                                entry['DATUM'] + "  " + entry['BETRAG'] + "  " +
                                entry['KTOA'] + "  " + ktob + "  0.00  " + o + entry['REMARK'] )


        ktotext = "\n".join(zeilen)

#        print("===============================",ktoa_s)
        if len(ktoa_s) > 1:
        

            zeilen1 = []
            for zeile in zeilen:  #  auch das ktoa Konto anpassen
                m    = re.search(r"^(\d\d\d\d\d\d\d\d +\-?\d+\.\d\d +)(\S+) +(\S+)( +\-?\d+\.\d\d +.*)$",zeile)
                if not m:
                    zeilen1.append(zeile) 
                    continue
                ktoa = m.group(2)
                ktob = m.group(3)
                m9   = re.search(" " + ktoa + "-(\S+) +" + ktob + " ",ktotext)
                if m9:
                    zeile1 = m.group(1) + ktoa + "-" + m9.group(1) + "  " + ktob + "  " +  m.group(4)
                    zeilen1.append(zeile1)
                else:
                    zeilen1.append(zeile) 

            ktotext = "\n".join(zeilen1)


        if zweiter_durchgang_erforderlich:
            ktotext = self.assign_ausgaben(ktotext,tmpkto,"")

        return(ktotext)
        

#*********************************************************************************

    def xxcompare (self,file1,file2,mode):
    
        text1 = None
        text2 = None
        
        for file in (file1,file2):
            text = open(file).read()

            for zeile in text.split("\n"):
                m = re.search(r"^(\d\d\d\d\d\d\d\d) +(\S+) +(\S*) +(\S+) +(\-?\d+\.\d\d) +(.*)$",zeile)
            
#*********************************************************************************

    def xxusteuer (self,ktotext,ust_kto,mode="-"):

        text = []
        ul   = len(ust_kto)
        
        jahressumme = {}

        for zeile in ktotext.split('\n'):

            m = re.search('^(\d\d\d\d\d\d\d\d) +(\-?\d+\.\d\d) +(\S+?) +(\S+) +(\-?\d+\.\d\d) +(.*)', zeile)
            if not m:
                text.append(zeile)
                continue
                
            datum  = m.group(1)
            betrag = m.group(2)
            ktoa   = m.group(3)
            ktob   = m.group(4)
            remark = m.group(6)

            if ktob[0:ul] == ust_kto:
                continue

            text.append(zeile)
            if not datum[0:4] in jahressumme:
                jahressumme[ datum[0:4] ] = 0.00
            jahressumme[ datum[0:4] ] = jahressumme[ datum[0:4] ] + float(betrag)

            if remark[0:2] == '++':
                steuersatz = 19
            elif remark[0:2] == '+-':
                steuersatz = 7
            elif remark[0:2] == '-+':
                steuersatz = 16
            elif remark[0:2] == '--':
                steuersatz = 5
            else:
                continue

#            m = re.search(r"\D\_\_+(\d+)\_(\d\d)\_\_+(\d+)\_(\d\d)\D",remark)
#            if m:
#                sign = 2*int(float(betrag)>=0)-1
#                betrag2 = float(m.group(1) + "." + m.group(2)) * sign
#                betrag3 = float(m.group(3) + "." + m.group(4)) * sign
#                betrag1 = (abs(float(betrag)) - betrag2 - betrag3) * sign
#                betrag1 = "%3.2f" % betrag1
#                betrag2 = "%3.2f" % betrag2
#                betrag3 = "%3.2f" % betrag3
#
#                if steuersatz == 19:
#                    steuersatz1 = 19
#                    steuersatz2 =  7
#                    steuersatz3 =  0
#            
#                if steuersatz == 7:
#                    steuersatz1 =  7
#                    steuersatz2 = 19
#                    steuersatz3 =  0
#            
#                ustbuchungen = [  [datum,betrag1,ktoa,ktob,steuersatz1,remark] , 
#                                  [datum,betrag2,ktoa,ktob,steuersatz2,remark] , 
#                                  [datum,betrag3,ktoa,ktob,steuersatz3,remark] ]
#            else:
#                m = re.search(r"\_\_+(\d+)\_(\d\d)\D",remark)
#                if m:
#                    sign = 2*int(float(betrag)>=0)-1
#                    betrag2 = float(m.group(1) + "." + m.group(2)) * sign
#                    betrag1 = (abs(float(betrag)) - betrag2) * sign
#                    betrag1 = "%3.2f" % betrag1
#                    betrag2 = "%3.2f" % betrag2
#
#                    if steuersatz == 19:
#                        steuersatz1 = 19
#                        steuersatz2 =  7
#            
#                    if steuersatz == 7:
#                        steuersatz1 =  7
#                        steuersatz2 = 19
#            
#                    ustbuchungen = [  [datum,betrag1,ktoa,ktob,steuersatz1,remark] , 
#                                      [datum,betrag2,ktoa,ktob,steuersatz2,remark] ]
#                else:
            if True:
                    ustbuchungen = [ [datum, betrag, ktoa, ktob, steuersatz, remark] ]
#                    print(ustbuchungen)
                    
#            print(124)
            for buchung in ustbuchungen:
                steuersatz = buchung[4]
                betrag     = buchung[1]
#                if mode == 0:
#                    gegenkto  = 1 - int(buchung[2][0:1] == '-' and not buchung[3][0:1] == '-')
#                else:
                gegenkto  = 1 - int(buchung[2].startswith(mode) and not buchung[3].startswith(mode))
                steuerart = 1 - (gegenkto + int(float(buchung[1]) < 0))
                steuerkto = ['U', 'I'][steuerart % 2]
                if steuersatz == 19:
                    steuerkto = steuerkto + '6'
                elif steuersatz == 7:
                    steuerkto = steuerkto + '7'
                elif steuersatz == 16:
                    steuerkto = steuerkto + '2'
                elif steuersatz == 5:
                    steuerkto = steuerkto + '1'
                                    
                steuerart = ['USt.', 'Vorst.'][steuerart % 2]
                if steuersatz < 100:
                    buchung[1] = '%3.2f' % (-steuersatz * 0.01 / (1.0 + steuersatz * 0.01) * float(buchung[1]))
                    buchung[5] = '   ' + str(steuersatz) + ' v.H. ' + steuerart + ' von ' + '%3.2f' % abs(float(betrag)) + ' (' + buchung[5][2:] + ')'
                else:
                    m = re.search(r"ST(\d\d)\__(\d+)\_(\d\d)",buchung[5])
                    if m:
                        buchung[1] = '%3.2f' % (float(m.group(3)+"."+m.group(3)) * [1,-1]*int(float(buchung[1])<1))
                        buchung[5] = '   ' + m.group(1) + ' v.H. ' + steuerart + ' enthalten in ' + '%3.2f' % abs(float(betrag)) + ' (' + buchung[5][2:] + ')'
                    else:
                        continue
                buchung[3 - gegenkto] = ust_kto + '-' + steuerkto
                buchung[4] = '0.00'
                text.append('  '.join(buchung))
                jahressumme[ buchung[0][0:4] ] = jahressumme[ buchung[0][0:4] ] + float( buchung[1] )
                
        brutto = ""
        jahre = list( jahressumme.keys() )
        jahre.sort()
        for jahr in jahre:
            brutto = brutto + jahr + "  " + ("%20.2f" % jahressumme[jahr] ) + "\n"
        open("brutto.txt","w").write(brutto+"\n"+str(random.randint(100000,999990))+"\n")
        
        return( '\n'.join(text) + '\n' )
        
#*************************************************************************

    def xxparse_ktoauszug1 (self,ktotext,files,kknr,kk):  #  not ktosafe

        ktotext = self.parse_ktoauszug(ktotext,files,kknr,kk)
        
        if ktotext:
            ktotext = re.sub(r" 10-1500-(\S+?)\-kkcheck"," 10-B12-3695-kk\\1",ktotext,99999999)
            ktotext = re.sub(r" 13-6011", " 13-D9a-7303",ktotext,99999999)
            ktotext = re.sub(r" 10-1500-"," 10-B12-1361-",ktotext,99999999)
            ktotext = re.sub(r" 10-1510-"," 11-C13-3759-",ktotext,99999999)
        
        return(ktotext)


#*************************************************************************

    def xxparse_ktoauszug (self,ktotext,files,kknr,kk):  #  not ktosafe

        if len(files) == 0:
            return(ktotext)
            
        uleistung = {}

        kknr = str(kknr)
        text = []
        for zeile in ktotext.split("\n"):
            if not re.search(r"^\d\d\d\d\d\d\d\d +\-?\d+\.\d\d.*\-(meldung|meldZUS|saeumn|mahn|retour)",zeile):
                if not "Leistung U" in zeile:
                    text.append(zeile)
                else:
                   ukey = re.sub(r"^(\d\d\d\d\d\d\d\d) +(\S+).*$","\\1\\2",zeile)
                   uleistung[ukey] = zeile
            elif " manuell " in zeile:
                text.append(zeile)
        ktotext = "\n".join(text) + "\n"
                  
        files.sort()
        day       = {}
        entries   = {}
        
#        return(ktotext)


        for file in files:
        
            if "_orig" in file or "orig_" in file or "_ORIG" in file or "ORIG_" in file:
                continue
        
            print (file)
        
            buchungen = []

#            periode = [100000,999999]
            m       = re.search(r"\D(\d\d\d\d\d\d)\D+(\d\d\d\d\d\d)\D",file)
            if m:
                periode = [ int(m.group(1)) , int(m.group(2)) ]
                periode.sort()
            else:
                continue
            text = open(file).read()
            text = self.normalize_text(text)
            text = re.sub("BKK Verkehrsbau","VBU",text)


            zeile0 = ""  #   special TKK
            text0  = ""
            for zeile in text.split("\n"):
                m = re.search(r"^(.*?Gesamtbetr.*Beitrags)(.*)$",zeile0)
                if m:
                    if re.search(r" *monat",zeile):
                        zeile0 = m.group(1) + zeile + m.group(2)
                else:
                    zeile0 = zeile
                text0  = text0 + zeile0 + "\n"
                zeile0 = zeile
            text0 = text0 + zeile0 + "\n"       

            text  = re.sub(r"(\d)\.(\d\d\d)\,","\\1\\2,",text0,999999); 
            while (0 == 0):   #  Punkte und Leerzeichen entfernen in Zahlendarstellungen
                text1 = text
                text  = re.sub(r"(\s)(\d+) (\d+),","\\1\\2\\3,",text,9999)
                text  = re.sub(r",(\d+) (\d+)(\s)",",\\1\\2\\3",text,9999)
                text  = re.sub(r", (\d+)",",\\1",text,9999)
                text  = re.sub(r"(\d+) ,","\\1,",text,9999)
                if text1 == text:
                    break
           
            jahr  = str(periode[0])[0:4]
            monat = str(periode[0])[4:6]
            text1 = []


            if int(kknr) == 1517:  #  TKK
                for zeile in text.split("\n"):
                    m = re.search(r"(\d\d)[/\.](\d\d\d\d) +Faelligkei",zeile)
                    if m:
                        jahr  = m.group(2)
                        monat = m.group(1)
                        continue
                    m = re.search(r"(Auszahlung.*?aus|Umbuchung.*?Leistung.*U|Saeumnis|g.*?tzter +Betrag|[bB]e.trags *nach|Mahngeb|Erlass|Retoure +G|Gebuehr|Umbuchung +Leistung +U1)(.*?) +(\-?\d+)[\,\.](\d\d)",zeile)
                    if m:
                        text1.append([jahr+monat,m.group(1) + m.group(2),m.group(3)+"."+m.group(4)])
#                        print(text1[-1])
      
            elif int(kknr) == 1510:  #  DAK
                for zeile in text.split("\n"):
                    zeile = re.sub(r"Forderung","Ford. Beitrag",zeile)
                    zeile = re.sub(r"B eitrag","Beitrag",zeile)
                    m = re.search(r"Bezugszeitraum +(\d\d)\.(\d\d)\.(\d\d)",zeile,re.IGNORECASE)
                    if m:
                        jahr  = "20" + m.group(3)
                        monat = m.group(2)
                        continue
                    else:
                        m = re.search(r"^ *(\d\d)\.(\d\d)\.(\d\d\d\d)",zeile,re.IGNORECASE)
                        if m:
                            jahr  = m.group(3)
                            monat = m.group(2)
                    m = re.search(r"(Ford. Beitrag|Beitrag aus Betriebspruefung|Mahnge|Saeumnisz|Beitrag)(.*?) +(\-?\d+)\,(\d\d)",zeile)
                    if m:
                        text1.append([jahr+monat,m.group(1),re.sub(r" ","",m.group(3)+"."+m.group(4),99)])

            else:
                for zeile in text.split("\n"):
                    zeile = re.sub(r"20t2","2012",zeile)
                    zeile = re.sub(r"\s+","  ",zeile,9999)
                    zeile = re.sub(r"'","",zeile,9999)
                    zeile = re.sub(r"________"," ",zeile,9999)
                    zeile = re.sub(r"(\D\d\d)\.(\d\d)\.(\d\d\D)","\\1.\\2.20\\3",zeile,9999)
                    zeile = re.sub(r"(SZ|SA) +.?(B)(S?)"," Beitrag\\3 ",zeile,9999,re.IGNORECASE)  #  special MobilOil
                    zeile = re.sub(r"(SZ|SA) +.?S"," Saeumniszuschlag ",zeile,9999,re.IGNORECASE)  #  special MobilOil
#                    zeile = re.sub(r"(Säumnis)","Saeumnis",zeile,9999,re.IGNORECASE)       #  special AOK RPf
                    zeile = re.sub(r"(Beitragszahlung|im +Beitrag)","",zeile,9999,re.IGNORECASE)   #  special Minijob, TKK
                    zeile = re.sub(r"\((\d\d)\/(\d\d\d\d)\)\s*","01.\\1.\\2   ",zeile)             #  VBU BKK futur
                    zeile = re.sub(r"(Beitraege )","Beitrag ",zeile,9999)                          #  Barmer                
                    zeile = re.sub(r" 0,00 "," ",zeile,9999)                                       #  special Minijob
#                    zeile = re.sub(r"(\(\d\d\.\d\d\.\d\d\d\d ?- ?\d\d\.\d\d\.\d\d\d\d\)) +\d\d\.\d\d\.\d\d\d\d","\\1",zeile,9999)   #  AOK
#                    m = re.search(r"bezugszeitraum +(.*?) *$",zeile.lower())             #  special DAK
#                    print (zeile)
                    

                    m = re.search(r"(Betriebspruef|Ausser|Vollstreck|Mahn-|Mahngeb|Saeumnisz|Rueckla.*?geb|Dauerbeitr|Beitrags?f?e?|Beitraege|Ruecklaeuf|Forderung\s)(.*?)(\s.*?\d\d)\.(\d\d)\.(\d\d.\d).*?\s(\-?[1-9]?\d*),(\d\d\-?)",zeile)
                    if m:
#                        print (" --->  MATCH  --->",zeile)
#                        print(m.group(5))
                        jahr  = m.group(5)
                        monat = m.group(4)
                        betrag = m.group(6)+"."+m.group(7)
                        betrag = re.sub(r"(.*)(-$)","-\\1",betrag)
                        text1.append([jahr+monat,m.group(1)+m.group(2),betrag])
#                        print(text1[-1])
                        
#                text = re.sub(r"^(\d\d\.\d\d\.\d\d\d\d[ \-]+\d\d\.\d\d\.\d\d\d\d)(.*?)(\d\d\.\d\d\.\d\d\d\d)",
#                                          "\\1$\\2",text,9999);  #  special AOK
#                text = re.sub(r"^(\d\d\.\d\d\.\d\d\d\d) *\- *(\d\d\.\d\d\.\d\d\d\d)(.*?)","\\1-\\2",text,9999) # special Barmer
#                text = re.sub(r"^(\d\d)[\.,](\d\d)[\.,](\d\d\d\d) "," \\1.\\2.\\3 ",text,9999)
#
#        for zeile in text.split("\n"):
#            zeile = re.sub(r"\s+"," ",zeile,9999)
#            zeile = re.sub(r"(SZ|SA) .?(B)(S?)"," Beitrag\\3 ",zeile,9999)       #  special MobilOil
#            zeile = re.sub(r"(SZ|SA) .?S"," Saeumniszuschlag ",zeile,9999)       #  special MobilOil
#            zeile = re.sub(r"(Beitragszahlung|im +Beitrag)","",zeile,9999)       #  special Minijob, TKK
#            m = re.search(r"bezugszeitraum +(.*?) *$",zeile.lower())             #  special DAK
#            if m:
#                zeitraum = m.group(1)
#            else:
#                zeitraum = ""
#            zeile = re.sub(r"^\s*Forderung \d\d\.\d\d\.\d\d","Forderung Beitrag "+zeitraum,zeile) #  special DAK
#            m = re.search(r"(Betriebspr|Beitra.?g|Saeumnis|Mahn|[A-Z].*?gebuehr|Umbuchung +Leistung +U1)(.*?)(0\d|10|11|12)([\/\.])($jahr|$jahr1)[\_ ]+(.*?)(\-?\d+)\,(\d\d)(-?)",
#                             zeile)
#            print zeile
#            if not m:
#                continue
#            text1.append([jahr + m.group(3) + ("%02u" % day[o9]),
#                          re.sub(r"--","",m.group(9) + "-" + m.group(7) + "." + m.group(8)),
#                          "555",
#                          "899",
#                          kk + ", " + m.group(1) + m.group(2) + m.group(3) + m.group(4) + m.group(5)])
#'''

            for zeile in text1:
            
                jjjjmm = zeile[0]
                remark = zeile[1]
                betrag = zeile[2]
                o9     = kknr + jjjjmm + remark[0:10]
                if o9 in day:
                    day[o9] = day[o9] + 1
                else:
                    day[o9] = 26
            
                dd   = ("%02u" % day[o9])
                ukey = ""
                betrag = re.sub(r"--","",zeile[2])
                if "Saeumn" in remark:
                    ktoa = "13-6011"
                    ktob = "10-1500-"+kknr+"-saeumn"
                elif "Mahn" in remark or "Ausser" in remark or "Forderung" in remark or "Ruecklast" in remark or "Vollstreck" in remark:
                    ktoa = "13-6011"
                    ktob = "10-1500-"+kknr+"-mahn"
                elif "Ruecklae" in remark or "Retoure" in remark:
                    ktoa = "13-6011"
                    ktob = "10-1500-"+kknr+"-retoure"
                    remark = remark  #  + " " + dd
                elif "Umbuchung Leistung" in remark:
                    ktoa = "10-1500-"+kknr+"-zahlung"   #  + "-"+self.ukto_from_betrag(betrag)
                    ktob = "10-1500-"+kknr+"-kkcheck"
                    remark = remark + " " + dd
                    ukey   = jjjjmm+dd + betrag
                elif "Umbuchung" in remark or "Auszahlung" in remark:
                    ktob = "10-1500-"+kknr+"-kk-"+self.ukto_from_betrag(betrag)+"-abr"
                    ktoa = "10-1500-"+kknr+"-kkcheck"
                    remark = remark + " " + dd
                    continue
                elif "eitra" in remark or "ettra" in remark or "orderung" or "Ford. " in remark:
                    ktob = "10-1500-"+kknr+"-meldung-"+dd
                    ktoa = "10-1510-"+kknr+"-beitrag"
                if not periode[0] <= int(jjjjmm) <= periode[1]:
                    continue
#                print(zeile,dd)
#                print(ktoa,ktob)

#                print ("--->")
                buchung =     [jjjjmm + dd,
                              betrag,
                              ktoa,ktob,"0.00",
                              kk + ", " + remark + ", Beitragsmonat " + jjjjmm[4:6] + "/" + jjjjmm[0:4]]
                entry = jjjjmm + dd + " " + buchung[1] + " " + ktoa + " " + buchung[5]
#                print (buchung)
#                print (entry)
                if not entry in entries:
                    if ukey in uleistung:
                        buchungen.append([uleistung[ukey]])
                        del uleistung[ukey]
                    else:
                        buchungen.append(buchung)
                    entries[entry] = 1

            zeilen = []
            for buchung in buchungen:
                zeilen.append("  ".join(buchung))

            if buchungen:
                ktotext = ktotext + "\n" + "\n".join(zeilen) + "\n"

 
        return(ktotext)
            
#*************************************************************************

    def xxfinanzamt_zahlungen (self,ktotext,text,zkto,fkto):  #  not ktosafe

        text1 = []
        for zeile in ktotext.split("\n"):
            if not "Steuerzahlung lt. Kontoauszug" in zeile:
                text1.append(zeile)
        ktotext = "\n".join(text1) + "\n"
                  
        zaehler = 0
        text = re.sub("Mai ","Mai.",text,99999999)
        kontext = "001"

        for zeile in text.split("\n"):
                
            if "MARK" in zeile:
                kontext = "%03u" % (int(kontext) + 1)
            zeile = zeile[15:]
            m = re.search("(.)(.) +(\d\d)(\d\d)(\d\d)(\S?) +(CR|) +(\d+) *[,.] *(\d\d) *(zusammeng|Zahlung|Umbuch)",zeile)
            if not m:
                m = re.search("(\d\d\d) +(\d\d\d\d\d\d)\S? +(\d\d)(\d\d)(\d\d)\S? +(\d\d\d\d\d\d) +(CR|) +(\d+) *[,.] *(\d\d)",zeile)
            if not m:
                m = re.search("(\d\d\d) +(\d\d\d\d\d\d)\S? +(\d\d)(\d\d)(\d\d)\S? +(\S*) +(CR|) +(\d+) *[,.] *(\d\d)",zeile)
            if m:
                betrag = "-" + re.sub("CR","-",m.group(7) + m.group(8) + "." + m.group(9))
                betrag = re.sub("--","",betrag)
                zeile1 = "20" + m.group(5) + m.group(4) + m.group(3)
#                zeile1 = "20060101"
                zeile1 = zeile1 +  "  " + betrag
                zeile1 = zeile1 + "  " + zkto + "-" + kontext + "  " + fkto + "  0.00  Steuerzahlung lt. Kontoauszug " 
                zaehler = "%04u" % (int(zaehler) + 1)
                zeile1 = zeile1 + zaehler
                ktotext = ktotext + zeile1 + "\n"
 
        return(ktotext)
            
#*************************************************************************

    def xxparse_krankmeldung (self,ktotext,files):


        kkdatum            = {}
        self.betriebsnr_kk = {}
#        new_addtext        = False

        if len(files) == 0:
            return()

        buchungen = []
        for zeile in ktotext.split("\n"):
            if not re.search(r"^\d\d\d\d\d\d\d\d +\-?\d+\.\d\d.* Ausfall",zeile):
                buchungen.append(zeile)
                  
        files.sort()

        for file in files:

            if "STORN" in file:
                continue
                
            print(file)

            text = open(file).read()
            text = self.normalize_text(text)
            text = re.sub(r"(\d)\.(\d\d\d)\,","\\1\\2\,",text,9999)
            while (0 == 0):
                o9   = text
                text = re.sub(r"(\d+) ?(\d*) ?\, ?(\d) ?(\d)","\\1\\2,\\3\\4",text)
                if text == o9:
                    break

            text = re.sub(r"[\'\"\|\]\[\(\)]","",text,99999999)

            kk   = "allg"
            if re.search(r"(15027365|Techniker +Krankenkasse)",text):
                kk = "TKK"
            if re.search(r"(98000006|Knappschaft.*Bahn-See)",text):
                kk = "MINIJOB"

            m = re.search(r"(Personalnummer|Arbeitnehmer).*?Name.*?([A-Za-z]+).*?Vorname.*?([A-Za-z]+)",text,re.DOTALL)
            if not m:
                continue
            person = (m.group(3)[0] + m.group(2)).lower()
            if person[0:2] == "ss":
                person = (m.group(3)[0:2] + m.group(2)).lower()

            m = re.search('Erstattung.*?[vV]om.*?(\\d+)\\.(\\d+)\\.(\\d\\d)(\\d+)', text, re.DOTALL)
            if not m:
                continue
            datum = m.group(3) + m.group(4) + m.group(2) + m.group(1)

            m = re.search(r"Erstattungsbetrag.*?(\d+)\,(\d+)",text,re.DOTALL)
            if not m:
                continue
            betrag = m.group(1) + "." + m.group(2)

            m = re.search("Monatliches.*?(\d+)\,(\d\d)",text,re.DOTALL)
            if not m:
                continue

            brutto = m.group(1) + "." + m.group(2)

            azeit = 40
            m = re.search("Arbeitszeit\s+w.*?chentl.*?(\d+)\,(\d+)",text,re.DOTALL)

            if not m:
                continue
            azeit = m.group(1) + "." + m.group(2)

            m = re.search("Erstattungssatz.*?(\d+)\,(\d+)",text,re.DOTALL)
            if not m:
                continue
            esatz = m.group(1) + "." + m.group(2)

            m = re.search("Fortgezahltes.*?(\d+)\,(\d+)",text,re.DOTALL)
            if not m:
                continue
            fortz = m.group(1) + "." + m.group(2)
            print ("1111111111111111111111"+file)

            m = re.search("Arbeitszeit\s+t.*glich.*?(\d+)\,(\d+)",text,re.DOTALL)
            if not m:
                az = 0.0
            else:
                az = float(m.group(1) + "." + m.group(2))
            if az < 0.1 and float(azeit) > 0.0:
                az = ("%3.1f" % (float(azeit)/5.0))

            m = re.search('Ausgefallene.*?Arbeitstage.*?(\\d+)', text, re.DOTALL)

            if m:
                ktage = m.group(1)
            else:
                ktage = "0"
                if float(brutto) > 0:
                    ktage = ("%1u" % int(float(fortz)/float(brutto)*20) )
#            print (file)
            m         = re.search(r"^(.*)\.(.*?)$",file)  #  renaming the original files
            filename0 = m.group(1)
            ending    = m.group(2)

            m = re.search("TAN +(\d\d\d\d\d\d\d\d\d)\D",text)
            if not m:
                continue
            filename = m.group(1)
                
            m = re.search("Betriebsnummer +(\d\d\d\d\d\d\d\d)\D",text)
            if not m:
                continue
            filename = filename + "_" + m.group(1)
                
            filename = filename + "_Arbeitsunf_Erstattung_" + (kk+"______")[0:6] + "_" + datum + "_" + ktage + "_" + person


            if not filename0 == filename:
                print ("rename file " + filename0 + " to " + filename)
                for rename_file in glob.glob(filename0 + ".*"):
                    m2 = re.search("(.*)\.(.*)$",rename_file)
                    os.rename(filename0 + "." + m2.group(2) ,filename + "." + m2.group(2))
#                new_addtext = True
#
#            if new_addtext:
#                self.fibu.make_addtext(ktodata)


            buchungen.append(datum + "  " + betrag + "  -kk-" + self.ukto_from_betrag(betrag) + " 12-6001-"
                             + person + "  0.00  Ausfall " + ("%2u" % int(ktage)) + " Tage a " + str(float(az)) +
                             " Std, Monatsbrutto " + brutto + ", Satz " + esatz + ", Fortzahlung " + fortz)

        ktotext = "\n".join(buchungen) + "\n"
        
        return(ktotext)
        

#*************************************************************************

    def xxparse_quittungen (self,ktotext,gegenkonto):  #  not ktosafe


        text       = []
        ll         = len(gegenkonto)
        quittungen = glob.glob("*.ocr")
        subkto     = os.path.relpath(".","..")
        subkto     = re.sub(r"^(.*)\_\_(.*)$","\\1",subkto)
        old_lines  = {}
        
        for zeile in ktotext.split("\n"):
            m = re.search(r"^(\d\d\d\d\d\d\d\d) +\-?(\d+\.\d\d) +(\S+) +(\S+) +(\-?\d+\.\d\d) +[\+\-]*(.*)",zeile)
            if m and m.group(4)[0:ll] == gegenkonto:
                old_lines[m.group(1)+m.group(2)+m.group(6)] = (m.group(3),m.group(4))
                continue
            text.append(zeile)

        for quittung in quittungen:
            m      = re.search(r"^(\d\d\d\d\d\d)\.(qq|qw|)\_*(\d+)\_+(\d\d)\_\_+(.*)\.ocr",quittung)
            if not m:
                continue
            datum  = m.group(1)
            mwst   = m.group(2)
            betrag = float(m.group(3) + "." + m.group(4))
            remark = m.group(5)
            mwst   = re.sub(r"qq","++",mwst)
            mwst   = re.sub(r"qw","+-",mwst)
#            print(old_lines)
            try:
                (kto,sub) = old_lines["20"+datum+("%3.2f"%betrag)+remark]
            except:
#                print("20"+datum+("%3.2f"%betrag)+remark)
#                (kto,sub) = ("-11111",gegenkonto+"-"+subkto)
                (kto,sub) = ("-11111",gegenkonto)
            zeile  =    ("20" + datum + "  " + ("%3.2f" % -betrag) + "  " + kto + "  " +
                          sub + "  0.00  " + mwst + remark)
            text.append(zeile)
           
        ktotext = '\n'.join(text) + '\n'
        return(ktotext)
            

#*************************************************************************

    def xxparse_finanzamt (self,ktotext,files,gegenkonto0,gegenkonto1):

        if len(files) == 0:
            return(ktotext)
            
        steuerarten = {
                "US"   :   "Umsatzsteuer",
                "LS"   :   "Lohnsteuer",
                "LD"   :   "Lohn-Solidaritaetszuschlag",
                "LR"   :   "Lohn-rk. Kirchensteuer",
                "LE"   :   "Lohn-ev. Kirchensteuer",
                "KS"   :   "Koerperschaftsteuer",
                "KD"   :   "Koerperschaft-Solidaritaetszuschlag",
                "QS"   :   "Quellensteuer",
                "QD"   :   "Quellen-Solidaritaetszuschlag",
                "GB"   :   "Gebuehren",
                "GW"   :   "Gewerbesteuer",
            }
            
        gebuehrenarten = {
                "ST"   :   "",
                "SZ"   :   ", Saeumniszuschlag",
                "MS"   :   ", Saeumniszuschlag",
                "VZ"   :   ", Verspaetungszuschlag",
                "MA"   :   ", Mahngebuehr",
                "PZ"   :   ", Mahngebuehr",
                "PF"   :   ", Mahngebuehr",
                "ZI"   :   ", Zinsen",
                "GS"   :   ", Gutschrift",
                "NZ"   :   ", Nachzahlungs-Zinsen",
                "EZ"   :   ", Erstattungszinsen",
                "VS"   :   " Vollstreckung",
                "MG"   :   ", Mahngebuehr",
                "GR"   :   ", Grundsteuerauskunft",
                "ZW"   :   " Zwangsgeld"
            }
                
        text = []
        for zeile in ktotext.split("\n"):

#            if "-erklaerung-" in zeile or gegenkonto0 in zeile or " 10-1510-15" in zeile:
            if "-auszahlung" in zeile or "-XX-" in zeile:
                text.append(zeile)
            elif re.search(r" 10-B.*? 10-B",zeile):
                text.append(zeile)
            elif re.search(r"-[A-Z][A-Z]\-[A-Z][A-Z]\-\d\d",zeile):
                continue
            else:
                text.append(zeile)
                  
        for zeile in open(files[0]).read().split("\n"):
        
            m = re.search(r"^(\d\d\d\d\d*) +([A-Z\-]+) +(\-?\d+\.\d\d)(.*)$",zeile)
#            print(zeile)
            if not m:
                continue
            datum     = m.group(1)
            
            if len(datum) == 4:
                datum = datum + "1230"
            if len(datum) == 6:
                datum = datum + "29"
            zeitraum  = datum[2:4]
            steuerart = m.group(2)
            betrag    = float(m.group(3))
            rest      = m.group(4)
            addrem    = ""
            m = re.search(r"(\d\d\d\d\d\d\d\d)(.*?) *$",rest)
            if m:
                datum  = m.group(1)
                addrem = m.group(2)
#            print(datum)
            gegenkonto = gegenkonto1
            if steuerart in ("LS-ST","LD-ST","LR-ST","LE-ST","LI-ST","LA-ST",
                             "LS-ZI","LD-ZI","LR-ZI","LE-ZI","LI-ZI","LA-ZI",
                             "LS-VZ","LD-VZ","LR-VZ","LE-VZ","LI-VZ","LA-VZ"):
                gegenkonto = gegenkonto0 + "-1503-bescheid" #+ zeitraum
            if steuerart in ("US-ST","US-ZI","US-VZ"):
                gegenkonto = gegenkonto0 + "-1502-bescheid" #+ zeitraum
            if steuerart in ("KS-ST","KD-ST","KS-ZI","KD-ZI","KS-VZ","KD-VZ"):
                gegenkonto = gegenkonto0 + "-1505-bescheid" #+ zeitraum
            if steuerart in ("GW-ST","GW-ZI","GW-VZ","GW-NZ","GW-EZ"):
                gegenkonto = gegenkonto0 + "-1506-bescheid" #+ zeitraum
            if steuerart in ("QS-ST","QD-ST","QS-ZI","QD-ZI","QS-VZ","QD-VZ"):
                gegenkonto = gegenkonto0 + "-1507-bescheid" #+ zeitraum
            zeile1 = datum + "  " + ("%3.2f" % -betrag) + "  -" + steuerart + "-" + zeitraum + "  " + gegenkonto
            zeile1 = zeile1 + "  0.00  " + steuerarten[ steuerart[0:2] ] + " 20" + zeitraum + gebuehrenarten[ steuerart[3:5] ]
            zeile1 = zeile1 + addrem
            text.append(zeile1)

        ktotext = "\n".join(text) + "\n"
        return(ktotext)
            
#*************************************************************************

    def xxparse_gewerbesteuer_fuerth (self,ktotext,files,gegenkonto0,gegenkonto1):

        if len(files) == 0:
            return()
            
        steuerarten = {
                "GW"   :   "Gewerbesteuer",
            }
            
        gebuehrenarten = {
                "ST"   :   "",
                "SZ"   :   ", Saeumniszuschlag",
                "VZ"   :   ", Verspaetungszuschlag",
                "ZI"   :   ", Zinsen",
                "VS"   :   " Vollstreckung",
                "ZW"   :   " Zwangsgeld"
            }
                

        text = []
        for zeile in ktotext.split("\n"):
            if "-erklaerung-" in zeile or gegenkonto0 in zeile:
                continue
            text.append(zeile)

        for file in files:
            for zeile in open(file).read().split("\n"):
                m = re.search(r"^ *\d\d\.\d\d\.\d\d +\d+ +\d+ +\d+ +(\d\d)\.(\d\d)\.(\d\d) +20(\d+) +\d+ +([A-Z]+) *(\S+).*? +(\S+) +(\S+) +(\-?[\d\.]+),(\d\d) *$",zeile)
                if not m:
                    continue
#                print(zeile)
                datum      = "20" + m.group(3) + m.group(2) + m.group(1)
                zeitraum   = m.group(4)
                steuerart  = "GW-" + m.group(5)
                betrag     = float(re.sub(r"\.","",m.group(9)) + "." + m.group(10))
                gegenkonto = gegenkonto1
                if steuerart in ("GW-GEWSTR","GW-GWSTVE","GW-GWSTNZ"):
                    gegenkonto = gegenkonto0 + "-1506-erklaerung-" + zeitraum
#                if steuerart in ("KS-ST","KD-ST"):
#                    gegenkonto = "11-1505-erklaerung-" + zeitraum
                zeile1 = datum + "  " + ("%3.2f" % -betrag) + "  -" + steuerart + "-" + zeitraum + "  " + gegenkonto
                zeile1 = zeile1 + "  0.00  " + "xxx" # steuerarten[ steuerart[0:2] ] + gebuehrenarten[ steuerart[3:5] ]
                text.append(zeile1)

        ktotext = "\n".join(text) + "\n"
        return(ktotext)
            
#*************************************************************************

    def xxparse_jahreswerte (self,ktotext,jahreswerte,konten):  #  not ktosafe

        text          = []
        ausschuettung = {}
        for zeile in ktotext.split("\n"):
            m = re.search(r"^(\d\d\d\d)(\d\d\d\d) +(\-?\d+\.\d\d) .* Ausschuettung",zeile)
            if m:
                ausschuettung[m.group(1)] = float(m.group(3))                
            elif re.search(r"\d\d\d\d\d\d\d\d ",zeile):
                continue
            text.append(zeile)

        x10 = konten[0]
        x11 = konten[1]
        x12 = konten[2]
        x13 = konten[3]
        x14 = konten[4]
        
        w10 = 0.00
        w11 = 0.00
        w12 = 0.00
        w13 = 0.00
        w14 = 0.00

        jahreswert = { x10: {}, x11: {}, x12: {}, x13: {} }
        for zeile in jahreswerte:
            m = re.search(r"\-(\d\d)\-([Z\d]\d\d\d).* (\-?\d+\.\d\d)",zeile)
            art    = m.group(1)
            jahr   = re.sub("Z","2",m.group(2))
            betrag = float(m.group(3))
            jahreswert[art][jahr] = betrag

        jahre = list( jahreswert[x10].keys() )
        jahre.sort() 
        for jahr in jahre:
        
            anfangsbestand = w12 + w13
        
            j10 = jahreswert[x10][jahr]
            j11 = jahreswert[x11][jahr]
            j12 = jahreswert[x12][jahr]
            j13 = jahreswert[x13][jahr]
            j14 = jahreswert[x14][jahr]
            
            w10 = w10 + j10
            w11 = w11 + j11
            w12 = w12 + j12
            w13 = w13 + j13
            w14 = w14 + j14

            gewinn = j12 + j13

            kapitalertragsteuer  = -0.15  * gewinn
            gewerbesteuer        = -0.035 * 3.9 * gewinn
            if jahr in ausschuettung:
                quellensteuer        =  0.25  * ausschuettung[jahr]
            else:
                quellensteuer        = 0.00
            kirchensteuer        = quellensteuer * 0.08
            soli_kapitalertragst = 0.055  * kapitalertragsteuer
            soli_quellensteuer   = 0.055  * quellensteuer
                    
#            text.append(jahr + "1240  " + ("%3.2f" % anfangsbestand)        +  
#                             "  -ERG      15-1200  0.00  Anfangsbestand")
#            text.append(jahr + "1241  " + ("%3.2f" % gewinn)                +  
#                             "  -ERG      15-1201  0.00  Jahresergebnis")
#            text.append(jahr + "1241  " + ("%3.2f" % (-endbestand))         +  
#                             "  -ERG      15-1201  0.00  Endbestand")
            text.append(jahr + "1242  " + ("%3.2f" % kapitalertragsteuer)  +  
                             "  -KAP-ST   " + x11 + "-1505  0.00  Koerperschaftsteuer")
            text.append(jahr + "1243  " + ("%3.2f" % soli_kapitalertragst) +  
                             "  -KAP-SL   " + x11 + "-1505  0.00  Soli Koerperschaftsteuer")
            text.append(jahr + "1244  " + ("%3.2f" % gewerbesteuer) +  
                             "  -GEW      " + x11 + "-1506  0.00  Gewerbesteuer")
            text.append(jahr + "1245  " + ("%3.2f" % quellensteuer) +  
                             "  -QUE-ST   " + x11 + "-1507  0.00  Quellensteuer")
            text.append(jahr + "1246  " + ("%3.2f" % soli_quellensteuer) +  
                             "  -QUE-SL   " + x11 + "-1507  0.00  Soli Quellensteuer")
            text.append(jahr + "1247  " + ("%3.2f" % kirchensteuer) +  
                             "  -QUE-KI   " + x11 + "-1507  0.00  Kirchen-Quellensteuer")
#            text.append(jahr + "1250  " + ("%3.2f" % extern)  +  
#                             "  -EXT      99-EXT  0.00  Abweichung")

            abweichung = ( kapitalertragsteuer + soli_kapitalertragst + gewerbesteuer +
                           quellensteuer + soli_quellensteuer + kirchensteuer )
                           
            diff = endbestand + abweichung
            
            text.append(jahr + "1250  " + ("%3.2f" % (abweichung)) +  
                             "  -ABW   10-7000-cgabriel  0.00  externe Zahlungen")
            text.append(jahr + "1251  " + ("%3.2f" % (-abweichung)) +  
                             "  -ABW   99  0.00  externe Konten und Buchhaltungen")

        ktotext = "\n".join(text) + "\n"
        return(ktotext)
            
#*************************************************************************

    def xxparse_jahreswerte1 (self,ktotext,jahreswerte):  #  not ktosafe

        j    = {}
        text = []

        jahreswerte.sort()
        for zeile in jahreswerte:
            m = re.search(r"\-([Z\d]\d\d\d)\-(\d\d).* (\-?\d+\.\d\d)",zeile)
            if m:
                j[m.group(2)] = float(m.group(3))

        jk   = list(j.keys())
        jk.sort()
        jk   = jk[0:5]
        jahr = re.sub(r"^Z","2",os.path.relpath("..","../.."))

        ausschuettung = {}
        for zeile in ktotext.split("\n"):    #   Korrektur der Aktiva, Passive, Ertrag, Aufwand anbringen ...
            if not re.search(r"^(\d\d\d\d\d\d\d\d) ",zeile):
                text.append(zeile)
            else:
                m = re.search(r"^(\d\d\d\d\d\d\d\d) +(\-?\d+\.\d\d) +\-(\S+) +(\d\d)(\S*)",zeile)
                if m:
                    if m.group(4) in jk:
                        jahr   = m.group(1)[0:4]
                        betrag = float(m.group(2))
                        kto    = m.group(4)
                        j[kto] = j[kto] + betrag
                    m = re.search(r"7000-([a-z]+)$",m.group(5))
                    if m:
                        print(betrag,m.group(1))
                        ausschuettung[m.group(1)] = abs(betrag)

        j10 = j[jk[0]]
        j11 = j[jk[1]]
        j12 = j[jk[2]]
        j13 = j[jk[3]]
        j14 = j[jk[4]]
        
        extern = j10 + j11 + j12 + j13 
        text.append(jahr + "1250  " + ("%3.2f" % -extern)  +  "  -ST      99                  0.00  extern verbucht")
        text.append(jahr + "1250  " + ("%3.2f" %  extern)  +  "  -ST      " + jk[0] + "-7000-cgabriel-extern  0.00  extern verbucht")

        j10 = j10 - extern

        gewinn = min(0,j12 + j13)

        jj  = "-"+jahr[2:4]
        erg = 0.15  * gewinn
        text.append(jahr + "1251  " + ("%3.2f" %  erg)  +  "  -ST   " + jk[4] + "-01_kpst  0.00  Koerperschaftsteuer")
        text.append(jahr + "1251  " + ("%3.2f" % -erg)  +  "  -ST   " + jk[1] + "-1505-berechnung"+jj+"  0.00  Koerperschaftsteuer")
        j14 = j14 - erg
        j11 = j11 + erg
        
        erg = 0.055 * erg
        text.append(jahr + "1252  " + ("%3.2f" %  erg)  +  "  -ST   " + jk[4] + "-02_kpst_soli  0.00  Soli Koerperschaftsteuer")
        text.append(jahr + "1252  " + ("%3.2f" % -erg)  +  "  -ST   " + jk[1] + "-1505-berechnung"+jj+"  0.00  Soli Koerperschaftsteuer")
        j14 = j14 - erg
        j11 = j11 + erg
        
        erg = 0.035 * 3.9 * gewinn
        text.append(jahr + "1253  " + ("%3.2f" %  erg)  +  "  -ST   " + jk[4] + "-03_gewst               0.00  Gewerbesteuer")
        text.append(jahr + "1253  " + ("%3.2f" % -erg)  +  "  -ST   " + jk[1] + "-1506-berechnung"+jj+"    0.00  Gewerbesteuer")
        j14 = j14 - erg
        j11 = j11 + erg
        
        erg = 0.00
        for gesellschafter in ausschuettung:
            betrag = ausschuettung[gesellschafter]
            text.append(jahr + "1254  " + ("%3.2f" % -betrag)  +  "  -ST      " + jk[4] + "-04_ausschuet "  +
                                                 "  0.00  Ausschuettung " + gesellschafter)
            text.append(jahr + "1254  " + ("%3.2f" %  betrag)  +  "  -ST      " + jk[0] + "-7000-" + gesellschafter +
                                                 "  0.00  Ausschuettung " + gesellschafter)
            j14 = j14 + betrag
            j10 = j10 - betrag
            erg = erg + betrag 

        erg = -erg
 
        if abs(erg) > 0.0001:

            erg = 0.25 * erg
            text.append(jahr + "1255  " + ("%3.2f" %  erg)  +  "  -ST   " + jk[4] + "-05_qst           0.00  Quellensteuer")
            text.append(jahr + "1255  " + ("%3.2f" % -erg)  +  "  -ST   " + jk[1] + "-1507-berechnung  0.00  Quellensteuer")
            j14 = j14 - erg
            j11 = j11 + erg
    
            erg1 = 0.055 * erg
            text.append(jahr + "1256  " + ("%3.2f" %  erg1)  +  "  -ST   " + jk[4] + "-06_qst_soli      0.00  Soli Quellensteuer")
            text.append(jahr + "1256  " + ("%3.2f" % -erg1)  +  "  -ST   " + jk[1] + "-1507-berechnung  0.00  Soli Quellensteuer")
            j14 = j14 - erg1
            j11 = j11 + erg1
    
            erg2 = 0.08 * erg
            text.append(jahr + "1257  " + ("%3.2f" %  erg2)  +  "  -ST   " + jk[4] + "-07_qst_kist      0.00  Kirchen-Quellensteuer")
            text.append(jahr + "1257  " + ("%3.2f" % -erg2)  +  "  -ST   " + jk[1] + "-1507-berechnung  0.00  Kirchen-Quellensteuer")
            j14 = j14 - erg2
            j11 = j11 + erg2

        gewinn_nach_steuern = j12 + j13 + j14

        text.append(jahr + "1258  " + ("%3.2f" % -gewinn_nach_steuern)  +  "  -" + jahr[2:4] + "  " + jk[1] + "-1805  0.00  Gewinn")
        j11 = j11 + gewinn_nach_steuern
#        print(j10,j11,j12,j13,gewinn_nach_steuern)

        ktotext = "\n".join(text) + "\n"
        return(ktotext)
            
#*************************************************************************

    def xxparse_jahressteuern (self,ktotext,jahreswerte,konten):  #  not ktosafe

        text          = []
        ausschuettung = {}
        for zeile in ktotext.split("\n"):
            m = re.search(r"^(\d\d\d\d)(\d\d\d\d) +(\-?\d+\.\d\d) .* Ausschuettung",zeile)
            if m:
                ausschuettung[m.group(1)] = float(m.group(3))                
            elif re.search(r"\d\d\d\d\d\d\d\d ",zeile):
                continue
            text.append(zeile)

        x11 = konten[0]
        x12 = konten[1]
        x13 = konten[2]

        jahreswert = { x12: {}, x13: {} }
        for zeile in jahreswerte:
            print(zeile)
            m = re.search(r"\-(\d\d)\-([Z\d]\d\d\d).* (\-?\d+\.\d\d)",zeile)
            art    = m.group(1)
            jahr   = re.sub("Z","2",m.group(2))
            betrag = float(m.group(3))
            jahreswert[art][jahr] = betrag

        jahre = list( jahreswert[x12].keys() )
        jahre.sort() 
        for jahr in jahre:
        
            gewinn               = jahreswert[x12][jahr] + jahreswert[x13][jahr]
            kapitalertragsteuer  = -0.15  * gewinn
            gewerbesteuer        = -0.035 * 3.9 * gewinn
            if jahr in ausschuettung:
                quellensteuer        =  0.25  * ausschuettung[jahr]
            else:
                quellensteuer        = 0.00
            kirchensteuer        = quellensteuer * 0.08
            soli_kapitalertragst = 0.055  * kapitalertragsteuer
            soli_quellensteuer   = 0.055  * quellensteuer
            text.append(jahr + "1242  " + ("%3.2f" % kapitalertragsteuer)  +  
                             "  -KAP-ST   " + x11 + "-1505  0.00  Koerperschaftsteuer")
            text.append(jahr + "1243  " + ("%3.2f" % soli_kapitalertragst) +  
                             "  -KAP-SL   " + x11 + "-1505  0.00  Soli Koerperschaftsteuer")
            text.append(jahr + "1244  " + ("%3.2f" % gewerbesteuer) +  
                             "  -GEW      " + x11 + "-1506  0.00  Gewerbesteuer")
            text.append(jahr + "1245  " + ("%3.2f" % quellensteuer) +  
                             "  -QUE-ST   " + x11 + "-1507  0.00  Quellensteuer")
            text.append(jahr + "1246  " + ("%3.2f" % soli_quellensteuer) +  
                             "  -QUE-SL   " + x11 + "-1507  0.00  Soli Quellensteuer")
            text.append(jahr + "1247  " + ("%3.2f" % kirchensteuer) +  
                             "  -QUE-KI   " + x11 + "-1507  0.00  Kirchen-Quellensteuer")

        ktotext = "\n".join(text) + "\n"
        print(ktotext)
        return(ktotext)
            
#********************************************************************************

    def xxparse_sv_meldunge1 (self,ktotext,files,kknr,kk,st=1.0):

        ktotext = self.parse_sv_meldunge(ktotext,files,kknr,kk,st)
        
        ktotext = re.sub(r"  11-",     "  11-C13-3740-", ktotext,99999999)
        ktotext = re.sub(r"  10-1510-","  11-C13-3759-", ktotext,99999999)
        
        return(ktotext)



#********************************************************************************

    def xxidem_kto (self,ktotext,grenze=0.99,maxdiff=99999999,group_matrix0={}):



        group_matrix = { 1:99999999, 2:1000, 3:120, 4:50, 5:30, 6:24, 7:20, 8:18, 9:17, 10:16,
                             11:15,  12:16, 13:15, 14:15, 15:15 }

#        group_matrix = { 1:99999999, 2:1000, 3:50, 4:20, 5:10, 6:8, 7:7 }

        for i in group_matrix0:
            group_matrix[i] = group_matrix0[i]

        text      = []
        buchungen = []
        groups    = [buchungen]
          
        for zeile in ktotext.split("\n"):

            m = re.search(r"^(\d\d\d\d\d\d\d\d) +(\-?\d+\.\d\d) +(\S+) +(\S+) +(\-?\d+\.\d\d) +(.*)",zeile)
            if not m:
                text.append(zeile)
            else:
                datum   = m.group(1)
                betrag  = m.group(2)
                ktoa    = m.group(3)
                ktob    = m.group(4)
                remark  = m.group(6)
                m       = re.search(r"^(.*)\-(\d\d\d\d\d)$",ktoa)
                if m:
                    buchungen.append([0,datum,betrag,m.group(1),ktob,remark])
                    day0 = datetime.datetime.strptime("19700101","%Y%m%d")
                    if datum[4:6] == "02":
                        tag = min(28,int(datum[6:8]))
                    else:
                        tag = min(30,int(datum[6:8]))
                    day  = datetime.datetime.strptime(datum[0:6]+("%02u"%tag),"%Y%m%d")
                    buchungen[-1][0] = (day-day0).days
                else:
                    text.append(zeile)

        buchungen.sort(key=lambda x: x[0])            
        pointer = []
        maxlen  = len(buchungen)-1
        self.mark("")

        while (0 == 0):
        
            maxlen   = min(maxlen,len(buchungen)-1)
            pointer0 = pointer[:]
            pointer  = self.next_pointer(pointer,maxlen)
            if not pointer:
                break
                
            
            #  Zusatzpruefung: Die Buchungen der pointer duerfen nicht zu weit auseinanderliegen
            if len(pointer) > 0:
                maxlen   = min(pointer[0] + len(pointer),len(buchungen)-1)
                while (0 == 0):
                    if maxlen == len(buchungen)-1:
                        break
                    if buchungen[maxlen+1][0] - buchungen[pointer[0]][0] > maxdiff:
                        break
                    maxlen = maxlen+1
            #  Zusatzpruefung ENDE
                
            if not len(pointer0) == len(pointer):
                self.mark("        ... searching " + str(len(pointer)) + "-tuples in " + str(len(buchungen)) + " rows")
                
            if len(buchungen) >  group_matrix [len(pointer)]:
                print("        ... skip")
                break

            sum     = 0.00
            for i in pointer:
#                try:
                    sum = sum + float(buchungen[i][2])
#                except:
#                    sum = 999.99
#                    break

            if abs(sum) > grenze:
                continue

            zaehler = 0
            group   = []
            for i in pointer:
                group.append(buchungen[i-len(group)])
                del buchungen[i-len(group)+1]
                pointer[zaehler] = pointer[0] + zaehler
                zaehler = zaehler + 1
            pointer[-1] = pointer[-1] - 1
            groups.append(group)
            
        last_group = ""
        if len(buchungen) == 0:
            groups.remove(buchungen)            
        else:
            last_group = groups[0]
        groups.sort(key=lambda x:  x[0][0]  )

        zaehler = {}
        for group in groups:
            id = None
            if len(group) == 2:
                buchung1 = group[0]
                buchung2 = group[1]
                betrag1  = buchung1[2]
                betrag2  = buchung2[2]
                if abs(float(betrag1) + float(betrag2)) <= grenze:
                    id = self.ukto_from_betrag(betrag1)  #  es kann 2er Gruppen geben, die sich nicht auf 0 addieren!
            if id == None:
                ll = len(group)
                if not ll in zaehler:
                    zaehler[ll] = 0
                zaehler[ll] = zaehler[ll] + 1
                id = "0" + str(ll)
                id = id + ("%0" + str(5-len(id)) + "u") % zaehler[ll]
            
            if group == last_group:
                id = "99999"
            
            for buchung in group:
                text.append(buchung[1] + " " + buchung[2] + " " + buchung[3] + "-" + id + " " +
                            buchung[4] + "  0.00  " + buchung[5])
                
                            
        return( '\n'.join(text) + '\n' + str(time.perf_counter()) )

#********************************************************************************

    def xxquittungen_reverse (self,ktotext):
    
        text = []
        for zeile in ktotext.split("\n"):
            
            if re.search(r"\-qu-\d\d\d\d\d ",zeile) and not "-qu-99999 " in zeile:
                m = re.search(r"^(\d\d)(\d\d\d\d\d\d) +\-?(\d+\.\d\d) +(\S+) +(\S+) +(\-?\d+\.\d\d) +(\+\+|\+\-|)(.*) *$",zeile)
                if m:
                    dateiname = m.group(2) + "*" + re.sub("\.","_",m.group(3)) + "*" + m.group(8) + "*"
                else:
                    print("Wrong line.", zeile)
                    continue
                dateiname = glob.glob(dateiname)
                for d in dateiname:
                    text.append("mv " + d + " $1")
                
        return("\n".join(text))
                
#********************************************************************************
            
    def xxnext_pointer (self,pointer,maxlen):
    
        if len(pointer) > maxlen:   #   hier ist nichts mehr zu machen, es gibt keinen hoeheren Index
            return(None)

        if len(pointer) > 0:

            if pointer[-1] < maxlen:            #   erst sehen, ob der letzte Index problemlos erhoeht werden kann
                pointer[-1] = pointer[-1] + 1
                return(pointer)
                
            pointer = self.next_pointer(pointer[:-1],maxlen-1)   #   wenn das nicht geht, das zweithoechste Teilstueck erhoehen
            if len(pointer) > 0:
                pointer.append(pointer[-1]+1)   #  dann den letzten Index erhoehen
                if not pointer[-1] > maxlen:    #  wenn der noch passt, fertig
                    return(pointer)

        zaehler = 0          #   ansonsten die Gesamtlange des Pointers um 1 erhoehen
        for i in (pointer):
            pointer[zaehler] = zaehler
            zaehler          = zaehler + 1
        pointer.append(zaehler)
        
        return(pointer)                    
        
        
#********************************************************************************

    def xxassign_quittungen (self,daydiff1=9999999,ktotext="",valid_konten=None):

        text  = ""
        text5 = ""
#        text =        "mkdir 5555\n"
#        text = text + "mkdir 5559\n\n"
        dir  = "."
        
        valid_konten = valid_konten.split(",")
#        print (valid_konten)
        
        ktotext1 = []
        for zeile in ktotext.split('\n'):
            m = re.search('^(\d\d\d\d\d\d\d\d) +(\-?\d+\.\d\d) +\-(\S+?) +\-(\S+) +(\-?\d+\.\d\d) +(.*)', zeile)
            if m:
                ktoa = m.group(3)
                ktob = m.group(4)
                if ktoa in valid_konten or ktob in valid_konten:
                    ktotext1.append(zeile)
        ktotext = "\n".join(ktotext1) + "\n"
#        for o in ktotext1:
#            print(o)

        for rechn in (glob.glob(dir + "/*/*.pdf")):

#            text = text + "\n" + "# " + rechn + "\n"

            self.stunden  = None
            self.betraege = None
            self.mitarb   = None
            erg           = self.analyze(rechn)

            m = re.search(r"^.*?[\\\/](\d\d\d\d\d\d)\.(qq|qw|)\_*(\d+)\_+(\d\d)\_+(.*)\.pdf","/"+rechn)

            if m:
                datum7  = m.group(1)
                ust7    = m.group(2)
                betrag7 = m.group(3) + "." + m.group(4)
                remark7 = m.group(5)

                if erg:
                    if not erg[2] == datum7 or not float(erg[0]) == float(betrag7):
                        print ("WARNING: " + ("%13.2f"%float(erg[0])) + "  " + erg[1] + "  " + erg[2] + "  " + rechn)

            else:
                datum7  = ""
                ust7    = ""
                betrag7 = ""
                remark7 = ""

            datum1 = datum7
            ust    = ust7
            betrag = betrag7

            if datum1 == "" and erg:
            
                datum1 = erg[2]
                ust    = erg[1]  #  re.sub(r"q","+",re.sub(r"w","-",erg[1],9),9)
                betrag = erg[0]
                
                if valid_konten == None:
                    if len(ust) > 0:
                        ust = ust + "_"
                    rechn1   = re.sub(r"\.pdf$",".ocr",rechn)
                    text9    = open(rechn1).read()
                    addtext  = str( base64.urlsafe_b64encode(hashlib.md5(text9.encode("utf8")).digest()),"ascii" )
                    filename = datum1 + "." + ust + re.sub(r"\.","_","%3.2f"%float(betrag)) + "__" + addtext[0:6].lower()
                    os.rename(rechn,filename+".pdf")
                    try:
                        os.rename( re.sub(r"\.pdf$",".ocr",rechn) ,filename+".ocr")
                    except:
                        pass
                    print(filename)
                    continue
                    
            if valid_konten == None:
                continue


            if datum1 == "":
                continue

            if len(ust) > 0:
                ust = ust + "_"
            if len(datum1) < 8:
                datum1 = "20" + datum1
                
            if remark7 == "":
                remark7 = re.sub(r"^(.*)[\\\/](.*)(\.pdf)$","\\2",rechn)
            
            text5 = (text5 + "mv " + rechn + " " + datum1[2:] + "." + ust + re.sub(r"\.","_",betrag) + 
                 "__" + re.sub(r"^([a-zA-Z]+)(.*)$","\\1\\2",remark7) + 
                 ".pdf\n")
            text5 = (text5 + "mv " + re.sub(r"\.pdf$",".ocr",rechn) + " " + datum1[2:] + "." + ust + re.sub(r"\.","_",betrag) + 
                 "__" + re.sub(r"^([a-zA-Z]+)(.*)$","\\1\\2",remark7) + 
                 ".ocr\n")
            if int(datum1[4:6]) > 31:
                datum1 = datum1[0:4] + "30"
            
#            text = text + "# " + datum1 + "  " + ("%13.2f" % float(betrag)) + "\n"

            m = re.search(r"^(.*?\n)("+datum1[0:4]+".*$)",ktotext,re.DOTALL)  # hier noch moegliche Buchungssaetze mit suchen
            if m:
                ktotext1 = m.group(2)
            else:
                ktotext1 = ktotext
#            if abs(float(betrag)) == 357.00:
#                print("*****************************",ktotext1[:10000],"******************************")
           
            betrag2 = "%3.2f" % float(betrag)
            for zeile in ktotext1.split('\n'):
                m = re.search('^(\d\d\d\d\d\d\d\d) +(\-?\d+\.\d\d) +\-(\S+?) +\-(\S+) +(\-?\d+\.\d\d) +(.*)', zeile)
                if m:
                    datum2  = m.group(1)
                    betrag2 = ("%3.2f" % abs(float(m.group(2))))
                    remark2 = m.group(6)
                    ktoa    = m.group(3)
                    ktob    = m.group(4)
                else:
                    continue
#                if int(datum2) < int(datum1):
#                    continue
                if (ktoa in valid_konten or ktob in valid_konten) and betrag == betrag2:

#                    text = text + "# " + zeile + "\n"
                    if datum7 == "":
                        original_text = re.sub(r"\.pdf$","",rechn)
                        original_text = re.sub(r"^(.*)\.","",original_text)
                        ust3          = ""
                    else:
                        original_text = remark7 + "__"
                        ust3          = ust7

                    m2      = re.search(r"^([\+\-]*)(.*)$",remark2)
                    if   m2.group(1) == "++" or ust3 == "qq":
                        ust = "qq_"
                    elif m2.group(1) == "+-" or ust3 == "qw":
                        ust = "qw_"
                    remark2 = original_text + "__" + m2.group(2)
                    if not datum1 == datum2:
                        remark2 = datum1[2:] + "_" + remark2
                    
                    remark3 = self.normalize_text(remark2,"extended")[0:100]
                    betrag3 = re.sub(r"\.","_",betrag2)

                    daydiff = abs(self.days_since_1970(datum2) - self.days_since_1970(datum1))
                    section = "a"
                    if daydiff > 5:
                        section = "b"
                    if daydiff > 10:
                        section = "c"
                    if daydiff > 30:
                        section = "d"
                    if daydiff > 100:
                        section = "e"
                    
                    cc = ""
#                    if not section == "a":
#                        cc = "# "
                    section = ""
                                            
                    if daydiff < int(daydiff1):
#                        text  = text + "# " + datum2 + "  " + ("%13.2f" % float(betrag)) + "  " + remark3 + "\n"
                        text1 = rechn + "  $1" + section + "/" + datum2[2:] + "." + ust + betrag3 + "__" + remark3 + ".pdf "
                        text1 = cc + "mv " + text1 + "\n" # + cc + "mv " + rechn + "  5556" + section + "\n"
                        text  = text + text1
                        text1 = re.sub(r"\.pdf ",".ocr ",text1,9999)
                        text  = text + text1

#                        text  = text + "mv " + re.sub(r"\.pdf$",".*",rechn,9999) + " $1\n"
                    break
                        
        return(text+text5)
        
#********************************************************************************

    def xxdays_since_1970 (self,datum):

        day0 = datetime.datetime.strptime("19700101","%Y%m%d")
        if not len(datum) == 8:
            return(0)

        if datum[4:6] == "02":
            tag = min(28,int(datum[6:8]))
        else:
            tag = min(30,int(datum[6:8]))
        tag = max(1,int(datum[6:8]))
        try:
            day  = datetime.datetime.strptime(datum[0:6]+("%02u"%tag),"%Y%m%d")
            datumnr = (day-day0).days
            return(datumnr)
        except:
            return(0)

#********************************************************************************

    def xxrechnungen2018a (self,ktotext,company,dir="."):
    
        ktotext = self.rechnungen2018(ktotext,company)
        ktotext = re.sub(r" 12-8400"," 12-D1a-4400",ktotext)
        return(ktotext)

#********************************************************************************

    def xxrechnungen2013a (self,ktotext,company,dir="."):
    
        ktotext = self.rechnungen2013(ktotext,company)
        ktotext = re.sub(r" 12-8400"," 12-D1a-4400",ktotext)
        return(ktotext)

#********************************************************************************

    def xxrechnungen2013 (self,ktotext,company,dir="."):

        text      = []
        buchungen = {}
        ukto      = ""

        for zeile in ktotext.split("\n"):
            if ukto == "":
                m = re.search(r"^(\S+) +\(.*?\)",zeile)
                if not m:
                    m = re.search(r"\^(\S+)",zeile)
                if m:
                    ukto = m.group(1)
                else:
                    print("No ukto could be identified. There should be a ^pattern inside.")
                    return(ktotext)
        
            if not "Rechnung" in zeile or "manuell" in zeile or "Rueckzahlung" in zeile or "GUTSCHRIFT" in zeile:
                text.append(zeile)

        for rechn in (glob.glob(dir + "/*.pdf")):

            if "nterschrieben" in rechn or "ndenzettel" in rechn or "NOTVALID" in rechn or "EXCLUDE§" in rechn:
                continue
            
            self.stunden  = None
            self.betraege = None
            self.mitarb   = None
            erg           = self.analyze(rechn)
#            if "GULP" in self.text or "rogressive" in self.text:
#                self.text = re.sub(r"HAYS","",self.text,9999,re.IGNORECASE)

            if erg:
                datum1 = erg[2]
                ust    = re.sub(r"q","+",re.sub(r"w","-",erg[1],9),9)
                betrag = erg[0]
                proj   = ""
                if self.mitarb:
                    o = list(self.mitarb.keys())[0]
                else:
                    o = "unknown"
                if self.stunden:
                    o1 = list(self.stunden.keys())[0]
                    o  = o + " " + o1
                    if float(o1.split(" ")[0]) < 0.02:
                        betrag = 0.00
#                    m = re.search(r"\/ *(.*?)(\.|$)",self.stunden.keys()[0])
#                    if m:
#                        proj = "-" + m.group(1)
                m  = re.search(r"^(.*)[\\\/](.*)\.pdf$",rechn)
                if m:
                    o = o + ", " + m.group(2)
                if int(datum1[4:6]) > 31:
                    datum1 = datum1[0:4] + "30"
                
                text.append("20"+datum1 + "  " + str(betrag) + "  " + ukto + "-11111  12-8400-" +
                              company + "  0.00 " + ust + o + company)

#                betrkto = "-" + self.ukto_from_betrag(betrag)
#                buchungen["20"+datum1[0:4]+betrkto] = (
#                   ["20"+datum1,betrag,"-11111","12-8400-"+company,"0.00",ust+o+", "+company])

                

#           m = re.search(r"^(\d\d\d\d\d\d\d\d) +(\-?\d+\.\d\d) +(\S+) +(\S+) +(\-?\d+\.\d\d) +(.*)",zeile)
#           if not m:
#               text.append(zeile)
#           else:
#               datum   = m.group(1)
#               betrag  = m.group(2)
#               ktoa    = m.group(3)
#               ktob    = m.group(4)
#               remark  = m.group(6)
#               betrkto = "-" + self.ukto_from_betrag(betrag)
#               buchungen[datum[0:6]+betrkto] = [datum,betrag,ktoa,ktob,"0.00",remark]

        for buchung in buchungen.values():
            text.append("  ".join(buchung))
                
        return( "\n".join(text) + "\n")
        
#**********************************************************************            

    def xxrechnungen2018 (self,ktotext,company,dir="."):

        text      = []
        buchungen = {}

        for zeile in ktotext.split("\n"):
            if not "Rechnung" in zeile or "manuell" in zeile:
                text.append(zeile)

        for rechn in (glob.glob(dir + "/*.md")):


            text1 = open(rechn).read()
            m     = re.search(r"^(.*)(\d\d)\.(\d\d)\.(\d\d\d\d)(.*?)Rechnung +(\d\d\d\d\-\d\d\d)(.*?)Gesamtbetrag +von +(\d+)[\.\,](\d\d) +bis",text1,re.DOTALL)
            if m:
                text.append(m.group(4)+m.group(3)+m.group(2) + "  " + m.group(8) + "." + m.group(9) +
                                 "  -11111  12-8400-" + company + "  0.00  ++Rechnung Kistler " +
                                                     m.group(6) + "  " + m.group(3) + "/" + m.group(4))
        return( "\n".join(text) + "\n")
        
#******************************************************************************

    def xxplan (self,ktotext,templates):
    
        templates = templates + "\n99999999  i  z  x  x  x\n\n"
        templates = re.sub(r"\.\.\.",".  .  .  .  .",templates,99999999)
        text = ""
 
        jm   = ""
        z    = 0
        for zeile in templates.split("\n"):
        
            i = 1
            m = re.search(r"^(\d\d\d\d\d\d)(\d\d) +(\S+) +(\S+) +(\S+) +(\S+) +(.*)$",zeile)
            if not m:
                continue
                
            jm1      = m.group(1)
            day1     = m.group(2)
            
            zformel1 = m.group(3)
            if zformel1 == ".":
                zformel1 = zformel
            bformel1 = m.group(4)
            if bformel1 == ".":
                bformel1 = bformel
            
            ktoa1    = m.group(5)
            if ktoa1 == ".":
                ktoa1 = ktoa
            ktob1    = m.group(6)
            if ktob1 == ".":
                ktob1 = ktob
            
            remark1  = m.group(7)
            if remark1[0] == ".":
                remark1 = remark
            
            if not jm == "":
                
                while (0 == 0):
                 
                    z      = eval(zformel)
                    betrag = eval(bformel)
                    rem    = re.sub(r"-z-",str(z),remark,9999)
                    text = text + jm + day + "  " + ("%3.2f"%betrag) + "  " + ktoa + "  " + ktob + "  0.00  " + rem + "\n"
                    
                    if not (ktoa == ktoa1 and ktob == ktob1):
                        break
                        
                    if jm1 == jm:
                        break

                    monat = jm[4:6]
                    if monat == "12":
                        jm = str(int(jm[0:4])+1) + "01"
                    else:
                        jm = jm[0:4] + ("%02u"%(int(monat)+1))
#                    print("JJJJ",jm,jm1)
                    i = i + 1
                        
            jm      = jm1
            day     = day1
            zformel = zformel1
            bformel = bformel1
            ktoa    = ktoa1
            ktob    = ktob1
            remark  = remark1
            z0      = z            
                
        return(text)


#******************************************************************************

    def xxplan (self,ktotext,vars,templates):
    
        templates = re.sub(r"\.\.\.",".  .  .  .  .",templates+"\n",99999999)
        text = ""
 
        for var in vars:
            o         = vars[var]
            templates = re.sub("-"+var+"-",o,templates,99999999)
            try:
                o = self.add_month([o,1])
                templates = re.sub("-\."+var+"-",o,templates,99999999)
            except:
                pass

        jm   = ""
        z    = 0
        for zeile in templates.split("\n"):
        
            i   = 1
            jms = 0
            m   = re.search(r"^(\d\S+) +(\d\d) +(\S+) +(\S+) +(\S+) +(\S+) +(.*)$",zeile)
#            print("..",zeile)
            if not m:
                m   = re.search(r"^20(\d\d\d\d)(\d\d) +(\S+) +(\S+) +(\S+) +(\S+) +(.*)$",zeile)
                jms = 1
                if not m:
                    continue

#            print(">>",zeile)
            if jms == 0:
                jms = m.group(1)
            else:
                jms = m.group(1) + "-" + m.group(1)
            if not "+" in jms:
                jms = jms + "+0"    
                
            day     = m.group(2)
            
            zformel = m.group(3)
            if zformel == ".":
                zformel = zformel0
            bformel = m.group(4)
            if bformel == ".":
                bformel = bformel0
            
            ktoa    = m.group(5)
            if ktoa == ".":
                ktoa = ktoa0
            ktob    = m.group(6)
            if ktob == ".":
                ktob = ktob0
            
            remark  = m.group(7)
            if remark[0] == ".":
                remark = remark0
            
            m = re.search(r"^(\d+)\-(\d+)\+(\d+)$",jms)
            if m:
                jm0    = [m.group(1),m.group(3)]
                jm_end = "20" + self.add_month([m.group(2),m.group(3)]) + day

                i = 0
                while (0 == 0):
            
                    jm     = "20" + self.add_month(jm0) + day
                    z      = eval(zformel)
                    betrag = eval(bformel)
                    rem    = re.sub(r"-z-",str(z),remark,9999)
                    text = text + jm + "  " + ("%3.2f"%betrag) + "  " + ktoa + "  " + ktob + "  0.00  " + rem + "\n"
                    
                    if jm == jm_end:
                        break

                    jm0[1] = int(jm0[1]) + 1 
                    i      = i + 1
                        
            jms0     = jms
            day0     = day
            zformel0 = zformel
            bformel0 = bformel
            ktoa0    = ktoa
            ktob0    = ktob
            remark0  = remark
            z0       = z            
                
        return(text)


#******************************************************************************

    def xxadd_month (self,jm0):
    
        jahr  = int(jm0[0][0:2])
        monat = int(jm0[0][2:4])
        diff  = int(jm0[1])
        
        while (0 == 0):
            if diff == 0:
                break
            if monat == 12:
                jahr  = jahr + 1
                monat = 1
            else:
                monat = monat + 1
            diff = diff - 1
        
        erg = ("%02u"%jahr) + ("%02u"%monat)
        return(erg)


#******************************************************************************

    def xxanalyze (self,beleg):
    
        belegfile = re.sub(r"^(.*)\.pdf$","\\1",beleg)
        try:
            text = open(belegfile+".ocr").read()
        except:
            return()
            
        self.datum    = {}
        self.ust      = ""
        self.mitarb   = {}
        self.betraege = {}
        self.stunden  = {}
        self.stsatz   = {}
        self.remark   = { "xx" : 1 }
            
        datum2 = ""
        m = re.search(r"^(.*)[\\\/](.*)$",belegfile)
        if m:
            filename = m.group(2)
        else:
            filename = ""

        text = re.sub(r"(\d+)\.(\d\d\d),(\d\d)","\\1\\2,\\3",text,9999)

        self.text     = text
        
        while (0 == 0):    #   Ermittlung der Stunden
            m = re.search(r"^(.*?\D)(\d[\d+\.]*) +Stunden (.*)$",text,re.DOTALL)
            if not m:
                break
            m1     = re.search(r"\D([\d\.\,]+)\D",m.group(3)[0:40])
            stsatz = ""
            if m1:
                stsatz = re.sub(r",",".",m1.group(1))
            self.stunden[m.group(2)+" / "+stsatz] = 1
            text = m.group(1) + m.group(3)

#        print belegfile,filename
        m = re.search(r"[\\\/](\d?\d?)(\d\d\d\d\d\d)\_?(\D+)\_?","/"+filename)     #  Ermittlung des Datums
        if m:
            self.datum[m.group(2)] = 1
            self.remark[re.sub(r"\.","",m.group(3))] = 1
        else:
            m = re.search(r"[\\\/](\d\d)(\d\d)(\d\d)\.([a-z]+)\_(\D+)\_?","/"+filename)
            if m:
                self.datum["20" + m.group(3) + m.group(2) + m.group(1)] = 1
                self.mitarb[m.group(4)] = 1
                self.remark[m.group(5)] = 1
        if not m:
            self.datum = {}
            while (0 == 0):
                m = re.search(r"^(.*?[^\.\,0123456789])(\d\d?)[\.\-](\d\d?)[\.\-](\d?\d?)(\d\d)([^\.\,0123456789].*)$",text,re.DOTALL)
                if not m:
                    break
                self.datum[m.group(5)+("%02u"%int(m.group(3)))+("%02u"%int(m.group(2)))] = 1
                text = m.group(1) + m.group(6)

        while (0 == 0):    #  Ermittlung aller Betraege bzw. alles dessen, was nur annaehernd wie ein Betrag aussieht
            m = re.search(r"^(.*?[^\.\,0123456789])(\d+)[\,\.](\d\d)0?([^\.\,0123456789].*)$",text,re.DOTALL)
            if not m:
                break
            betrag = m.group(2)+"."+m.group(3)
            if float(betrag) > 0.00001:
                self.betraege[betrag] = {"b":1}
            text = m.group(1) + m.group(4)

        while (0 == 0):
            m = re.search(r"^(.*?)(Stundenaufstellung[^\n]*?, +|Name: +)(\S+).*? (\S+)(\D.*)$",text,re.DOTALL)
            if not m:
                break
            o = (m.group(3)[0] + m.group(4)).lower()
            o = re.sub("oime","onne",o)
            o = re.sub(r"^ss",m.group(3)[0:2].lower()+"s",o)
            self.mitarb[o] = 1
            text = m.group(1) + m.group(5)

        for betrag in self.betraege:
            for betrag1 in self.betraege:
                if   "%3.2f" % (float(betrag) / float(betrag1)) == "1.07":
                    self.betraege[betrag]["m"] = 1
                elif "%3.2f" % (float(betrag) / float(betrag1)) == "1.19":
                    self.betraege[betrag]["n"] = 1
                elif "%3.2f" % (float(betrag1) / float(betrag) * 1.07) == "0.07":
                    self.betraege[betrag]["v"] = 1
                elif "%3.2f" % (float(betrag1) / float(betrag) * 1.19) == "0.19":
                    self.betraege[betrag]["u"] = 1
        
#        print self.betraege
#        print self.datum
#        print self.remark
#        print self.stunden
#        print self.mitarb

        ust    = ""
        erg    = {}
        datum1 = None
        for betrag in self.betraege:
            id = list(self.betraege[betrag].keys())
            id.sort()
            if "".join(id) in ("bnu","bu"):
                erg[betrag] = "qq"
            elif "".join(id) in ("bmv","bv"):
                erg[betrag] = "qw"
            elif len(self.betraege) == 1:
                erg[list(self.betraege.keys())[0]] = ""

#        print self.betraege
        ergs = list(erg.keys())
        ergs.sort(key=lambda x: float(x))
        if ergs:        
            ust = erg[ ergs[-1] ]
            erg = ergs[-1]
        else:
            erg = None
            
        if len(self.datum) > 0:
            self.datum = list(self.datum.keys())
            self.datum.sort()
            self.datum.reverse()
            datum1 = self.datum[0]
#            m = re.search(r"^(\d\d?)\.(\d\d?)\.(\d\d)(\d\d)",self.datum[0])
#            if m:
#                datum1 = m.group(4) + ("%02u" % int(m.group(2))) + ("%02u" % int(m.group(1)))

#        print self.datum, datum1, erg
        
        if datum2 == "":
            if datum1 and erg:
                return([erg,ust,datum1,""])
            else:    
                return(None)
        else:
            return([betrag2,ust2,datum2,remark2])

#********************************************************************************

    def xxjahressteuer (self,ktotext,einnahmen_ausgaben,ks,ks_sz,gw,aus,qs,qs_sz,ueberschuss,gesell_form=2):
    
        steuersatz = {
    
          "KS": {2006:0.15,
                 2007:0.15,2008:0.15,2009:0.15,2010:0.15,2011:0.15,2012:0.15,
                 2013:0.15,2014:0.15,2015:0.15,2016:0.15,2017:0.15,2018:0.15,
                 2019:0.15,2020:0.15,2021:0.15,2022:0.15,2023:0.15,
                 2024:0.15,2025:0.15,2026:0.15,2027:0.15,2028:0.15,
                 2029:0.15,2030:0.15,2031:0.15,2032:0.15,2033:0.15,
                 2034:0.15,2035:0.15,2036:0.15,2037:0.15,2038:0.15,
                 },
                 
          "GW": {2006:0.035,
                 2007:0.035,2008:0.035,2009:0.035,2010:0.035,2011:0.035,2012:0.035,
                 2013:0.035,2014:0.035,2015:0.035,2016:0.035,2017:0.035,2018:0.035,
                 2019:0.035,2020:0.035,2021:0.035,2022:0.035,2023:0.035,
                 2024:0.035,2025:0.035,2026:0.035,2027:0.035,2028:0.035,
                 2029:0.035,2030:0.035,2031:0.035,2032:0.035,2033:0.035,
                 2034:0.035,2035:0.035,2036:0.035,2037:0.035,2038:0.035,
                 },
                 
          "HS": {2006:425,
                 2007:425,2008:425,2009:425,2010:425,2011:440,2012:440,
                 2013:440,2014:440,2015:440,2016:440,2017:440,2018:440,
                 2019:440,2020:440,2021:440,2022:440,2023:440,
                 2024:440,2025:440,2026:440,2027:440,2028:440,
                 2029:440,2030:440,2031:440,2032:440,2033:440,
                 2034:440,2035:440,2036:440,2037:440,2038:440,
                 },
                 
          "QS": {2006:0.25,
                 2007:0.25,2008:0.25,2009:0.25,2010:0.25,2011:0.25,2012:0.25,
                 2013:0.25,2014:0.25,2015:0.25,2016:0.25,2017:0.25,2018:0.25,
                 2019:0.25,2020:0.25,2021:0.25,2022:0.25,2023:0.25,
                 2024:0.25,2025:0.25,2026:0.25,2027:0.25,2028:0.25,
                 2029:0.25,2030:0.25,2031:0.25,2032:0.25,2033:0.25,
                 2034:0.25,2035:0.25,2036:0.25,2037:0.25,2038:0.25,
                 },

          "SZ": {2006:0.055,
                 2007:0.055,2008:0.055,2009:0.055,2010:0.055,2011:0.055,2012:0.055,
                 2013:0.055,2014:0.055,2015:0.055,2016:0.055,2017:0.055,2018:0.055,
                 2019:0.055,2020:0.055,2021:0.055,2022:0.055,2023:0.055,
                 2024:0.055,2025:0.055,2026:0.055,2027:0.055,2028:0.055,
                 2029:0.055,2030:0.055,2031:0.055,2032:0.055,2033:0.055,
                 2034:0.055,2035:0.055,2036:0.055,2037:0.055,2038:0.055,
                 }
                     
              }

        ks    = ks.split("/")        
        ks_sz = ks_sz.split("/")
        gw    = gw.split("/")
        aus   = aus.split("/")
        qs    = qs.split("/")
        qs_sz = qs_sz.split("/")
        ueb   = ueberschuss.split("/")

        hoechst_jahr = 9999
        for art in steuersatz:
            hoechst_jahr = min(max(list(steuersatz[art].keys())),hoechst_jahr)

        jahresgewinn = {}    
        for file in einnahmen_ausgaben:
            text3 = open(file).read()
            for zeile in text3.split("\n"):
                m = re.search(r"^ *(\d\d\d\d) +(\-?\d+\.\d\d) *$",zeile)
                if not m:
                    continue
                jahr   = m.group(1)
                betrag = m.group(2)
                if not jahr in jahresgewinn:
                    jahresgewinn[jahr] = 0.00
                jahresgewinn[jahr] = jahresgewinn[jahr] - float(betrag)
#                print(jahresgewinn[jahr],jahr)
                
        text            = ""
        ausschuettungen = {}

        
        for zeile in ktotext.split("\n"):
            m = re.search('^(\d\d\d\d\d\d\d\d) +(\-?\d+\.\d\d) +(\S+?) +(\S+) +(\-?\d+\.\d\d) +(.*)', zeile)
            if not m:
                text = text + zeile + "\n"
                continue
                
            datum   = m.group(1)
            betrag  = m.group(2)
            ktoa    = m.group(3)
            ktob    = m.group(4)
            remark  = m.group(6)
            jahr    = datum[0:4]
            
            if not jahr in ausschuettungen:
                ausschuettungen[jahr] = 0.00

#            print(ktoa,aus[0])
            if ktoa == aus[0]:
                ausschuettungen[jahr] = ausschuettungen[jahr] + float(betrag)
                text = text + zeile + "\n"

        jahre = list(jahresgewinn.keys())
        jahre.sort()
        for jahr in jahre:

            jahr1 = min(hoechst_jahr,int(jahr))

            gewinn        = float(jahresgewinn[jahr])
            hebesatz      = int(steuersatz['HS'][jahr1])
#            print(jahr,hebesatz,jahr1)
            soli          = float(steuersatz['SZ'][jahr1])
            ausschuettung = 0.00
            if jahr in ausschuettungen:
                ausschuettung = ausschuettungen[jahr]
            rest          = gewinn - ausschuettung

            betrag1  = max(0.00,float(gewinn)) * float(steuersatz["KS"][jahr1])
#            print(jahr1,betrag1,gewinn)
            if gesell_form < 2:
                betrag1 = 0.00
            zeile    = jahr+"1223" + "  " + ("%3.2f"%betrag1) + "  "  + ks[0] + "  " + ks[1] + "  0.00  "
            text     = text + zeile + "Koerperschaftsteuer\n"
            rest     = rest - float ("%3.2f"%betrag1) 

            betrag1  = max(0.00,float(gewinn)) * float(steuersatz["KS"][jahr1]) * soli
            if gesell_form < 2:
                betrag1 = 0.00
            zeile    = jahr+"1224" + "  " + ("%3.2f"%betrag1) + "  "  + ks_sz[0] + "  " + ks_sz[1] + "  0.00  "
            text     = text + zeile +  "Solidaritaetszuschlag zur Koerperschaftsteuer\n"
            rest     = rest - float ("%3.2f"%betrag1) 

            betrag1  = max(0.00,float(gewinn)) * float(steuersatz["GW"][jahr1]) * int(hebesatz) * 0.01
            if gesell_form < 1:
                betrag1 = 0.00
            zeile    = jahr+"1225"  + "  " + ("%3.2f"%betrag1) + "  "  + gw[0] + "  " + gw[1] + "  0.00  "
            text     = text + zeile + "Gewerbesteuer\n"
            rest     = rest - float ("%3.2f"%betrag1) 

            betrag1  = float(ausschuettung) * float(steuersatz["QS"][jahr1])
            if gesell_form < 2:
                betrag1 = 0.00
            zeile    = jahr+"1226"  + "  " + ("%3.2f"%betrag1) + "  "  + qs[0] + "  " + qs[1] + "  0.00  "
            text     = text + zeile + "Quellensteuer\n"
            rest     = rest - float ("%3.2f"%betrag1) 

            betrag1  = float(ausschuettung) * float(steuersatz["QS"][jahr1]) * soli
            if gesell_form < 2:
                betrag1 = 0.00
            zeile    = jahr+"1227"  + "  " + ("%3.2f"%betrag1) + "  "  + qs_sz[0] + "  " + qs_sz[1] + "  0.00  "
            text     = text + zeile + "Solidaritaetszuschlag zur Quellensteuerr\n"
            rest     = rest - float ("%3.2f"%betrag1) 

            zeile    = jahr + "1228" + "  " + ("%3.2f"%rest) + "  " + ueb[0] + "  " + ueb[1] + "-" + jahr[2:4] + "  0.00  " 
            text     = text + zeile + "Jahres-Netto-Ueberschuss" + "\n"
#            print(zeile)

        return(text + "\n")

#********************************************************************************

    def xxausschuettung (self,ktotext,qs,qs_sz,qs_ki):
    
        text = ""


        for zeile in ktotext.split("\n"):
            m = re.search('^(\d\d\d\d\d\d\d\d) +(\-?\d+\.\d\d) +(\S+?) +(\S+) +(\-?\d+\.\d\d) +(.*)', zeile)

            if not m:
                text = text + zeile + "\n"
                continue

            datum  = m.group(1)
            betrag = m.group(2)
            ktoa   = m.group(3)
            ktob   = m.group(4)
            remark = m.group(6)
            jahr   = datum[0:4]

            if "Quellensteuer" in remark:
                continue            

            text = text + zeile + "\n"

            if "usschuettung" in remark:

                betrag1  = -float(betrag) * 0.25
                zeile    = datum + "  " + ("%3.2f"%betrag1) + "  -  " + qs + "   0.00  " 
                text     = text + zeile + "Quellensteuer\n"

                betrag1  = -float(betrag) * 0.25 * 0.055
                zeile    = datum + "  " + ("%3.2f"%betrag1) + "  -  " + qs_sz + "  0.00  "
                text     = text + zeile + "Solidaritaetszuschlag zur Quellensteuer\n"

#                betrag1  = -float(betrag) * 0.25 * 0.08
#                zeile    = datum + "  " + ("%3.2f"%betrag1) + "  - " + qs_ki + "  0.00  "
#                text     = text + zeile + "Kirchensteuer zur Quellensteuer\n"

        return(text + "\n")

#********************************************************************************

    def xxausgleich (self,ktotext,kto1,kto2,korrektur_files):
    
    
        text = ""
        korrektur_aufwand = {}
        korrektur_aktiva  = {}
        
        for zeile in ktotext.split("\n"):
            m = re.search('^(\d\d\d\d\d\d\d\d) +(\-?\d+\.\d\d) +(\S+?) +(\S+) +(\-?\d+\.\d\d) +(.*)', zeile)
            if m:
                if "Bilanzwert" in m.group(6):
                    korrektur_aufwand[m.group(1)[0:4]] = m.group(2)
                else:
                    korrektur_aktiva[m.group(1)[0:4]]  = m.group(2)
            else:
                text = text + zeile + "\n"
                continue

        korrektur_files.sort()
        korrektur_text = ""
        for file in korrektur_files:
            korrektur_text = korrektur_text + open(file).read()
            
        for zeile in korrektur_text.split("\n"):
            m = re.search(r"^ *(\d\d\d\d) +(\-?\d+\.\d\d) +(\-?\d+\.\d\d) +(\-?\d+\.\d\d) +(\-?\d+\.\d\d) *$",zeile)
            if not m:
                continue
            jahr    = m.group(1)
            aktiva  = m.group(2)
            passiva = m.group(3)
            ertrag  = m.group(4)
            aufwand = m.group(5)
            
            diff1   = ertrag - aufwand - korrektur_aufwand[jahr]
            sum     = sum + diff1
            diff0   = aktiva - passiva - sum - korrektur_aktiva[jahr]
            text    = text + jahr + "1230  " + ("%3.2f"%diff1) + "  -korrektur  " + kto1 + "  0.00  Bilanzwert\n"
            text    = text + jahr + "1230  " + ("%3.2f"%diff1) + "  -korrektur  " + kto1 + "  0.00  Ausgleichsbuchung\n"

        return(text)

#********************************************************************************

    def xxukto_from_betrag (self,betrag):

        id = re.sub(r"^\-","",str(betrag))
        id = re.sub("\.","",id)
        id = re.sub(r"^(.*?0)0*$","\\1",id)
        id = id + "00000"  # damit immer 5 Zeichen lang
        id = id[0:min(5,len(id))]

        return(id)

#******************************************************************************



if __name__ == "__main__":

    Meldung().parse_sv_meldungen()
    
    

