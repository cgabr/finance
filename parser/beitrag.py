#  coding:  utf8

import os,sys,re,glob,time

try:
    from konto_custom import config
except:
    from konto.base import config


#*********************************************************************************

class Beitrag (object):

    def __init__ (self,dir="."):
        self.dir   = dir
        self.kk_meldung    = config.KTO_KK_MELDUNG     
        self.kk_bnachweis  = config.KTO_BEITRAGSNACHWEISE 
        self.krankenkasse  = config.KTO_KRANKENKASSEN 
        self.kkmap = re.sub(r"\s","",config.MAP_KRANKENKASSEN,99999999).split(",")
    
#*********************************************************************************

    def mark (self,remark=""):

        t = time.perf_counter()
        if 't0' in vars(self):
            print ( ("%9.2f" % ((t-self.t0)*1000)) + " ms for:  " + remark )
        self.t0 = t

#********************************************************************************

    def parse_beitragsnachweise (self):

        kkdatum            = {}
        self.betriebsnr_kk = {}

        ktofile = glob.glob("*.kto")
        if not len(ktofile) == 1:
            print("Ktofile ambiguous.")
            return()

        buchungen = []
        for zeile in open(ktofile[0]).read().split("\n"):
            if not re.search('^\d\d\d\d\d\d\d\d +\-?\d+\.\d\d.*-meld(ung|ZUS).*-meld(ung|ZUS)', zeile):
                buchungen.append(zeile)

        beitragsnachweise = glob.glob(self.dir+"/*.pdf") + glob.glob(self.dir+"/*.manuell") + glob.glob(self.dir+"/*.lexware")
        beitragsnachweise.sort()
        

        for beitragsnachweis in beitragsnachweise:
        
            if "_orig." in beitragsnachweis:
                continue

            buchungen1 = []
            text       = ""
            if "pdf" in beitragsnachweis.lower():
                os.system("pdftotext -layout " + beitragsnachweis + " __xx.txt")
                text = open("__xx.txt").read()
            
            if len(text) < 10:
                text = open(beitragsnachweis).read()

            text = self.normalize_text(text)

            m = re.search('Einzugsstelle.*Betriebsnummer +(\d+)(.*?)Name +([^\n ]+)', text, re.DOTALL)
            if not m:
                continue
            kknr   = m.group(1)
            remark = m.group(3) + ' ' + m.group(1)
            remark = re.sub('[\\n-]/', ' ', remark, 9999, re.DOTALL)
            remark = re.sub('^(.*?) +(.*?) .*? (\d+)$', '\\1 \\2 \\3', remark)

            print(beitragsnachweis)
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


            text = re.sub('(.*) +ohne +Sozialausgleich(.*)', '', text, 9999)  # wegen doppelt eingetragener Betraege

            m = re.search('Zeitraum +von +(\d+)\.(\d+)\.(\d+).*?Zeitraum +bis +(\d+)\.(\d+)\.(\d+)', text, re.DOTALL)
            if not m:
                continue
            if not m.group(2) == m.group(5):
                continue
            if not m.group(3) == m.group(6):
                continue

            jahr    = m.group(3)
            monat   = m.group(2)

            newname = kkid + '_' + kknr + '__' + jahr + '_' + monat + '__' + sendedatum + "_" + betriebsnummer + "_" + tan 

            text = re.sub('(\d)\.(\d+\,\d\d)', '\\1\\2', text, 9999)

            o = kknr + ',' + jahr + monat
            if o in kkdatum:
                kkdatum[o] = kkdatum[o] + 1
            else:
                kkdatum[o] = 20
                
            datum = jahr + monat + '%02u' % kkdatum[o]
            new_addtext = False

            stornofaktor = 1.0
            remarkadd    = ""
            add_mode     = ""
            
            if "Storno " in text:
                stornofaktor = -1.0
                remarkadd    = "manuell storniert - "
            if re.search(r"Stornierung +(JA|Ja|ja)",text):
                stornofaktor = -1.0
#                add_mode = "POSITIV"
#                print("STS",jahr+monat,st)
                remarkadd    = "Stornierung - "


            while (0 == 0):

                m = re.search('^(.*\n)(.*?Pausch\S*|Storno|Beitrae?\"?ge? [a-z]\S*|Zusatzb\S*|Umlage\S*) ([^\n]*?) *(\-?\d+)\,(\d\d)', text, re.IGNORECASE + re.DOTALL)
                if not m:
                    break

                text    = m.group(1)
                remark1 = remark + ', ' + m.group(2) + ' ' + m.group(3)
                remark1 = re.sub('\n', ' ', remark1, 9999, re.DOTALL)

                ktob = "-" + kkid + '-meldung-' + datum[6:8]

                if 'Storno' in remark1:
                    continue
                elif re.search(', Beitr.*Krankenvers.*allgem', remark1):
                    ktoa =  '-KV-meldung'
                elif re.search(', Zusatzbeitr.*Krankenvers', remark1):
                    ktoa =  '-KV-meldung'
                elif re.search(', Beitr.*Krankenvers.*geringf', remark1):
                    ktoa =  '-KV-meldung'
                elif re.search(', Pauschal.*Krankenvers', remark1):
                    ktoa =  '-KV-meldung'
                elif re.search(', Beitr.*Krankenvers.*erm', remark1):
                    ktoa =  '-EV-meldung'
                elif ' Arbeitsfoerderung' in remark1 or 'Arbeitslosen' in remark1:
                    if "halb" in remark1 or "pauschal" in remark1.lower():
                        ktoa =  '-BV-meldung'
                    else:
                        ktoa =  '-AV-meldung'
                elif ' Rentenversicherung' in remark1:
                    if "halb" in remark1 or "pauschal" in remark1.lower():
                        ktoa =  '-XV-meldung'
                    else:
                        ktoa =  '-RV-meldung'
                elif ' Pflegeversicherung' in remark1:
                    ktoa =  '-PV-meldung'
                elif ' Krankheitsaufwendungen' in remark1:
                    ktoa =  '-U1-meldung'
                elif ' Mutterschaftsaufwendungen' in remark1:
                    ktoa =  '-U2-meldung'
                elif ' Insolvenzgeldversicherung' in remark1:
                    ktoa =  '-U3-meldung'
                elif re.search('inheitliche *P', remark1):
                    ktoa =  '-ST-meldung'
                elif ' UST' in remark1:
                    ktoa =  '-xxUSTxx-meldung'
                elif ' einzubehaltene' in remark1:
                    ktoa =  '-LS-meldung'
                elif ' pauschal' in remark1:
                    ktoa =  '-PL-meldung'
                elif ' Solidarit' in remark1:
                    ktoa =  '-SZ-meldung'
                elif ' Kirchensteuer roem' in remark1:
                    ktoa =  '-KR-meldung'
                elif ' Kirchensteuer evan' in remark1:
                    ktoa =  '-KE-meldung'
                elif ' Kirchensteuer altk' in remark1:
                    ktoa =  '-KA-meldung'
                elif ' Kirchensteuer isra' in remark1:
                    ktoa =  '-KB-meldung'
                elif re.search(' Sae?umn| Mahn|gebuehr', remark1):
                    ktoa =  '-saeumn'
                elif re.search(' Beitrae?g| Betriebspr', remark1):
                    ktoa =  '-beitrag'
                elif re.search(' Umbuchung +Leistung+ U1', remark1):
                    ktoa =  '-umbuchung'
                else:
                    continue

                betrag1 = float(m.group(4) + '.' + m.group(5))
                
                betrag1 = (-betrag1) * stornofaktor

                if "POSITIV" in (beitragsnachweis+add_mode):
                    betrag1 = - ( float(m.group(4) + '.' + m.group(5)) )
                
                if abs(betrag1) > 0.0001:
                    buchungen.append(datum + "  " +  '%3.2f' % betrag1 + "  " + self.kk_meldung  + ktob +  "  " + self.kk_bnachweis + "-" + kkid + ktoa + "  0.00  " + remarkadd + remark1)
#                    print(buchungen[-1])

#            print(buchungen1)

            buchungen = buchungen + buchungen1

            if "POSITIV" in (beitragsnachweis+add_mode):
                newname = newname + "__POSITIV"
                
            newname = re.sub("__NEGATIV","",newname,99)
                
            m = re.search('^(.*)\.(.*?)$',beitragsnachweis)  #  renaming the original files
            filename = m.group(1)
            if not filename == newname:
#                print('rename file ' + beitragsnachweis + ' to ' + newname + "." + m.group(2))
                os.rename(beitragsnachweis, newname + '.' + m.group(2))

        zeilen = []
        for buchung in buchungen:
#            print(buchung)
            zeilen.append(' '.join(buchung))
#            print(zeilen[-1])

        ktotext = '\n'.join(buchungen) + '\n'

        open(ktofile[0],"w").write(ktotext)

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


#******************************************************************************



if __name__ == "__main__":

    Beitrag().parse_beitragsnachweise()
    
    

