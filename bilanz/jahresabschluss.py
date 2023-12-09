#!/usr/bin/python3
#  coding:  utf8

import os,sys,re,glob,time

from konto.base.konto import Konto

#*********************************************************************************

class Jahresabschluss (object):

    def __init__ (self):

        self.kto_koerperschaftsteuer      = "14-Daa-7603/11-C13-3040"
        self.kto_soli_koerperschaftsteuer = "14-Daa-7608/11-C13-3040"
        self.kto_gewerbesteuer            = "14-Daa-7610/11-C13-3035"
        self.kto_ausschuettung            = "14-Dba-7790/..........."
        self.kto_quellensteuer            = "14-Dba-3700/11-C13-3050"
        self.kto_soli_quellensteuer       = "14-Dba-3708/11-C13-3050"
        self.kto_ueberschuss              = "14-Dca-7639/11-C02-2080"

        
        self.steuersatz = {
    
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

        self.steuersatz_ba = {
        
          "KS": {
                 2019:0.15,2020:0.15,2021:0.15,2022:0.15,2023:0.15,
                 2024:0.15,2025:0.15,2026:0.15,2027:0.15,2028:0.15,
                 2029:0.15,2030:0.15,2031:0.15,2032:0.15,2033:0.15,
                 2034:0.15,2035:0.15,2036:0.15,2037:0.15,2038:0.15,
                 },
                 
          "GW": {
                 2019:0.00,2020:0.00,2021:0.00,2022:0.00,2023:0.00,
                 2024:0.00,2025:0.00,2026:0.00,2027:0.00,2028:0.00,
                 2029:0.00,2030:0.00,2031:0.00,2032:0.00,2033:0.00,
                 2034:0.00,2035:0.00,2036:0.00,2037:0.00,2038:0.00,
                 },
                 
          "HS": {2006:425,
                 2007:425,2008:425,2009:425,2010:425,2011:440,2012:440,
                 2013:440,2014:440,2015:440,2016:440,2017:440,2018:440,
                 2019:440,2020:440,2021:440,2022:440,2023:440,
                 2024:440,2025:440,2026:440,2027:440,2028:440,
                 2029:440,2030:440,2031:440,2032:440,2033:440,
                 2034:440,2035:440,2036:440,2037:440,2038:440,
                 },
                 
          "QS": {
                 2007:0.00025,2008:0.00025,2009:0.00025,2010:0.00025,2011:0.00025,2012:0.00025,
                 2013:0.00025,2014:0.00025,2015:0.00025,2016:0.00025,2017:0.00025,2018:0.00025,
                 2019:0.00025,2020:0.00025,2021:0.00025,2022:0.00025,2023:0.00025,
                 2024:0.00025,2025:0.00025,2026:0.00025,2027:0.00025,2028:0.00025,
                 2029:0.00025,2030:0.00025,2031:0.00025,2032:0.00025,2033:0.00025,
                 2034:0.00025,2035:0.00025,2036:0.00025,2037:0.00025,2038:0.00025,
                 },

          "SZ": {2006:0.000001,
                 2007:0.000001,2008:0.000001,2009:0.000001,2010:0.000001,2011:0.000001,2012:0.000001,
                 2013:0.000001,2014:0.000001,2015:0.000001,2016:0.000001,2017:0.000001,2018:0.000001,
                 2019:0.000001,2020:0.000001,2021:0.000001,2022:0.000001,2023:0.000001,
                 2024:0.000001,2025:0.000001,2026:0.000001,2027:0.000001,2028:0.000001,
                 2029:0.000001,2030:0.000001,2031:0.000001,2032:0.000001,2033:0.000001,
                 2034:0.000001,2035:0.000001,2036:0.000001,2037:0.000001,2038:0.000001,
                 }
                     
              }


#*********************************************************************************

    def mark (self,remark=""):

        t = time.perf_counter()
        if 't0' in vars(self):
            print ( ("%9.2f" % ((t-self.t0)*1000)) + " ms for:  " + remark )
        self.t0 = t

#*********************************************************************************

    def jahressteuer (self,ktotext0="",*pars):

        gesell_form = pars[0]   #  2: Koerperschaftsteuer und Quellensteuer
                                #  1: Koerperschaftsteuer
                                #  0: keine Bilanzierung

        if ktotext0 == "":
            ktofile = ( glob.glob("*.kto") + glob.glob("*.kto.html") )[0]
            ktotext = open(ktofile).read()
        else:
            ktotext = ktotext0
            
        ks    = self.kto_koerperschaftsteuer.split("/")        
        ks_sz = self.kto_soli_koerperschaftsteuer.split("/")
        gw    = self.kto_gewerbesteuer.split("/")
        aus   = self.kto_ausschuettung.split("/")
        qs    = self.kto_quellensteuer.split("/")
        qs_sz = self.kto_soli_quellensteuer.split("/")
        ueb   = self.kto_ueberschuss.split("/")

        if "firmaland" in self.dataset and self.dataset["firmaland"] == "BA":
            self.steuersatz = self.steuersatz_ba

#        jahresgewinn = {}    
#        for file in einnahmen_ausgaben:
#            text3 = open(file).read()
#            for zeile in text3.split("\n"):
#                m = re.search(r"^ *(\d\d\d\d) +(\-?\d+\.\d\d) *$",zeile)
#                if not m:
#                    continue
#                jahr   = m.group(1)
#                betrag = m.group(2)
#                if not jahr in jahresgewinn:
#                    jahresgewinn[jahr] = 0.00
#                jahresgewinn[jahr] = jahresgewinn[jahr] - float(betrag)
#                print(jahresgewinn[jahr],jahr)
                
        text            = ""
        ausschuettungen = {}
        min_jahr        = 9999
        max_jahr        = 0
        
        for zeile in ktotext.split("\n"):
#            print(zeile)
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
            
            min_jahr = min(int(jahr),min_jahr)
            
            if not jahr in ausschuettungen:
                ausschuettungen[jahr] = 0.00

#            print(jahr,ktoa,aus[0])
            if ktoa == aus[0]:
#                print(zeile)
                ausschuettungen[jahr] = ausschuettungen[jahr] + float(betrag)
                text = text + zeile + "\n"
                max_jahr = max(int(jahr),max_jahr)

        jahr = min_jahr - 1
        kto  = Konto()
        
#        print(ausschuettungen)
#        print(jahr,max_jahr)
 
        while 0 == 0:

            jahr = jahr + 1
            if jahr > max_jahr:
                break

            jahr1         = min(max_jahr,int(jahr))

            print("SALDO 12",kto.read_saldo("12-."+str(jahr)[2:4]))
            print("SALDO 13",kto.read_saldo("13-."+str(jahr)[2:4]))
            print("SALDO 16",kto.read_saldo("16-."+str(jahr)[2:4]))  #  Vor- und Ruecktraege
            gewinn_o_vortrag = - kto.read_saldo("12-."+str(jahr)[2:4]) - kto.read_saldo("13-."+str(jahr)[2:4])
            gewinn_m_vortrag = gewinn_o_vortrag - kto.read_saldo("16-."+str(jahr)[2:4])
            hebesatz      = int(self.steuersatz['HS'][jahr1])
#            print(jahr,hebesatz,jahr1,gewinn)
            soli          = float(self.steuersatz['SZ'][jahr1])
            ausschuettung = 0.00
            if str(jahr) in ausschuettungen:
                ausschuettung = ausschuettungen[str(jahr)]
            rest          = gewinn_o_vortrag - ausschuettung
#            print(jahr,"AUS",ausschuettung)

            betrag1  = max(0.00,float(gewinn_m_vortrag)) * float(self.steuersatz["KS"][jahr1])
#            print(jahr1,betrag1,gewinn)
            if int(gesell_form) < 2:
                betrag1 = 0.00
            zeile    = str(jahr)+"1223" + "  " + ("%3.2f"%betrag1) + "  "  + ks[0] + "  " + ks[1] + "  0.00  "
            text     = text + zeile + "Koerperschaftsteuer\n"
            rest     = rest - float ("%3.2f"%betrag1) 

            betrag1  = max(0.00,float(gewinn_m_vortrag)) * float(self.steuersatz["KS"][jahr1]) * soli
            if int(gesell_form) < 2:
                betrag1 = 0.00
            zeile    = str(jahr)+"1224" + "  " + ("%3.2f"%betrag1) + "  "  + ks_sz[0] + "  " + ks_sz[1] + "  0.00  "
            text     = text + zeile +  "Solidaritaetszuschlag zur Koerperschaftsteuer\n"
            rest     = rest - float ("%3.2f"%betrag1) 

            betrag1  = max(0.00,float(gewinn_m_vortrag)) * float(self.steuersatz["GW"][jahr1]) * int(hebesatz) * 0.01
            if int(gesell_form) < 1:
                betrag1 = 0.00
            zeile    = str(jahr)+"1225"  + "  " + ("%3.2f"%betrag1) + "  "  + gw[0] + "  " + gw[1] + "  0.00  "
            text     = text + zeile + "Gewerbesteuer\n"
            rest     = rest - float ("%3.2f"%betrag1) 

            betrag1  = float(ausschuettung) * float(self.steuersatz["QS"][jahr1])
            if int(gesell_form) < 2:
                betrag1 = 0.00
            zeile    = str(jahr)+"1226"  + "  " + ("%3.2f"%betrag1) + "  "  + qs[0] + "  " + qs[1] + "  0.00  "
            text     = text + zeile + "Quellensteuer\n"
            rest     = rest - float ("%3.2f"%betrag1) 

            betrag1  = float(ausschuettung) * float(self.steuersatz["QS"][jahr1]) * soli
#            print(gesell_form,"BB",betrag1)
            if int(gesell_form) < 2:
                betrag1 = 0.00
#            print(gesell_form,"BC",betrag1)
            zeile    = str(jahr)+"1227"  + "  " + ("%3.2f"%betrag1) + "  "  + qs_sz[0] + "  " + qs_sz[1] + "  0.00  "
            text     = text + zeile + "Solidaritaetszuschlag zur Quellensteuerr\n"
            rest     = rest - float ("%3.2f"%betrag1) 

            zeile    = str(jahr) + "1228" + "  " + ("%3.2f"%rest) + "  " + ueb[0] + "  " + ueb[1] + "-" + str(jahr)[2:4] + "  0.00  " 
            text     = text + zeile + "Jahres-Netto-Ueberschuss" + "\n"
#            print(zeile)

        ktotext = text
        
        if ktotext0 == "":
            open(ktofile,"w").write(ktotext)

        return(ktotext)

#**********************************************************************************************

if __name__ == "__main__":

    r = Jahresabschluss()
    

    kto          = Konto()
    kto.read_config(kto.base_dir+"/*.data")
    kto.read_config("../*.data")
    kto.read_config("./sv.data")
    kto.read_config("*/sv.data")
    kto.read_config("./15*/*.csv")
    kto.read_config("../05*/*.csv")
    r.dataset = kto.dataset
#    print("QQQQQ",r.dataset)

    r.jahressteuer("",*sys.argv[1:])
    
