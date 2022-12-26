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
    
#*********************************************************************************

    def parse_finanzamt (self):


        ktofile = glob.glob("*.kto")
        if not len(ktofile) == 1:
            print("There is no unique ktofile. Stop.")
            return(0)
            
        ktotext = open(ktofile[0]).read()
            
        gegenkonto0 = self.KTO_FINANZAMT
        gegenkonto1 = self.KTO_SAEUMNIS


        files = glob.glob("*.manuell")
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
            
#*********************************************************************************


if __name__ == "__main__":

    Finanzamt().parse_finanzamt()
    
    

