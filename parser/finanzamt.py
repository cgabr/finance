#  coding:  utf8

import os,sys,re,glob,time

try:
    from konto_custom import config
except:
    from konto.base import config


#*********************************************************************************

class Finanzamt (object):

    def __init__ (self,dir="."):
        self.dir            = dir
        self.KTO_FINANZAMT  = config.KTO_FINANZAMT     
        self.KTO_SAEUMNIS   = config.KTO_SAEUMNIS 
        self.KTO_ZWISCHEN   = config.KTO_ZWISCHEN  
        self.KTO_ZAHLUNG    = config.KTO_ZAHLUNG 
    
#*********************************************************************************

    def parse_finanzamt (self):

        ktofile = glob.glob("*.kto")
        if not len(ktofile) == 1:
            print("There is no unique ktofile. Stop.")
            return(0)
            
        ktotext = open(ktofile[0]).read()
            
        gegenkonto0 = self.KTO_FINANZAMT
        gegenkonto1 = self.KTO_SAEUMNIS


        files = glob.glob("*.csv")
        print(files)
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

        open(ktofile[0],"w").write(ktotext)
            
#*************************************************************************

    def finanzamt_zahlungen (self):  #  not ktosafe

        ktofile = glob.glob("*.kto")
        if not len(ktofile) == 1:
            print("There is no unique ktofile. Stop.")
            return(0)
            
        ktotext = open(ktofile[0]).read()
            
        zkto = self.KTO_ZWISCHEN
        fkto = self.KTO_ZAHLUNG 

        text1 = []
        for zeile in ktotext.split("\n"):
            if not "Steuerzahlung lt. Kontoauszug" in zeile:
                text1.append(zeile)
        ktotext = "\n".join(text1) + "\n"
                  
        files = glob.glob("*.csv")
        if len(files) == 0:
            return(ktotext)
            
        zaehler = 0
        text = open(files[0]).read()
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
 
        open(ktofile[0],"w").write(ktotext)

#*********************************************************************************


if __name__ == "__main__":

    if len(sys.argv) > 1:
        if sys.argv[1] == "zahlung":
            Finanzamt().finanzamt_zahlungen()
        elif sys.argv[1] == "steuern":
            Finanzamt().parse_finanzamt()
            



