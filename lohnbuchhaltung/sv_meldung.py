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
    
        self.base_dir  = konto.Konto().base_dir
        self.ankerjahr = "2023"

    def setup_method(self, method):

        self.vars    = {}
        self.dataset = {}
        self.driver  = webdriver.Firefox()
        return(self)
        
#**************************************************************************************

    def set_par (self,feld,inhalt=None):

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

        if inhalt == None:
            return()

        if inhalt.startswith("."):
            inhalt = self.dataset[inhalt[1:]]

        self.driver.find_element(By.ID,feld).send_keys(inhalt)
        time.sleep(0.55)
        return(inhalt)

#**************************************************************************************

    def set_par1 (self,feld,erg,inhalt=None):

        try:
            self.set_par(feld,erg[inhalt])
        except:
            pass

#**************************************************************************************

    def teardown_method(self, method):

        self.driver.quit()

#**************************************************************************************

    def el (self,selector):

        return(self.driver.find_element(By.CSS_SELECTOR,selector))

#    Besteuer   2731 247 6703, xuUKrHeW534


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

    def run (self):


        self.dataset["firmaadresse"] = self.dataset["firmastrasse"]
        m = re.search(r"^(.*) +(\d+[a-zA-Z]?) *$",self.dataset['firmastrasse'])
        if m:
            self.dataset['firmastrasse'] = m.group(1)
            self.dataset['firmahausnr']  = m.group(2)
        if not 'firmahausnr' in self.dataset:
            self.dataset['firmahausnr']  = ""



#   1.   Beginn, Ende, Jahresgehalt aus Gehaltsbscheinigungen

        if not self.jahr == "":
            self.dataset["meldejahr"] = self.jahr
        if not self.meldung == "":
            self.dataset["meldung"]   = self.meldung
#        if not self.person == "":
#            self.dataset["person"]    = self.person

        beginnmonat   = 13
        endmonat      =  0
        jahresgehalt  = "0,00"
        bruttogehalt  = "0,00"
        jahresgehalt0 = "0"
        bruttogehalt0 = "0"

        print("JJJJ",self.dataset["meldejahr"])


        if not 'beginn' in self.dataset or not 'jahresgehalt' in self.dataset:

            for gehaltsmeldung in glob.glob("*/gehalt*"+self.dataset["meldejahr"]+"*_*.md"):
#                print(gehaltsmeldung)
                m = re.search(r"_(\d\d\d\d)_(\d\d)",gehaltsmeldung)
                if m:
                    monat       = int(m.group(2))
                    beginnmonat = min(beginnmonat,monat)
                    if monat > endmonat:
                        endmonat = monat
                        text     = open(gehaltsmeldung).read()

                        m = re.search(r"Zahlung +KUG(.*?)(\d+\.\d\d) +(\d+\.\d\d)",text)
                        if m:
                            self.dataset["zahlungkug"] = m.group(3).replace(".",",")
                               
                        m = re.search(r"Gehalt +Brutto(.*?)(\d+\.\d\d) +(\d+\.\d\d)",text)
                        if m:
                            bruttogehalt = m.group(3).replace(".",",")
                               
                        m = re.search(r"fiktives +Gehalt(.*?)\((\d+\.\d\d)\) +\((\d+\.\d\d)\)",text)
                        if not m:
                            jahresgehalt = bruttogehalt
                        else:
                            jahresgehalt = m.group(3).replace(".",",")
                            print(jahresgehalt)
                            
                        self.read_sozialabgaben(text,"LS",        "lohnsteuer")
                        self.read_sozialabgaben(text,"SZ",        "soli")
                        self.read_sozialabgaben(text,"KI",        "kirchensteuer")
                        self.read_sozialabgaben(text,"AN-KV",     "ankv")
                        self.read_sozialabgaben(text,"AN-RV",     "anrv")
                        self.read_sozialabgaben(text,"AN-AV",     "anav")
                        self.read_sozialabgaben(text,"AN-PV",     "anpv")
                        self.read_sozialabgaben(text,"AR-KV",     "arkv")
                        self.read_sozialabgaben(text,"AR-RV",     "arrv")
                        self.read_sozialabgaben(text,"AR-AV",     "arav")
                        self.read_sozialabgaben(text,"AR-PV",     "arpv")


            if self.dataset["meldung"] == "70":
                self.dataset["meldejahr"] = "20" + self.yy
                beginnmonat = int(self.jahr)
                endmonat    = int(self.jahr)
#                self.dataset["meldejahr"] = "20" + self.dataset["meldejahr"][0:2]


            if len(self.dataset["meldejahr"]) < 4:
                self.dataset["meldejahr"] = "20" + self.dataset["meldejahr"]

            print(self.dataset["meldejahr"],beginnmonat,endmonat)


            beginn = "01." + re.sub(r"13","01",("%02u"%beginnmonat))  + "." + self.dataset["meldejahr"]
            ende   = "."   + ("%02u"%endmonat)     + "." + self.dataset["meldejahr"]
            if endmonat in (1,3,5,7,8,10,12):
                ende = "31" + ende
            elif endmonat in (4,6,9,11):
                ende = "30" + ende
            elif int(self.dataset["meldejahr"]) % 4 == 0 and not int(self.dataset["meldejahr"]) % 100 == 0:
                ende = "29" + ende
            else:
                ende = "28" + ende
                
            print(beginn,ende)
#            return()

            self.dataset['beginn']         = beginn
            self.dataset['ende']           = ende
            self.dataset['jahresgehalt']   = jahresgehalt
            self.dataset['bruttogehalt']   = bruttogehalt
            self.dataset['jahresgehalt0']  = re.sub(r",\d+$","",jahresgehalt)
            self.dataset['bruttogehalt0']  = re.sub(r",\d+$","",bruttogehalt)
        
        print(self.dataset)
        
        if self.dataset["meldung"] in ("10","30","50","92","01"):

            self.dataset["adresse"] = self.dataset["strasse"]
            m = re.search(r"^(.*) +(\d+[a-zA-Z]?) *$",self.dataset['strasse'])
            if m:
                self.dataset['strasse'] = m.group(1)
                self.dataset['hausnr']  = m.group(2)
            if not 'hausnr' in self.dataset:
                self.dataset['hausnr']  = ""

            self.dataset["lohnstid"] = re.sub(r" ","",self.dataset["lohnstid"],9999)

        if self.dataset["meldung"] in ("10","30","50","92","70"):

            self.driver.get("https://standard.gkvnet-ag.de/svnet/")
            self.driver.set_window_size(1600, 1000)
            time.sleep(2)
            self.el("[aria-labelledby='loginDialogLabelBetriebsnummer']").send_keys(self.dataset["betriebsnummer"])
            self.el("[aria-labelledby='loginDialogLabelBenutzername']")  .send_keys(self.dataset["user_soz"])
            self.el("[aria-labelledby='loginDialogLabelPasswort']")      .send_keys(self.dataset["password_soz"])
            self.xp("//div[text()='Anmelden']").click()
            time.sleep(2)
            self.el("[aria-labelledby='overviewViewformulareLabel']")    .click()
            time.sleep(2)

        if self.dataset["meldung"] == "70":   #  Beitragsnachweis

            self.el("[aria-labelledby='overviewViewbna_menuLabel']").click()
            if "minijob" in self.dataset: 
                print("MINIJOB")
                self.el("[aria-labelledby='overviewViewbnaGering_viewEntryLabel']").click()
            else:
                self.el("[aria-labelledby='overviewViewbna_viewEntryLabel']")    .click()
            time.sleep(1)
#            self.id("[aria-labelledby='overviewViewbna_viewEntryLabel']")    .click()
            

        if self.dataset["meldung"] == "10":

            self.el("[aria-labelledby='overviewViewduaLabel']")    .click()
            self.el("[aria-labelledby='overviewViewanmeldungLabel']")    .click()
            time.sleep(1)
            self.el("[aria-labelledby='overviewViewm10Label']")    .click()
            

        if self.dataset["meldung"] == "50":

            self.el("[aria-labelledby='overviewViewduaLabel']")    .click()
            self.el("[aria-labelledby='overviewViewjahresmeldungLabel']")    .click()
            time.sleep(1)
            self.el("[aria-labelledby='overviewViewm50Label']")    .click()

        if self.dataset["meldung"] == "92":
        
            self.el("[aria-labelledby='overviewViewduaLabel']")    .click()
            self.el("[aria-labelledby='overviewViewjahresmeldungLabel']")    .click()
            time.sleep(1)
            self.el("[aria-labelledby='overviewViewm92Label']")    .click()
            self.dataset['beginn'] = "01.01." + self.dataset["meldejahr"]
            self.dataset['ende']   = "31.12." + self.dataset["meldejahr"]

        if self.dataset["meldung"] == "30":

            self.el("[aria-labelledby='overviewViewduaLabel']")    .click()
            self.el("[aria-labelledby='overviewViewabmeldungLabel']")    .click()
            time.sleep(1)
            self.el("[aria-labelledby='overviewViewm30Label']")    .click()


        if self.dataset["meldung"] in ("10","30","50","92"):

            time.sleep(2)
            self.driver.switch_to.frame(1)
            time.sleep(1)

            self.set_par("firmaBetriebsnummer",            ".betriebsnummer")
            self.set_par("firmaName1",                     ".firmaname1")
            self.set_par("firmaName2",                     ".firmaname2")
            self.set_par("firmaStrasse",                   ".firmaadresse")
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


        if self.dataset["meldung"] in ("70"):

            time.sleep(2)
            self.driver.switch_to.frame(1)
            time.sleep(1)

            self.set_par("firmaBetriebsnummer",            ".betriebsnummer")
            try:
                self.set_par("firmaSteuernummer",              ".steuernummer")
            except:
                pass
            self.set_par("firmaName1",                     ".firmaname1")
            self.set_par("firmaName2",                     ".firmaname2")
            self.set_par("firmaStrasse",                   ".firmaadresse")
            self.set_par("firmaLand",                      ".firmaland")
            self.set_par("firmaPostleitzahl",              ".firmaplz")
            self.set_par("firmaOrt",                       ".firmastadt")
            self.set_par("firmaRechtskreis",               ".rechtskreis")
            self.set_par("betriebsnummerKrankenkasse",     ".kkbetrnr")
            self.set_par("beginn",                         ".beginn")
            self.set_par("ende",                           ".ende")

            erg = self.auswertung(int(self.monatsanzahl))

            print("MM2",self.monatsanzahl)
            print(erg)

            self.set_par1("beitrag1000",                    erg,"KV")
            self.set_par1("beitragZusatzKrankenvers",       erg,"KV-ZUS")
            self.set_par1("beitrag0100",                    erg,"RV")
            self.set_par1("beitrag0010",                    erg,"AV")
            self.set_par1("beitrag0001",                    erg,"PV")
            self.set_par1("beitragU1",                      erg,"U1")
            self.set_par1("beitragU2",                      erg,"U2")
            self.set_par1("beitrag0050",                    erg,"U3")

            self.set_par1("beitrag6000",                    erg,"KV")
            self.set_par1("beitrag0500",                    erg,"XV")
            self.set_par1("beitragPauschsteuer",            erg,"ST")

            self.set_par1("beitrag0050",                    erg,"U3")   #  um den Gesamtbetrag zu aktualisieren


        if self.dataset["meldung"] in ("10","30","50"):

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


        if "sozversnr" in self.dataset and self.dataset["sozversnr"] == "":

            self.set_par("personGeburtsName",              ".gebname")
            self.set_par("personGeburtsVorsatz",           "")
            self.set_par("personGeburtsZusatz",            "")
            self.set_par("personGeburtsdatum",             ".gebdat")
            self.set_par("personGeburtsOrt",               ".gebort")
            self.set_par("personGeschlecht",               ".mw")

#       Abmeldung / Jahresmeldung:

        if self.dataset["meldung"] in ("30","50"):

            if self.dataset["persgruppe"] == "109":
                self.set_par("besteuerungsArt",                ".pauschsteuer")
                self.set_par("firmaSteuernummer",              ".firmasteuernummer")
                self.set_par("identifikationsNrArbeitnehmer",  ".lohnstid")

            self.set_par("ende",                           ".ende")
#            self.set_par("entgeltRentenberechnung",        ".betrag")
#            self.set_par("waehrung",                       "E")
            self.set_par("entgelt",                        ".jahresgehalt0")
            self.set_par("gleitzone",                      ".gleitzone")   #  0,1,2  nein/ja/teils



#       Anmeldung

        if self.dataset["meldung"] == "10" and not self.dataset["persgruppe"] == "109": 

            self.set_par("kennzeichenSaisonArbeitnehmer",  "N")
            
            
#       UV-Jahresmeldung:

        if self.dataset["meldung"] == "92": 

            self.set_par("uvData.0.betriebsnummerUV",               ".betriebsnummeruv")
            time.sleep(1)
            self.set_par("uvData.0.firmaMitgliedsnummerUV",         ".mitgliedsnummeruv")
            self.set_par("uvData.0.grund",                          ".grunduv")
            self.set_par("uvData.0.betriebsnummerGefahrtarifstelle",".betriebsnrgefahr")
            self.set_par("uvData.0.gefahrtarifstelle",              ".gefahrtarifstelle")
            self.set_par("uvData.0.arbeitsentgelt",                 ".bruttogehalt0")

        if "storno" in self.dataset and self.dataset["storno"][0] == "J":
        
            self.xp("//label[text()='Stornierung']").click()
            self.set_par("datensatzIdUrsprungsmeldung",             ".datensatzid")
            
            
            
        if self.dataset["meldung"] == "01":     #   Lohnsteuerjahresbescheinigung
        
            self.driver.get("https://www.elster.de/eportal/start")
            self.driver.set_window_size(1600, 1000)
            self.id("loginButtonStart").click()
            self.id("durchsuchen").click()

            self.set_par("loginBox.file_cert",                 ".certfile")
            time.sleep(1)
            self.set_par("password",                           ".password_steu")
            self.el("#bestaetigenButton > span").click()
            time.sleep(8)

            try:
                self.id("temporaereaufgaben_nein_button").click()
            except:
                pass

            self.id("linkid_navi_formulare-leistungen").click()
            self.id("linkid_navi_formulare-leistungen_alleformulare").click()
            self.el(".toggleBox:nth-child(10) .toggleBox__title").click()
            self.li("Lohnsteuerbescheinigung (Neu/Korrektur)").click()

            self.id("zeitraumJahr").click()
            el1 = self.id("zeitraumJahr")
            el1.find_element(By.XPATH, "//option[. = '"+self.ankerjahr+"']").click()
            print("MELDEJAHR",self.dataset["meldejahr"])
            nr = int(self.ankerjahr) - int(self.dataset["meldejahr"]) + 1
            self.el("option:nth-child("+str(nr)+")").click()
            self.id("Enter").click()
            self.id("Continue").click()

            self.id("Startseite(0)_fields(eruLStBLohnsteuerbescheinigungAnweisungart)").click()
            dropdown = self.id("Startseite(0)_fields(eruLStBLohnsteuerbescheinigungAnweisungart)")
            dropdown.find_element(By.XPATH, "//option[. = 'Neu']").click()

            self.id("dialogeruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberArbGStNr-country").click()
            dropdown = self.id("dialogeruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberArbGStNr-country")
            dropdown.find_element(By.XPATH, "//option[. = 'Bayern']").click()

            stnrel = self.dataset["firmasteuernummer"].split("/")

            self.set_par("dialogeruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberArbGStNr-tax-number-tax-office",                         stnrel[0])
            self.set_par("dialogeruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberArbGStNr-tax-number-destrict",                           stnrel[1])
            self.set_par("dialogeruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberArbGStNr-tax-number-distinction-number",                 stnrel[2])
            self.el("#NextPage .interactive-icon__text").click()

            self.set_par("Startseite(0)_AngabenArbeitgeber(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberArbGName)",         ".firmakurzname")
            self.set_par("Startseite(0)_AngabenArbeitgeber(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberAdresseStr)",       ".firmastrasse")
            self.set_par("Startseite(0)_AngabenArbeitgeber(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberAdresseHausnummer)",".firmahausnr")
            self.set_par("Startseite(0)_AngabenArbeitgeber(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberAdressePLZ)",       ".firmaplz")
            self.set_par("Startseite(0)_AngabenArbeitgeber(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberAdresseOrt)",       ".firmastadt")
            self.el("#NextPage .interactive-icon__text").click()

            self.set_par("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinIdNr)",                                    ".lohnstid")
            try:
                self.set_par("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinETIN)",                                    ".etin")
            except:
                pass
            self.set_par("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinOrdnungsmerkmal)",                         ".account")
            dropdown = self.id("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersongeschlecht)")
            if self.dataset["mw"].upper() == "M":
                dropdown.find_element(By.XPATH, "//option[. = 'männlich']").click()
            else:
                dropdown.find_element(By.XPATH, "//option[. = 'weiblich']").click()
            self.set_par("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonGeburtsdatum)",                      ".gebdat")
            self.set_par("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameName)",                  ".name")
            self.set_par("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameTitel)")
            self.set_par("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameVorname)",               ".vorname")
            self.set_par("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdresseStr)",                        ".strasse")
            self.set_par("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdresseHausnummer)",                 ".hausnr")
            self.set_par("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdressePLZ)",                        ".plz")
            self.set_par("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdresseOrt)",                        ".stadt")
            self.set_par("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdresselaenderkennzeichen)")
            self.el("#NextPage .interactive-icon__text").click()


            zaehler = 0
            kirchensteuer_anzugeben = 0
            while zaehler < 1:

                lohnsteuermerkmale    = self.dataset["lohnstkl"].split("/")
                lohnsteuerklasse      = lohnsteuermerkmale[0]
                kinderfreibetrag      = re.sub(r"\.",",",re.sub(r"-","",lohnsteuermerkmale[1]))
                kirchensteuermerkmale = lohnsteuermerkmale[2]

                self.el(".mzb__info").click()
                self.el("#JumpToPage\\/Startseite\\[0\\]\\/Besteuerungsmerkmale\\[0\\]\\/MZBBesteuerungsmerkmaleMZB\\[0\\] .interactive-icon__text").click()
                self.set_par("Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMgueltig_ab)",".beginn")
                dropdown = self.id("Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMSteuerklasse)")
                dropdown.find_element(By.XPATH, "//option[. = '"+lohnsteuerklasse+"']").click()
                dropdown = self.id("Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMKinder)")
                dropdown.find_element(By.XPATH, "//option[. = '"+kinderfreibetrag+"']").click()
                self.el("#Startseite\\(0\\)_Besteuerungsmerkmale\\(0\\)_MZBBesteuerungsmerkmaleMZB\\(0\\)_fields\\(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMKinder\\) > option:nth-child(2)").click()
                dropdown = self.id("Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMKirchensteuerabzugkonfession)")

                if "e" in kirchensteuermerkmale:
                    dropdown.find_element(By.XPATH, "//option[. = 'Evangelische Kirchensteuer - ev']").click()
                    kirchensteuer_anzugeben = 1
                elif "k" in kirchensteuermerkmale:
                    dropdown.find_element(By.XPATH, "//option[. = 'Römisch-Katholische Kirchensteuer - rk']").click()
                    kirchensteuer_anzugeben = 1
                else:
                    dropdown.find_element(By.XPATH, "//option[. = '--']").click()
                self.el("#NextPage .interactive-icon__text").click()
                
                zaehler = zaehler + 1
                

            self.el("#NextPage .interactive-icon__text").click()
            
            self.set_par("Startseite(0)_ArbeitslohnAbzuege(0)_fields(eruLStBLohnsteuerbescheinigungDauerAnfang)",                                         ".beginn")
            self.set_par("Startseite(0)_ArbeitslohnAbzuege(0)_fields(eruLStBLohnsteuerbescheinigungDauerEnde)",                                           ".ende")
            self.set_par("Startseite(0)_ArbeitslohnAbzuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenBruttoArbLohn)",                 ".bruttogehalt")
            self.set_par("Startseite(0)_ArbeitslohnAbzuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenLSteuer)",                       ".lohnsteuer")
            self.set_par("Startseite(0)_ArbeitslohnAbzuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSoli)",                          ".soli")
            if kirchensteuer_anzugeben == 1:
                self.set_par("Startseite(0)_ArbeitslohnAbzuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbnKiSteuer)",                  ".kirchensteuer")
            self.set_par("Startseite(0)_ArbeitslohnAbzuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenEhegKiSteuer)")
            self.el("#NextPage .interactive-icon__text").click()

            self.set_par("Startseite(0)_VersorgungsbezErmArblohn(0)_Versorgungsbezuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenVersorgungsbezgeVBez)")
            self.set_par("Startseite(0)_VersorgungsbezErmArblohn(0)_Versorgungsbezuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenVersorgungsbezgebmgfreibetrag)")
            self.set_par("Startseite(0)_VersorgungsbezErmArblohn(0)_Versorgungsbezuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenVersorgungsbezgejahr)")
            self.set_par("Startseite(0)_VersorgungsbezErmArblohn(0)_Versorgungsbezuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenVersorgungsbezgebeginn)") 
            self.set_par("Startseite(0)_VersorgungsbezErmArblohn(0)_Versorgungsbezuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenVersorgungsbezgeende)")
            self.set_par("Startseite(0)_VersorgungsbezErmArblohn(0)_Versorgungsbezuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenVersorgungsbezgeeinmversbezug)")
            self.set_par("Startseite(0)_VersorgungsbezErmArblohn(0)_ErmBestVersbezuegeMKal(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenK_ErmStVBezMKalJahrErmStVBezMKalJahr)")
            self.set_par("Startseite(0)_VersorgungsbezErmArblohn(0)_ErmBestVersbezuegeMKal(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenK_ErmStVBezMKalJahrjahr)")
            self.set_par("Startseite(0)_VersorgungsbezErmArblohn(0)_NichtErmBestVersbezuegeMKal(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenK_NErmStVBezMKalJahrNErmStVBezMKalJahr)")
            self.set_par("Startseite(0)_VersorgungsbezErmArblohn(0)_NichtErmBestVersbezuegeMKal(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenK_NErmStVBezMKalJahrjahr)")
            self.set_par("Startseite(0)_VersorgungsbezErmArblohn(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenErmStBetrMKalJahr)")
            self.set_par("Startseite(0)_VersorgungsbezErmArblohn(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenLSteuerMKalJahr)")
            self.set_par("Startseite(0)_VersorgungsbezErmArblohn(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSoliMKalJahr)")
            self.set_par("Startseite(0)_VersorgungsbezErmArblohn(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenKiSteuerArbnMKalJahr)")
            self.set_par("Startseite(0)_VersorgungsbezErmArblohn(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenKiSteuerEhegMKalJahr)")
            self.el("#NextPage .interactive-icon__text").click()

            try:
                self.set_par("Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenKurzArbGeld)",                                          ".zahlungkug")
            except:
                pass
            self.set_par("Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenStFreiGeKrankVers)")
            self.set_par("Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenStFreiPrKrankVers)")
            self.set_par("Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenStFreiGePflegeVers)")
            self.set_par("Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenArbnAnteilKrankVers)",     ".ankv")
            self.set_par("Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenArbnAnteilPflegVers)",     ".anpv")
            self.set_par("Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenArbnAnteilArblVers)",      ".anav")
            self.set_par("Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenArbnAnteilRenVers)",       ".anpv")
            self.set_par("Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenArbnAnteilBerufsVers)")
            self.set_par("Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenArbgAnteilRenVers)",       ".arrv")
            self.set_par("Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenBeitrPrKrankVers)")
            self.set_par("Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenArbgAnteilBerufsVers)")
            self.set_par("Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenAusgezKinderGeld)")
            self.set_par("Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenFreibetragDbaTuerkei)")
            self.el("#NextPage .interactive-icon__text").click()

            self.set_par("Startseite(0)_FreiwilligeAngaben(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbnAnteilWBUmlage)")
            self.set_par("Startseite(0)_FreiwilligeAngaben(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbgAnteilZusatzVers)")
            self.set_par("Startseite(0)_FreiwilligeAngaben(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenAnzahlArbTag)")
            self.set_par("Startseite(0)_FreiwilligeAngaben(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenStFreiFahrtKAusw)")
            self.set_par("Startseite(0)_FreiwilligeAngaben(0)_ArbgFreiwilligeWerte(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenFreierWertname)")
            self.set_par("Startseite(0)_FreiwilligeAngaben(0)_ArbgFreiwilligeWerte(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenFreierWertWert)")
            self.set_par("Startseite(0)_FreiwilligeAngaben(0)_ArbgFreiwilligeTexte(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenFreierTextname)")
            self.set_par("Startseite(0)_FreiwilligeAngaben(0)_ArbgFreiwilligeTexte(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenFreierTextText)")

            '''

      "target": "/eportal/login/softpse",
      "target": "971x807",
      "target": "id=durchsuchen",
      "target": "id=loginBox.file_cert",
      "target": "id=password",
      "target": "id=password",
      "target": "css=#bestaetigenButton > span",
      "target": "id=temporaereaufgaben_nein_button",
      "target": "css=#linkid_navi_formulare-leistungen .interactive-icon__text",
      "target": "id=linkid_navi_formulare-leistungen_alleformulare",
      "target": "css=.toggleBox:nth-child(9) .toggleBox__title",
      "target": "linkText=Lohnsteuerbescheinigung (Neu/Korrektur)",
      "target": "id=zeitraumJahr",
      "target": "id=zeitraumJahr",
      "target": "css=option:nth-child(4)",
      "target": "id=Enter",
      "target": "css=.page-default__row:nth-child(3) > .page-default__main",
      "target": "id=Continue",
      "target": "id=Startseite(0)_fields(eruLStBLohnsteuerbescheinigungAnweisungart)",
      "target": "id=Startseite(0)_fields(eruLStBLohnsteuerbescheinigungAnweisungart)",
      "target": "css=#Startseite\\(0\\)_fields\\(eruLStBLohnsteuerbescheinigungAnweisungart\\) > option:nth-child(3)",
      "target": "id=Startseite(0)_fields(eruLStBLohnsteuerbescheinigungAnweisungRefKmId)",
      "target": "id=Startseite(0)_fields(eruLStBLohnsteuerbescheinigungAnweisungRefKmId)",
      "target": "css=.page-form__row:nth-child(3)",
      "target": "id=dialogeruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberArbGStNr-country",
      "target": "id=dialogeruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberArbGStNr-country",
      "target": "css=#dialogeruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberArbGStNr-country > option:nth-child(3)",
      "target": "id=dialogeruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberArbGStNr-tax-number-tax-office",
      "target": "id=dialogeruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberArbGStNr-tax-number-tax-office",
      "target": "id=dialogeruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberArbGStNr-tax-number-destrict",
      "target": "id=dialogeruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberArbGStNr-tax-number-distinction-number",
      "target": "css=.page-form__row:nth-child(3)",
      "target": "css=#NextPage .interactive-icon__text",
      "target": "id=Startseite(0)_AngabenArbeitgeber(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberArbGName)",
      "target": "id=Startseite(0)_AngabenArbeitgeber(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberArbGName)",
      "target": "id=Startseite(0)_AngabenArbeitgeber(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberAdresseStr)",
      "target": "id=Startseite(0)_AngabenArbeitgeber(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberAdresseStr)",
      "target": "id=Startseite(0)_AngabenArbeitgeber(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberAdresseHausnummer)",
      "target": "id=Startseite(0)_AngabenArbeitgeber(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberAdresseHNrZusatz)",
      "target": "id=Startseite(0)_AngabenArbeitgeber(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberAdresseAnschriftenzusatz)",
      "target": "id=Startseite(0)_AngabenArbeitgeber(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberAdressePLZ)",
      "target": "id=Startseite(0)_AngabenArbeitgeber(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberAdressePLZ)",
      "target": "id=Startseite(0)_AngabenArbeitgeber(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberAdresseOrt)",
      "target": "id=Startseite(0)_AngabenArbeitgeber(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberAdresseAuslandsPLZ)",
      "target": "id=Startseite(0)_AngabenArbeitgeber(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberAdresseAuslandsPLZ)",
      "target": "css=.page-form__row:nth-child(4)",
      "target": "id=Startseite(0)_AngabenArbeitgeber(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberAdresselaenderkennzeichen)",
      "target": "id=Startseite(0)_AngabenArbeitgeber(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberAdresselaenderkennzeichen)",
      "target": "css=option:nth-child(7)",
      "target": "css=.page-form__row:nth-child(4)",
      "target": "css=#NextPage .interactive-icon__text",
      "target": "css=.page-form__row:nth-child(4)",
      "target": "id=Startseite(0)_AngabenArbeitgeber(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberAdresseAuslandsPLZ)",
      "target": "id=Startseite(0)_AngabenArbeitgeber(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberAdresseAuslandsPLZ)",
      "target": "id=Startseite(0)_AngabenArbeitgeber(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberAdresselaenderkennzeichen)",
      "target": "id=Startseite(0)_AngabenArbeitgeber(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberAdresselaenderkennzeichen)",
      "target": "css=option:nth-child(1)",
      "target": "css=#NextPage .interactive-icon__text",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinIdNr)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinIdNr)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinETIN)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinETIN)",
      "target": "css=.page-form__row:nth-child(4)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinETIN)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinOrdnungsmerkmal)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinOrdnungsmerkmal)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameart)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameart)",
      "target": "css=#Startseite\\(0\\)_AngabenArbeitnehmer\\(0\\)_fields\\(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameart\\) > option:nth-child(3)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameBlockname)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameBlockname)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersongeschlecht)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersongeschlecht)",
      "target": "css=#Startseite\\(0\\)_AngabenArbeitnehmer\\(0\\)_fields\\(eruLStBLohnsteuerbescheinigungAllgemeinPersongeschlecht\\) > option:nth-child(3)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameTitel)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameTitel)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameName)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameName)",
      "target": "css=.page-form__row:nth-child(4)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameVorname)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameVorname)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameNamensvorsatz)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameNamensvorsatz)",
      "target": "css=#Startseite\\(0\\)_AngabenArbeitnehmer\\(0\\)_fields\\(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameNamensvorsatz\\) > option:nth-child(13)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameNamenszusatz)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameNamenszusatz)",
      "target": "css=#Startseite\\(0\\)_AngabenArbeitnehmer\\(0\\)_fields\\(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameNamenszusatz\\) > option:nth-child(11)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonGeburtsdatum)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonGeburtsdatum)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonGeburtsnameName)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonGeburtsnameName)",
      "target": "css=.page-form__row:nth-child(4)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonGeburtsnameNamensvorsatz)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonGeburtsnameNamensvorsatz)",
      "target": "css=#Startseite\\(0\\)_AngabenArbeitnehmer\\(0\\)_fields\\(eruLStBLohnsteuerbescheinigungAllgemeinPersonGeburtsnameNamensvorsatz\\) > option:nth-child(8)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonGeburtsnameNamenszusatz)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonGeburtsnameNamenszusatz)",
      "target": "css=#Startseite\\(0\\)_AngabenArbeitnehmer\\(0\\)_fields\\(eruLStBLohnsteuerbescheinigungAllgemeinPersonGeburtsnameNamenszusatz\\) > option:nth-child(14)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdresseStr)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdresseStr)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdresseHausnummer)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdresseHNrZusatz)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdresseAnschriftenzusatz)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdressePLZ)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdressePLZ)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdresseOrt)",
      "target": "css=.page-form__row:nth-child(4)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdresseAuslandsPLZ)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdresseAuslandsPLZ)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdresselaenderkennzeichen)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdresselaenderkennzeichen)",
      "target": "css=#Startseite\\(0\\)_AngabenArbeitnehmer\\(0\\)_fields\\(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdresselaenderkennzeichen\\) > option:nth-child(13)",
      "target": "css=#NextPage .interactive-icon__text",
      "target": "css=.page-form__row:nth-child(4)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameart)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameart)",
      "target": "css=#Startseite\\(0\\)_AngabenArbeitnehmer\\(0\\)_fields\\(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameart\\) > option:nth-child(1)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameBlockname)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameBlockname)",
      "target": "css=.page-form__row:nth-child(4)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdresseAuslandsPLZ)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdresseAuslandsPLZ)",
      "target": "css=.page-form__row:nth-child(4)",
      "target": "css=#NextPage .interactive-icon__text",
      "target": "id=correctnow",
      "target": "css=.page-form__row:nth-child(4)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdresselaenderkennzeichen)",
      "target": "id=Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdresselaenderkennzeichen)",
      "target": "css=#Startseite\\(0\\)_AngabenArbeitnehmer\\(0\\)_fields\\(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdresselaenderkennzeichen\\) > option:nth-child(1)",
      "target": "css=.page-form__row:nth-child(4)",
      "target": "css=#NextPage .interactive-icon__text",
      "target": "css=#JumpToPage\\/Startseite\\[0\\]\\/Besteuerungsmerkmale\\[0\\]\\/MZBBesteuerungsmerkmaleMZB\\[0\\] .interactive-icon__text",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMgueltig_ab)",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMgueltig_ab)",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMSteuerklasse)",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMSteuerklasse)",
      "target": "css=#Startseite\\(0\\)_Besteuerungsmerkmale\\(0\\)_MZBBesteuerungsmerkmaleMZB\\(0\\)_fields\\(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMSteuerklasse\\) > option:nth-child(6)",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMfaktor)",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMfaktor)",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMKinder)",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMfaktor)",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMfaktor)",
      "target": "css=.page-form__row:nth-child(4)",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMKinder)",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMKinder)",
      "target": "css=#Startseite\\(0\\)_Besteuerungsmerkmale\\(0\\)_MZBBesteuerungsmerkmaleMZB\\(0\\)_fields\\(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMKinder\\) > option:nth-child(7)",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMKirchensteuerabzugkonfession)",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMKirchensteuerabzugkonfession)",
      "target": "css=#Startseite\\(0\\)_Besteuerungsmerkmale\\(0\\)_MZBBesteuerungsmerkmaleMZB\\(0\\)_fields\\(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMKirchensteuerabzugkonfession\\) > option:nth-child(4)",
      "target": "css=.page-form__row:nth-child(4)",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMKirchensteuerabzugehegkonfession)",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMKirchensteuerabzugehegkonfession)",
      "target": "css=#Startseite\\(0\\)_Besteuerungsmerkmale\\(0\\)_MZBBesteuerungsmerkmaleMZB\\(0\\)_fields\\(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMKirchensteuerabzugehegkonfession\\) > option:nth-child(4)",
      "target": "css=.page-form__row:nth-child(4)",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMSteuerfreibetragjahr)",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMSteuerfreibetragjahr)",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMSteuerfreibetragjahr)",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMSteuerfreibetragjahr)",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMSteuerfreibetragmonat)",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMSteuerfreibetragwoche)",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMSteuerfreibetragtag)",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMSteuerfreibetragjahr)",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMSteuerfreibetragwoche)",
      "target": "css=.page-form__row:nth-child(4)",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMHinzurechnungsbetragjahr)",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMHinzurechnungsbetragjahr)",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMHinzurechnungsbetragmonat)",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMHinzurechnungsbetragwoche)",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMHinzurechnungsbetragtag)",
      "target": "css=#NextPage .interactive-icon__text",
      "target": "css=.page-form__row:nth-child(4)",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMfaktor)",
      "target": "id=Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMfaktor)",
      "target": "css=.page-form__row:nth-child(4)",
      "target": "css=#NextPage .interactive-icon__text",
      "target": "css=#NextPage .interactive-icon__text",
      "target": "id=Startseite(0)_ArbeitslohnAbzuege(0)_fields(eruLStBLohnsteuerbescheinigungDauerAnfang)",
      "target": "id=Startseite(0)_ArbeitslohnAbzuege(0)_fields(eruLStBLohnsteuerbescheinigungDauerAnfang)",
      "target": "id=Startseite(0)_ArbeitslohnAbzuege(0)_fields(eruLStBLohnsteuerbescheinigungDauerEnde)",
      "target": "id=Startseite(0)_ArbeitslohnAbzuege(0)_fields(eruLStBLohnsteuerbescheinigungDauerEnde)",
      "target": "css=.page-form__row:nth-child(4)",
      "target": "id=Startseite(0)_ArbeitslohnAbzuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenBruttoArbLohn)",
      "target": "id=Startseite(0)_ArbeitslohnAbzuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenBruttoArbLohn)",
      "target": "id=Startseite(0)_ArbeitslohnAbzuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenLSteuer)",
      "target": "id=Startseite(0)_ArbeitslohnAbzuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenLSteuer)",
      "target": "id=Startseite(0)_ArbeitslohnAbzuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSoli)",
      "target": "id=Startseite(0)_ArbeitslohnAbzuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSoli)",
      "target": "id=Startseite(0)_ArbeitslohnAbzuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbnKiSteuer)",
      "target": "id=Startseite(0)_ArbeitslohnAbzuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbnKiSteuer)",
      "target": "id=Startseite(0)_ArbeitslohnAbzuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenEhegKiSteuer)",
      "target": "id=Startseite(0)_ArbeitslohnAbzuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenEhegKiSteuer)",
      "target": "css=#NextPage .interactive-icon__text",
      "target": "id=Startseite(0)_VersorgungsbezErmArblohn(0)_Versorgungsbezuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenVersorgungsbezgeVBez)",
      "target": "id=Startseite(0)_VersorgungsbezErmArblohn(0)_Versorgungsbezuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenVersorgungsbezgeVBez)",
      "target": "id=Startseite(0)_VersorgungsbezErmArblohn(0)_Versorgungsbezuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenVersorgungsbezgebmgfreibetrag)",
      "target": "id=Startseite(0)_VersorgungsbezErmArblohn(0)_Versorgungsbezuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenVersorgungsbezgejahr)",
      "target": "id=Startseite(0)_VersorgungsbezErmArblohn(0)_Versorgungsbezuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenVersorgungsbezgejahr)",
      "target": "id=Startseite(0)_VersorgungsbezErmArblohn(0)_Versorgungsbezuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenVersorgungsbezgebeginn)",
      "target": "id=Startseite(0)_VersorgungsbezErmArblohn(0)_Versorgungsbezuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenVersorgungsbezgebeginn)",
      "target": "id=Startseite(0)_VersorgungsbezErmArblohn(0)_Versorgungsbezuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenVersorgungsbezgeende)",
      "target": "id=Startseite(0)_VersorgungsbezErmArblohn(0)_Versorgungsbezuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenVersorgungsbezgeende)",
      "target": "id=Startseite(0)_VersorgungsbezErmArblohn(0)_Versorgungsbezuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenVersorgungsbezgeeinmversbezug)",
      "target": "id=Startseite(0)_VersorgungsbezErmArblohn(0)_Versorgungsbezuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenVersorgungsbezgeeinmversbezug)",
      "target": "css=#CreateMzbItem\\/Startseite\\[0\\]\\/VersorgungsbezErmArblohn\\[0\\]\\/Versorgungsbezuege\\[0\\] .interactive-icon__text",
      "target": "id=Startseite(0)_VersorgungsbezErmArblohn(0)_ErmBestVersbezuegeMKal(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenK_ErmStVBezMKalJahrErmStVBezMKalJahr)",
      "target": "id=Startseite(0)_VersorgungsbezErmArblohn(0)_ErmBestVersbezuegeMKal(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenK_ErmStVBezMKalJahrErmStVBezMKalJahr)",
      "target": "id=Startseite(0)_VersorgungsbezErmArblohn(0)_ErmBestVersbezuegeMKal(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenK_ErmStVBezMKalJahrjahr)",
      "target": "id=Startseite(0)_VersorgungsbezErmArblohn(0)_ErmBestVersbezuegeMKal(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenK_ErmStVBezMKalJahrjahr)",
      "target": "css=.page-form__row:nth-child(4)",
      "target": "id=Startseite(0)_VersorgungsbezErmArblohn(0)_NichtErmBestVersbezuegeMKal(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenK_NErmStVBezMKalJahrNErmStVBezMKalJahr)",
      "target": "id=Startseite(0)_VersorgungsbezErmArblohn(0)_NichtErmBestVersbezuegeMKal(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenK_NErmStVBezMKalJahrNErmStVBezMKalJahr)",
      "target": "id=Startseite(0)_VersorgungsbezErmArblohn(0)_NichtErmBestVersbezuegeMKal(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenK_NErmStVBezMKalJahrjahr)",
      "target": "id=Startseite(0)_VersorgungsbezErmArblohn(0)_NichtErmBestVersbezuegeMKal(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenK_NErmStVBezMKalJahrjahr)",
      "target": "css=.page-form__row:nth-child(4)",
      "target": "id=Startseite(0)_VersorgungsbezErmArblohn(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenErmStBetrMKalJahr)",
      "target": "id=Startseite(0)_VersorgungsbezErmArblohn(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenErmStBetrMKalJahr)",
      "target": "id=Startseite(0)_VersorgungsbezErmArblohn(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenLSteuerMKalJahr)",
      "target": "id=Startseite(0)_VersorgungsbezErmArblohn(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenLSteuerMKalJahr)",
      "target": "id=Startseite(0)_VersorgungsbezErmArblohn(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSoliMKalJahr)",
      "target": "id=Startseite(0)_VersorgungsbezErmArblohn(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenKiSteuerArbnMKalJahr)",
      "target": "id=Startseite(0)_VersorgungsbezErmArblohn(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenKiSteuerEhegMKalJahr)",
      "target": "css=.page-form__row:nth-child(4)",
      "target": "css=#NextPage .interactive-icon__text",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenKurzArbGeld)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenKurzArbGeld)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenStFreiArbLohnDBA)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenStFreiArbLohnATE)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenStFreiArbgLeistg)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenStFreiArbgLeistg)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenPauschArbgLeistg)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenPauschArbgLeistg)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenStPflichtArbLohnMKalJahr)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenStPflichtArbLohnMKalJahr)",
      "target": "css=.page-form__row:nth-child(4)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenStFreiVerpfleg)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenStFreiVerpfleg)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenStFreiDopHaushalt)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenStFreiDopHaushalt)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenArbgAnteilRenVers)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenArbgAnteilBerufsVers)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenArbgAnteilBerufsVers)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenArbnAnteilRenVers)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenArbnAnteilRenVers)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenArbnAnteilBerufsVers)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenArbnAnteilBerufsVers)",
      "target": "css=.page-form__row:nth-child(4)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenStFreiGeKrankVers)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenStFreiGeKrankVers)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenStFreiGeKrankVers)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenStFreiPrKrankVers)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenStFreiPrKrankVers)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenStFreiGePflegeVers)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenStFreiGePflegeVers)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenArbnAnteilKrankVers)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenArbnAnteilKrankVers)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenArbnAnteilPflegVers)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenArbnAnteilPflegVers)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenArbnAnteilArblVers)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenArbnAnteilArblVers)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenBeitrPrKrankVers)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenBeitrPrKrankVers)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenAusgezKinderGeld)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenAusgezKinderGeld)",
      "target": "css=.page-form__row:nth-child(4)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenFreibetragDbaTuerkei)",
      "target": "id=Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenFreibetragDbaTuerkei)",
      "target": "css=#NextPage .interactive-icon__text",
      "target": "css=.page-form__row:nth-child(4)",
      "target": "id=Startseite(0)_FreiwilligeAngaben(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbnAnteilWBUmlage)",
      "target": "id=Startseite(0)_FreiwilligeAngaben(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbnAnteilWBUmlage)",
      "target": "id=Startseite(0)_FreiwilligeAngaben(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbgAnteilZusatzVers)",
      "target": "id=Startseite(0)_FreiwilligeAngaben(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbnAnteilZusatzVers)",
      "target": "id=Startseite(0)_FreiwilligeAngaben(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenAnzahlArbTag)",
      "target": "id=Startseite(0)_FreiwilligeAngaben(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenStFreiFahrtKAusw)",
      "target": "id=Startseite(0)_FreiwilligeAngaben(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenStFreiFahrtKAusw)",
      "target": "id=Startseite(0)_FreiwilligeAngaben(0)_ArbgFreiwilligeWerte(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenFreierWertname)",
      "target": "id=Startseite(0)_FreiwilligeAngaben(0)_ArbgFreiwilligeWerte(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenFreierWertname)",
      "target": "id=Startseite(0)_FreiwilligeAngaben(0)_ArbgFreiwilligeWerte(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenFreierWertWert)",
      "target": "css=.page-form__row:nth-child(4)",
      "target": "id=Startseite(0)_FreiwilligeAngaben(0)_ArbgFreiwilligeTexte(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenFreierTextname)",
      "target": "id=Startseite(0)_FreiwilligeAngaben(0)_ArbgFreiwilligeTexte(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenFreierTextname)",
      "target": "id=Startseite(0)_FreiwilligeAngaben(0)_ArbgFreiwilligeTexte(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenFreierTextText)",
      "target": "css=#SwitchModus .interactive-icon__text",

'''
        
#**********************************************************************************************************
         
    def read_sozialabgaben(self,text,id,dfield):
    
        m = re.search(id+" +\(?(\-?\d+\.\d\d)\)? +\(?(\-?\d+\.\d\d)\)? +\(?(\-?\d+\.\d\d)\)?",text)
        if m:
            self.dataset[dfield] = m.group(3).replace(".",",")
        else:
            self.dataset[dfield] = "0,00"
                            
#**********************************************************************************************************

    def read (self,file):
    
        os.system("pdftotext -layout " + file)
        text = open(file[:-4]+".txt").read()
        os.unlink(file[:-4] + ".txt")
        
        m = re.search(r"^(.*?Angaben +zu)(.*?)(Angaben +zu)(.*?)(Meldedaten)(.*?)(Angaben +zu)(.*)",text,re.DOTALL)
        
        text_firma  = m.group(1) + m.group(2)
        text_person = m.group(4)
        text_melde  = m.group(6)
        text_einzug = m.group(8)
        
        d1 = {}
        
        self.set_d1( re.search(r"sv.net +(\S+)"                                    ,text_firma),      "svnetversion"      )
        self.set_d1( re.search(r"TAN +(\d+)"                                       ,text_firma),      "tan"               )
        self.set_d1( re.search(r"Betriebsnummer +(\d+)"                            ,text_firma),      "betriebsnummer"    )
        self.set_d1( re.search(r"Name +(.+)"                                       ,text_firma),      "firmaname1"        )
        self.set_d1( re.search(r"Name +[^\n]+\n +([^\n]+)"                         ,text_firma),      "firmaname2"        )
        self.set_d1( re.search(r"Straße *\/ *Hausn\S+ +(.*)"                       ,text_firma),      "strasse"           )
        self.set_d1( re.search(r"Land *\/ *PLZ *\/ *Ort +(\S+) +(\S+) +(\S+)"      ,text_firma),      "firmaland"         )
        self.set_d1( re.search(r"Land *\/ *PLZ *\/ *Ort +\S+ +(\S+) +(\S+)"        ,text_firma),      "firmaplz"          )
        self.set_d1( re.search(r"Land *\/ *PLZ *\/ *Ort +\S+ +\S+ +(\S+)"          ,text_firma),      "firmastadt"        )

        self.set_d1( re.search(r"Versicherung\S+ +(\S+)"                           ,text_person),     "sozversnr"         )
        self.set_d1( re.search(r"Personal\S+ +(\S+)"                               ,text_person),     "account"           )
        self.set_d1( re.search(r"Name +(\S+)"                                      ,text_person),     "name"              )
        self.set_d1( re.search(r"Vorname +(\S+)"                                   ,text_person),     "vorname"           )
        self.set_d1( re.search(r"Straße *\/ *Hausn\S+ +(.*)"                       ,text_person),     "strasse"           )
        self.set_d1( re.search(r"Land *\/ *PLZ *\/ *Ort +(\S+) +(\S+) +(\S+)"      ,text_person),     "land"              )
        self.set_d1( re.search(r"Land *\/ *PLZ *\/ *Ort +\S+ +(\S+) +(\S+)"        ,text_person),     "plz"               )
        self.set_d1( re.search(r"Land *\/ *PLZ *\/ *Ort +\S+ +\S+ +(\S+)"          ,text_person),     "stadt"             )

        self.set_d1( re.search(r"Storni\S+ +(\S+)"                                 ,text_melde),      "stornierung"       )
        self.set_d1( re.search(r"Datensatz +ID +(.+)"                              ,text_melde),      "datensatzid"       )
        self.set_d1( re.search(r"Grund der Abgabe +(\d+)"                          ,text_melde),      "meldung"           )
        self.set_d1( re.search(r"Midijob +(\d+)"                                   ,text_melde),      "midijob"           )
        self.set_d1( re.search(r"Gleitzone +(\d+)"                                 ,text_melde),      "midijob"           )
        self.set_d1( re.search(r"Besch\S+ +von +(\S+)"                             ,text_melde),      "beginn"            )
        self.set_d1( re.search(r"Besch\S+ +bis +(\S+)"                             ,text_melde),      "ende"              )
        self.set_d1( re.search(r"Personengruppe +(\d+)"                            ,text_melde),      "persgruppe"        )
        self.set_d1( re.search(r"Art der Besteuerung +(\d+)"                       ,text_melde),      "pauschsteuer"      )
        self.set_d1( re.search(r"Steuernummer des +(\d+)"                          ,text_melde),      "firmasteuernummer" )
        self.set_d1( re.search(r"Krankenvers\S+ +(\d+)"                            ,text_melde),      "kv"                )
        self.set_d1( re.search(r"Rentenvers\S+ +(\d+)"                             ,text_melde),      "rv"                )
        self.set_d1( re.search(r"Arbeitslosenvers\S+ +(\d+)"                       ,text_melde),      "av"                )
        self.set_d1( re.search(r"Pflegevers\S+ +(\d+)"                             ,text_melde),      "pv"                )
        self.set_d1( re.search(r"T..?tigkei\S+ +(\d+)"                             ,text_melde),      "tschluessel"       )
        self.set_d1( re.search(r"Schulabschlu\S+ +(\d+)"                           ,text_melde),      "schule"            )
        self.set_d1( re.search(r"Berufsausb\S+ +(\d+)"                             ,text_melde),      "beruf"             )
        self.set_d1( re.search(r"AÜG +(\d+)"                                       ,text_melde),      "aueg"              )
        self.set_d1( re.search(r"(\d+)(.*?)wird nicht anderen"                     ,text_melde),      "aueg"              )
        self.set_d1( re.search(r"Vertrag\S+ +(\d+)"                                ,text_melde),      "vertrag"           )
        self.set_d1( re.search(r"Bruttoarb\S+ +(\S+)"                              ,text_melde),      "jahresgehalt"      )

        self.set_d1( re.search(r"Betriebsnummer +(\S+)"                            ,text_einzug),     "kkbetrnr"          )

        self.jahr              = "9999"
        self.meldung           = self.dataset["meldung"]
        self.dataset["storno"] = "Ja"
        
        if not "datensatzid" in self.dataset:
            if not "svnetversion" in self.dataset:
                self.dataset["svnetversion"] = "18.0.0.0"
            self.dataset["datensatzid"] = (self.dataset["svnetversion"].replace(".","",99) + "000000000000")[0:8] + "A 0" + self.dataset["tan"]

        if not "jahresgehalt" in self.dataset:
            self.dataset["jahresgehalt"] = "0"


#**************************************************************************************

    def set_d1 (self,m,key):
    
        if m:
            self.dataset[key] = m.group(1)
            
#**************************************************************************************

    def auswertung (self,faktor=1.0):

        konto.Konto().kto()

#        print("")
        print(glob.glob("*.kto"))
        erg = {}
        kv  = 0.00
        zus = 0.00
        for zeile in os.popen("grep -P '^([A-Z0-9]+|KV-Z|KV-meldZUS) +(\S+) *$' *.kto").read().split("\n"):
            print(zeile)
            m = re.search(r"^(\S+) +(.*)$",zeile)
            if not m:
                continue
            if m.group(1) == "KV":
                kv = float(m.group(2))
                erg["KV"] = re.sub(r"\.",",","%3.2f"%(-kv/faktor))
            elif m.group(1) == "KV-Z":
                zus = float(m.group(2))
                erg["KV-ZUS"] = re.sub(r"\.",",","%3.2f"%(-zus/faktor))
            elif m.group(1) == "KV-meldZUS":
                zus = zus + float(m.group(2))
                kv  = kv - zus
                erg["KV"]     = re.sub(r"\.",",","%3.2f"%(-kv/faktor))
                erg["KV-ZUS"] = re.sub(r"\.",",","%3.2f"%(-zus/faktor))
                print ("%-10s" % "KV" +     "%10.2f"%(kv/faktor))
                print ("%-10s" % "KV-ZUS" + "%10.2f"%(zus/faktor))
#            elif m.group(1) == "AV":
#                text = "%-10s" % m.group(1) + "%10.2f"%(float(m.group(2))/faktor)
#            elif m.group(1) == "PV":
#                text = text + "\n" + "%-10s" % m.group(1) + "%10.2f"%(float(m.group(2))/faktor)
            else:
                erg[m.group(1)] = re.sub(r"\.",",","%3.2f"%(-float(m.group(2))/faktor))
                print("%-10s" % m.group(1) + "%10.2f"%(float(m.group(2))/faktor))
#            if m.group(1) == "RV":
#                print(text)

        return(erg)

#**************************************************************************************
            

if __name__ == "__main__":

    r            = SV_Meldung().setup_method("")
#    config_data  = [ os.popen("python3 -m fibu.xlsmanager memory oa ./15*/*.csv aktuell").read() ]  #  personal data
    kto          = konto.Konto()
    kto.read_config(kto.base_dir+"/*.data")
    kto.read_config("../*.data")
    kto.read_config("./sv.data")
    kto.read_config("*/sv.data")
    kto.read_config("./15*/*.csv")
    kto.read_config("../05*/*.csv")
    r.dataset = kto.dataset

    print(r.dataset)

#    for o in r.dataset.keys():
#        print(r.dataset[o])

    if len(sys.argv) == 2 and os.path.isfile(sys.argv[1]):
        r.read(sys.argv[1])
    else:

        try:
            arg1 = sys.argv[1]
        except:
            arg1 = None
    
        try:
            arg2 = sys.argv[2]
        except:
            arg2 = None

        try:
            arg3 = sys.argv[3]
        except:
            arg3 = None

#        print(333333333333333333333333333,arg2,arg1)

        if arg2 and len(arg1) > 2:
            r.yy = arg1[0:2]
            o    = arg1[-2:]
            arg1 = arg2
            arg2 = o

        if arg2:     #  Jahr, um das es geht
            r.jahr = arg2
        else:
            r.jahr = ""
            
        if arg1:      #  Nummer der SV-Meldung  (10,30,50,...)
            r.meldung = arg1
        else:
            r.meldung = ""
            
        dir = os.path.abspath(".")
        m = re.search(r"^(.*)[\\\/]([a-z]+)([\\\/]|$)",dir)
        if m:
            r.person = m.group(2)
        else:
            r.person = ""
        
        if arg3:
            r.monatsanzahl = arg3
        else:
            r.monatsanzahl = "1"
        
        
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
    

#   Aufruf:   python3 -m konto.lohnbuchhaltung <jahr> <meldeart>
#   bei 70 (Beitragsnachweis):      <jahr> = <yymm>
