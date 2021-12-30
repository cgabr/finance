import os,re,sys,glob

#import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from konto.base import konto

#**********************************************************************************

#  a geckodriver has to run

class SV_Meldung():

    def __init__ (self):
    
        self.base_dir = konto.Konto().base_dir

    def setup_method(self, method):

        self.vars    = {}
        self.dataset = {}
        self.driver  = webdriver.Firefox()
        return(self)
        
#**************************************************************************************

    def set_par (self,feld,inhalt):

#        inhalt1 = inhalt
#        if re.search(r"^\-([A-Z]+\d*)\-$",inhalt):
#            m = re.search(inhalt[1:-1]+'\: +(.*?)\"',self.dataset)
#            if not m:
#                if inhalt in self.soz_par:
#                    inhalt1 = self.soz_par[inhalt]
#                else:
#                    inhalt1 = ""
#            else:
#                inhalt1 = m.group(1)
#            self.soz_par[inhalt] = inhalt1
#             print(inhalt,self.soz_par[inhalt],inhalt1)


        if inhalt.startswith("."):
            inhalt = self.dataset[inhalt[1:]]

        self.driver.find_element(By.ID,feld).send_keys(inhalt)
        time.sleep(0.5)
        return(inhalt)

#**************************************************************************************

    def teardown_method(self, method):

        self.driver.quit()

#**************************************************************************************

    def el (self,selector):

        return(self.driver.find_element(By.CSS_SELECTOR,selector))

#**************************************************************************************

    def li (self,selector):

        return(self.driver.find_element_by_link_text(selector))

#**************************************************************************************

    def id (self,selector):

        return(self.driver.find_element_by_id(selector))

#**************************************************************************************

    def xp (self,selector):

        return(self.driver.find_element_by_xpath(selector))

#**************************************************************************************

    def run1 (self):

        self.driver.get("https://standard.gkvnet-ag.de/svnet/")
        self.driver.set_window_size(712, 705)
        time.sleep(2)
        self.el("[aria-labelledby='loginDialogLabelBetriebsnummer']").send_keys("14993475")
        self.el("[aria-labelledby='loginDialogLabelBenutzername']")  .send_keys("cgabriel")
        self.el("[aria-labelledby='loginDialogLabelPasswort']")      .send_keys("IfT2012")
        self.xp("//div[text()='Anmelden']").click()
        time.sleep(2)
        self.el("[aria-labelledby='overviewViewformulareLabel']")    .click()
        time.sleep(2)

#   1.   Beginn, Ende, Jahresgehalt aus Gehaltsbscheinigungen

        if not self.jahr == "":
            self.dataset["meldejahr"] = self.jahr
        if not self.meldung == "":
            self.dataset["meldung"]   = self.meldung
        if not self.person == "":
            self.dataset["person"]    = self.person

        print(self.dataset["meldejahr"])

        beginnmonat = 13
        endmonat    =  0
        
        if not 'beginn' in self.dataset or not 'jahresgehalt' in self.dataset:

            for gehaltsmeldung in glob.glob("*/gehalt*"+self.dataset["meldejahr"]+"*_*.md"):
                print(gehaltsmeldung)
                m = re.search(r"_(\d\d\d\d)_(\d\d)",gehaltsmeldung)
                if m:
                    monat       = int(m.group(2))
                    beginnmonat = min(beginnmonat,monat)
                    if monat > endmonat:
                        endmonat = monat
                        text     = open(gehaltsmeldung).read()
                        m = re.search(r"Gehalt +Brutto(.*?)(\d+\.\d\d) +(\d+\.\d\d)",text)
                        if m:
                            jahresgehalt = str(int(float(m.group(3))+0.5))
                            print(jahresgehalt)
                               
            beginn = "01." + ("%02u"%beginnmonat)  + "." + self.dataset["meldejahr"]
            ende   = "."   + ("%02u"%endmonat)     + "." + self.dataset["meldejahr"]
            if endmonat in (1,3,5,7,8,10,12):
                ende = "31" + ende
            elif endmonat in (4,6,9,11):
                ende = "30" + ende
            elif int(self.dataset["meldejahr"]) % 4 == 0 and not int(self.dataset["meldejahr"]) % 100 == 0:
                ende = "29" + ende
            else:
                ende = "28" + ende
                
            self.dataset['beginn']  = beginn
            self.dataset['ende']    = ende
            self.dataset['betrag']  = jahresgehalt
        
        if self.dataset["meldung"] == "10":

            self.xp("//div[text()='SV-Meldung (Allgemein, Knappschaft, See)']").click()
            self.xp("//div[text()='Anmeldung']").click()
            time.sleep(1)
            self.el("[aria-labelledby='overviewViewm10Label']")    .click()
            
#            self.el( "div:nth-child(3) > div:nth-child(2) > div:nth-child(2) > div").click()
#            self.el( "div:nth-child(7) > div > div > div > div:nth-child(1) >  div:nth-child(1)").click()
#            self.el( "div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div").click()
#            self.el( "div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div").click()
#            self.el( "div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div").click()

        if self.dataset["meldung"] == "50":

            self.xp("//div[text()='SV-Meldung (Allgemein, Knappschaft, See)']").click()
            self.xp("//div[text()='Jahresmeldung']").click()
            time.sleep(1)
            self.el("[aria-labelledby='overviewViewm50Label']")    .click()

#            self.el( "div:nth-child(3) div:nth-child(6) > div").click()
#            self.el( "div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div").click()
#            self.el( "div:nth-child(2) > div:nth-child(4) > div:nth-child(1) > div").click()
#            self.el( "div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div").click()

        if self.dataset["meldung"] == "92":
        
            self.xp("//div[text()='SV-Meldung (Allgemein, Knappschaft, See)']").click()
            self.xp("//div[text()='Jahresmeldung']").click()
            time.sleep(1)
            self.el("[aria-labelledby='overviewViewm92Label']")    .click()
            self.dataset['beginn'] = "01.01." + self.dataset["meldejahr"]
            self.dataset['ende']   = "31.12." + self.dataset["meldejahr"]

#            self.el( "div:nth-child(3) div:nth-child(6) > div").click()
#            self.el( "div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div").click()
#            self.el( "div:nth-child(2) > div:nth-child(4) > div:nth-child(1) > div").click()
#            self.el( "div:nth-child(2) > div:nth-child(3) > div:nth-child(1) > div").click()

        if self.dataset["meldung"] == "30":

            self.el( "div:nth-child(3) div:nth-child(6) > div").click()
            self.el( "div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div").click()
            self.el( "div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div").click()
            self.el( "div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div").click()

#        return()
        time.sleep(5)
        self.driver.switch_to.frame(1)

        self.set_par("firmaBetriebsnummer",            ".betriebsnummer")
        self.set_par("firmaName1",                     ".firmaname1")
        self.set_par("firmaName2",                     ".firmaname2")
        self.set_par("firmaStrasse",                   ".firmastrasse")
        self.set_par("firmaAnschriftenzusatz",         ".firmastrasse2")
        self.set_par("firmaLand",                      ".firmaland")
        self.set_par("firmaPostleitzahl",              ".firmaplz")
        self.set_par("firmaOrt",                       ".firmastadt")

        self.set_par("betriebsnummerKrankenkasse",     ".kkbetrnr")
        self.set_par("beginn",                         ".beginn")

        self.set_par("personVersicherungsnummer",      ".sozversnr")
        self.set_par("personPersonalnummer",           ".account")
        self.set_par("personStaat",                    ".stkuerzel")
        self.set_par("personName",                     ".name")
        self.set_par("personVorsatz",                  "")
        self.set_par("personVorname",                  ".vorname")
        self.set_par("personZusatz",                   "")
        self.set_par("personStrasse",                  ".strasse")
        self.set_par("personHausnummer",               ".hausnr")
        self.set_par("personAnschriftenzusatz",        "")
        self.set_par("personLand",                     ".land")
        self.set_par("personPostleitzahl",             ".plz")
        self.set_par("personOrt",                      ".stadt")


        if not self.dataset["meldung"] == "92": 

            self.set_par("firmaRechtskreis",               ".rechtskreis")
            self.set_par("personengruppe",                 ".persgruppe")
            self.set_par("taetigkeit",                     ".tschluessel")
            self.set_par("schulabschluss",                 ".schule")
            self.set_par("berufsausbildung",               ".beruf")
            self.set_par("aUEG",                           ".aueg")
            self.set_par("kv",                             ".kv")
            self.set_par("rv",                             ".rv")
            self.set_par("pv",                             ".pv")
            self.set_par("av",                             ".av")
            self.set_par("vertragsform",                   ".vertrag")


        if self.dataset["sozversnr"] == "":

            self.set_par("personGeburtsName",              ".gebname")
            self.set_par("personGeburtsVorsatz",           "")
            self.set_par("personGeburtsZusatz",            "")
            self.set_par("personGeburtsdatum",             ".gebdat")
            self.set_par("personGeburtsOrt",               ".gebort")
            self.set_par("personGeschlecht",               ".mw")

#       Anmeldung

        if self.dataset["meldung"] == "10" and not self.dataset["persgruppe"] == "109": 

            self.set_par("kennzeichenSaisonArbeitnehmer",  "N")
            
            
#       Jahresmeldung:

        if self.dataset["meldung"] == "50": 

            self.set_par("ende",                           ".ende")
#            self.set_par("entgeltRentenberechnung",        ".betrag")
#            self.set_par("waehrung",                       "E")
            self.set_par("entgelt",                        ".betrag")
            self.set_par("gleitzone",                      ".gleitzone")   #  0,1,2  nein/ja/teils

#       UV-Jahresmeldung:

        if self.dataset["meldung"] == "92": 

            self.set_par("uvData.0.betriebsnummerUV",               ".betriebsnummeruv")
            self.set_par("uvData.0.firmaMitgliedsnummerUV",         ".mitgliedsnummeruv")
            self.set_par("uvData.0.grund",                          ".grunduv")
            self.set_par("uvData.0.betriebsnummerGefahrtarifstelle",".betriebsnrgefahr")
            self.set_par("uvData.0.gefahrtarifstelle",              ".gefahrtarifstelle")
            self.set_par("uvData.0.arbeitsentgelt",                 ".betrag")




#**************************************************************************************

    def run (self):
        
#        gehaltsbescheinigungen = glob.glob("./*/*gehalt*"+self.dataset["meldejahr"]+"*.md")
#        gehaltsbescheinigungen.sort()
#        m = re.search(r"Gehalt +[bB]rutto[: ]+\d+\.\d\d +(\d+\.\d\d)", open(gehaltsbescheinigungen[-1]).read())
#        if m:
#            self.dataset['betrag'] = str(int(float(m.group(1))))
            
        m = re.search(r"^(.*) +(\d+[a-zA-Z]?) *$",self.dataset['strasse'])
        if m:
            self.dataset['strasse'] = m.group(1)
            self.dataset['hausnr']  = m.group(2)
        if not 'hausnr' in self.dataset:
            self.dataset['hausnr']  = ""


        self.run1() 
            
#*************************************************************************************
            

if __name__ == "__main__":

    r            = SV_Meldung().setup_method("")
#    config_data  = [ os.popen("python3 -m fibu.xlsmanager memory oa ./15*/*.csv aktuell").read() ]  #  personal data
    kto          = konto.Konto()
    kto.read_config(kto.base_dir+"/*.data")
    kto.read_config("../*.data")
    kto.read_config("./sv.data")
    kto.read_config("*/sv.data")
    kto.read_config("./15*/*.csv")
    r.dataset = kto.dataset

    print(r.dataset)
#    for o in r.dataset.keys():
#        print(r.dataset[o])


    try:
        r.jahr = ("20" + sys.argv[2])[-4:]
    except:
        r.jahr = ""
        
    try:
        r.meldung = sys.argv[1]
    except:
        r.meldung = ""
        
    dir = os.path.abspath(".")
    m = re.search(r"^(.*)[\\\/]([a-z]+)([\\\/]|$)",dir)
    if m:
        r.person = m.group(2)
    else:
        r.person = ""

    r.run()


#*************************************************************************************

#        r.soz_par = {}
#    
#        person    = "tbroecking"
#        meldejahr = "2021"
#        meldung   = "10"
#    
#        r.dataset = os.popen("python3 -m fibu.xlsmanager memory oa " + person + "/15*/*.csv aktuell").read()
#        
#        gehaltsbescheinigungen = glob.glob(person+"/gehalt*"+meldejahr+"*.md")
#        gehaltsbescheinigungen.sort()
#        m = re.search(r"Gehalt +[bB]rutto[: ]+\d+\.\d\d +(\d+\.\d\d)", open(gehaltsbescheinigungen[-1]).read())
#        if m:
#            r.soz_par['-BETRAG-']     = str(int(float(m.group(1))))
#            
#        r.soz_par['-ART-']        = meldung
#        r.soz_par['-GLEITZONE-']  = 0
#        r.soz_par['-BEGINN-']     = "01.03." + meldejahr
#        r.soz_par['-ENDE-']       = "31.12." + meldejahr
#        
#        r.run1()    
    
