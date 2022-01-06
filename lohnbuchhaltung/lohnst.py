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

class Lohnst():

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
        time.sleep(0.55)
        return(inhalt)

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


        m = re.search(r"^(.*) +(\d+[a-zA-Z]?) *$",self.dataset['strasse'])
        if m:
            self.dataset['strasse'] = m.group(1)
            self.dataset['hausnr']  = m.group(2)
        if not 'hausnr' in self.dataset:
            self.dataset['hausnr']  = ""

        self.driver.get("https://www.elster.de/eportal/start")
        self.driver.set_window_size(1600, 1000)
        self.id("loginButtonStart").click()
        self.id("durchsuchen").click()

        self.set_par("loginBox.file_cert",                 "/home/cgabriel/25_ift/30_hr/05_template/IfT_elster_2019.pfx")
        time.sleep(1)
        self.set_par("password",                           "IfT9372")
        self.el("#bestaetigenButton > span").click()
        time.sleep(8)

        try:
            self.id("temporaereaufgaben_nein_button").click()
        except:
            pass

        self.id("linkid_navi_formulare-leistungen").click()
        self.id("linkid_navi_formulare-leistungen_alleformulare").click()
        self.el(".toggleBox:nth-child(9) .toggleBox__title").click()
        self.li("Lohnsteuerbescheinigung (Neu/Korrektur)").click()

        self.id("zeitraumJahr").click()
        el1 = self.id("zeitraumJahr")
        el1.find_element(By.XPATH, "//option[. = '2020']").click()
        self.el("option:nth-child(3)").click()
        self.id("Enter").click()
        self.id("Continue").click()

#       Formular Seite 1

#        self.driver.find_element(By.CSS_SELECTOR, "#bestaetigenButton > span").click()
#        self.driver.find_element(By.ID, "temporaereaufgaben_nein_button").click()
#        self.driver.find_element(By.ID, "linkid_navi_formulare-leistungen").click()
#        self.driver.find_element(By.ID, "linkid_navi_formulare-leistungen_alleformulare").click()
#        self.el(".toggleBox:nth-child(9) .toggleBox__title").click()
#        self.driver.find_element(By.LINK_TEXT, "Lohnsteuerbescheinigung (Neu/Korrektur)").click()
#        self.driver.find_element(By.ID, "zeitraumJahr").click()
#        dropdown = self.driver.find_element(By.ID, "zeitraumJahr")
#        dropdown.find_element(By.XPATH, "//option[. = '2020']").click()
#        self.el("option:nth-child(3)").click()
#        self.driver.find_element(By.ID, "Enter").click()
#        self.driver.find_element(By.ID, "Continue").click()

        self.id("Startseite(0)_fields(eruLStBLohnsteuerbescheinigungAnweisungart)").click()
        dropdown = self.id("Startseite(0)_fields(eruLStBLohnsteuerbescheinigungAnweisungart)")
        dropdown.find_element(By.XPATH, "//option[. = 'Neu']").click()

        self.id("dialogeruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberArbGStNr-country").click()
        dropdown = self.id("dialogeruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberArbGStNr-country")
        dropdown.find_element(By.XPATH, "//option[. = 'Bayern']").click()

        self.id("dialogeruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberArbGStNr-tax-number-tax-office").send_keys("218")
        self.id("dialogeruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberArbGStNr-tax-number-destrict").send_keys("129")
        self.id("dialogeruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberArbGStNr-tax-number-distinction-number").send_keys("10296")
        self.el("#NextPage .interactive-icon__text").click()

        self.id("Startseite(0)_AngabenArbeitgeber(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberArbGName)").send_keys("IfT Informatik GmbH")
        self.id("Startseite(0)_AngabenArbeitgeber(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberAdresseStr)").send_keys("Nürnberger Str. 134")
        self.id("Startseite(0)_AngabenArbeitgeber(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberAdresseHausnummer)").send_keys("134")
        self.id("Startseite(0)_AngabenArbeitgeber(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberAdresseStr)").send_keys("Nürnberger Str.")
        self.id("Startseite(0)_AngabenArbeitgeber(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberAdressePLZ)").send_keys("90762")
        self.id("Startseite(0)_AngabenArbeitgeber(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbeitgeberAdresseOrt)").send_keys("Fürth")
        self.el("#NextPage .interactive-icon__text").click()
 
        self.id("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinIdNr)").send_keys("54290836417")
        self.id("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinOrdnungsmerkmal)").send_keys("vgabriel")
        dropdown = self.id("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersongeschlecht)")
        dropdown.find_element(By.XPATH, "//option[. = 'männlich']").click()
        self.id("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonGeburtsdatum)").send_keys("15.09.1970")
        self.id("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameName)").click()
        self.id("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameName)").send_keys("Gabriel")
        self.id("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameTitel)").click()
        self.id("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameTitel)").send_keys("Dr.")
        self.id("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameVorname)").click()
        self.id("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonFamiliennameVorname)").send_keys("Volker")
        self.id("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdresseStr)").click()
        self.id("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdresseStr)").send_keys("von-Steuben-Str.")
        self.id("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdresseHausnummer)").click()
        self.id("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdresseHausnummer)").send_keys("3")
        self.id("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdressePLZ)").click()
        self.id("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdressePLZ)").send_keys("31135")
        self.id("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdresseOrt)").send_keys("Hildesheim")
        self.id("Startseite(0)_AngabenArbeitnehmer(0)_fields(eruLStBLohnsteuerbescheinigungAllgemeinPersonAdresselaenderkennzeichen)").click()
        self.el("#NextPage .interactive-icon__text").click()


        zaehler = 0
        while zaehler < 1:

            self.el(".mzb__info").click()
            self.el("#JumpToPage\\/Startseite\\[0\\]\\/Besteuerungsmerkmale\\[0\\]\\/MZBBesteuerungsmerkmaleMZB\\[0\\] .interactive-icon__text").click()
            self.id("Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMgueltig_ab)").send_keys("01.01.2020")
            dropdown = self.id("Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMSteuerklasse)")
            dropdown.find_element(By.XPATH, "//option[. = '1']").click()
            dropdown = self.id("Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMKinder)")
            dropdown.find_element(By.XPATH, "//option[. = '0,0']").click()
            self.el("#Startseite\\(0\\)_Besteuerungsmerkmale\\(0\\)_MZBBesteuerungsmerkmaleMZB\\(0\\)_fields\\(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMKinder\\) > option:nth-child(2)").click()
            dropdown = self.id("Startseite(0)_Besteuerungsmerkmale(0)_MZBBesteuerungsmerkmaleMZB(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsmerkmaleELStAMKirchensteuerabzugkonfession)")
            dropdown.find_element(By.XPATH, "//option[. = 'Evangelische Kirchensteuer - ev']").click()
            self.el("#NextPage .interactive-icon__text").click()
            
            zaehler = zaehler + 1
            

        self.el("#NextPage .interactive-icon__text").click()



        self.id("Startseite(0)_ArbeitslohnAbzuege(0)_fields(eruLStBLohnsteuerbescheinigungDauerAnfang)").send_keys("01.01")
        self.id("Startseite(0)_ArbeitslohnAbzuege(0)_fields(eruLStBLohnsteuerbescheinigungDauerEnde)").send_keys("31.12")
        self.id("Startseite(0)_ArbeitslohnAbzuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenBruttoArbLohn)").send_keys("49571,20")
        self.id("Startseite(0)_ArbeitslohnAbzuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenLSteuer)").send_keys("0,00")
        self.id("Startseite(0)_ArbeitslohnAbzuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSoli)").send_keys("0,00")
        self.id("Startseite(0)_ArbeitslohnAbzuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbnKiSteuer)").send_keys("0,00")
        self.id("Startseite(0)_ArbeitslohnAbzuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenEhegKiSteuer)").send_keys("0,00")
        self.el("#NextPage .interactive-icon__text").click()

        self.id("Startseite(0)_VersorgungsbezErmArblohn(0)_Versorgungsbezuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenVersorgungsbezgeVBez)").send_keys("33,33")
        self.id("Startseite(0)_VersorgungsbezErmArblohn(0)_Versorgungsbezuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenVersorgungsbezgebmgfreibetrag)").send_keys("33,33")
        self.id("Startseite(0)_VersorgungsbezErmArblohn(0)_Versorgungsbezuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenVersorgungsbezgejahr)").send_keys("2018")
        self.id("Startseite(0)_VersorgungsbezErmArblohn(0)_Versorgungsbezuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenVersorgungsbezgebeginn)").send_keys("03")
        self.id("Startseite(0)_VersorgungsbezErmArblohn(0)_Versorgungsbezuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenVersorgungsbezgeende)").send_keys("10")
        self.id("Startseite(0)_VersorgungsbezErmArblohn(0)_Versorgungsbezuege(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenVersorgungsbezgeeinmversbezug)").send_keys("33,33")
        self.id("Startseite(0)_VersorgungsbezErmArblohn(0)_ErmBestVersbezuegeMKal(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenK_ErmStVBezMKalJahrErmStVBezMKalJahr)").send_keys("1,00")
        self.id("Startseite(0)_VersorgungsbezErmArblohn(0)_ErmBestVersbezuegeMKal(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenK_ErmStVBezMKalJahrjahr)").send_keys("2017")
        self.id("Startseite(0)_VersorgungsbezErmArblohn(0)_NichtErmBestVersbezuegeMKal(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenK_NErmStVBezMKalJahrNErmStVBezMKalJahr)").send_keys("33,33")
        self.id("Startseite(0)_VersorgungsbezErmArblohn(0)_NichtErmBestVersbezuegeMKal(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenK_NErmStVBezMKalJahrjahr)").send_keys("2016")
        self.id("Startseite(0)_VersorgungsbezErmArblohn(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenErmStBetrMKalJahr)").send_keys("33,33")
        self.id("Startseite(0)_VersorgungsbezErmArblohn(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenLSteuerMKalJahr)").send_keys("33,33")
        self.id("Startseite(0)_VersorgungsbezErmArblohn(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSoliMKalJahr)").send_keys("33,33")
        self.id("Startseite(0)_VersorgungsbezErmArblohn(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenKiSteuerArbnMKalJahr)").send_keys("33,33")
        self.id("Startseite(0)_VersorgungsbezErmArblohn(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenKiSteuerEhegMKalJahr)").send_keys("33,33")

        self.el("#NextPage .interactive-icon__text").click()



        self.id("Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenKurzArbGeld)").send_keys("21456,84")
        self.id("Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenStFreiGeKrankVers)").send_keys("11,22")
        self.id("Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenStFreiPrKrankVers)").send_keys("11,33")
        self.id("Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenStFreiGePflegeVers)").send_keys("11,44")
        self.id("Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenArbnAnteilKrankVers)").send_keys("11,55")
        self.id("Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenArbnAnteilPflegVers)").send_keys("11,66")
        self.id("Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenArbnAnteilArblVers)").send_keys("11,77")
        self.id("Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenBeitrPrKrankVers)").send_keys("11,88")
        self.id("Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenArbnAnteilRenVers)").send_keys("11,13")
        self.id("Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenArbnAnteilBerufsVers)").send_keys("11,88")
        self.id("Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenAusgezKinderGeld)").send_keys("11,99")
        self.id("Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenArbgAnteilRenVers)").send_keys("11,11")
        self.id("Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenSozialversicherungsleistungenArbgAnteilBerufsVers)").send_keys("11,12")
        self.id("Startseite(0)_Sonstiges(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenFreibetragDbaTuerkei)").send_keys("23,09")
        self.el("#NextPage .interactive-icon__text").click()

        self.id("Startseite(0)_FreiwilligeAngaben(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbnAnteilWBUmlage)").send_keys("23,10")
        self.id("Startseite(0)_FreiwilligeAngaben(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenArbgAnteilZusatzVers)").send_keys("23,11")
        self.id("Startseite(0)_FreiwilligeAngaben(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenAnzahlArbTag)").send_keys("170")
        self.id("Startseite(0)_FreiwilligeAngaben(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenStFreiFahrtKAusw)").send_keys("23,13")
        self.id("Startseite(0)_FreiwilligeAngaben(0)_ArbgFreiwilligeWerte(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenFreierWertname)").send_keys("23,14")
        self.id("Startseite(0)_FreiwilligeAngaben(0)_ArbgFreiwilligeWerte(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenFreierWertWert)").send_keys("23,15")
        self.id("Startseite(0)_FreiwilligeAngaben(0)_ArbgFreiwilligeTexte(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenFreierTextname)").send_keys("23,16")
        self.id("Startseite(0)_FreiwilligeAngaben(0)_ArbgFreiwilligeTexte(0)_fields(eruLStBLohnsteuerbescheinigungBesteuerungsgrundlagenFreierTextText)").send_keys("23,17")


#   1.   Beginn, Ende, Jahresgehalt aus Gehaltsbscheinigungen

        if not self.jahr == "":
            self.dataset["meldejahr"] = self.jahr
        if not self.meldung == "":
            self.dataset["meldung"]   = self.meldung
#        if not self.person == "":
#            self.dataset["person"]    = self.person

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
                            bruttogehalt = str(int(float(m.group(3))+0.000005))
                               
                        m = re.search(r"fiktives +Gehalt(.*?)\((\d+\.\d\d)\) +\((\d+\.\d\d)\)",text)
                        if not m:
                            jahresgehalt = bruttogehalt
                        else:
                            jahresgehalt = str(int(float(m.group(3))+0.000005))
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
                
            self.dataset['beginn']        = beginn
            self.dataset['ende']          = ende
            self.dataset['jahresgehalt']  = jahresgehalt
            self.dataset['bruttogehalt']  = bruttogehalt
        
        print(self.dataset)
#        return()
        
        if self.dataset["meldung"] == "10":

#            self.xp("//div[text()='SV-Meldung (Allgemein, Knappschaft, See)']").click()
            self.el("[aria-labelledby='overviewViewduaLabel']")    .click()
#            self.xp("//div[text()='Anmeldung']").click()
            self.el("[aria-labelledby='overviewViewanmeldungLabel']")    .click()
            time.sleep(1)
            self.el("[aria-labelledby='overviewViewm10Label']")    .click()
            
#            self.el( "div:nth-child(3) > div:nth-child(2) > div:nth-child(2) > div").click()
#            self.el( "div:nth-child(7) > div > div > div > div:nth-child(1) >  div:nth-child(1)").click()
#            self.el( "div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div").click()
#            self.el( "div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div").click()
#            self.el( "div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div").click()

        if self.dataset["meldung"] == "50":

#            self.xp("//div[text()='SV-Meldung (Allgemein, Knappschaft, See)']").click()
            self.el("[aria-labelledby='overviewViewduaLabel']")    .click()
#            self.xp("//div[text()='Jahresmeldung']").click()
            self.el("[aria-labelledby='overviewViewjahresmeldungLabel']")    .click()
#            return()
            time.sleep(1)
            self.el("[aria-labelledby='overviewViewm50Label']")    .click()

#            self.el( "div:nth-child(3) div:nth-child(6) > div").click()
#            self.el( "div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div").click()
#            self.el( "div:nth-child(2) > div:nth-child(4) > div:nth-child(1) > div").click()
#            self.el( "div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div").click()

        if self.dataset["meldung"] == "92":
        
#            self.xp("//div[text()='menuLinkSV-Meldung (Allgemein, Knappschaft, See)']").click()
            self.el("[aria-labelledby='overviewViewduaLabel']")    .click()
#            self.xp("//div[text()='Jahresmeldung']").click()
            self.el("[aria-labelledby='overviewViewjahresmeldungLabel']")    .click()
            time.sleep(1)
            self.el("[aria-labelledby='overviewViewm92Label']")    .click()
            self.dataset['beginn'] = "01.01." + self.dataset["meldejahr"]
            self.dataset['ende']   = "31.12." + self.dataset["meldejahr"]

#            self.el( "div:nth-child(3) div:nth-child(6) > div").click()
#            self.el( "div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div").click()
#            self.el( "div:nth-child(2) > div:nth-child(4) > div:nth-child(1) > div").click()
#            self.el( "div:nth-child(2) > div:nth-child(3) > div:nth-child(1) > div").click()

        if self.dataset["meldung"] == "30":

#            self.xp("//div[text()='menuLinkSV-Meldung (Allgemein, Knappschaft, See)']").click()
            self.el("[aria-labelledby='overviewViewduaLabel']")    .click()
#            self.xp("//div[text()='Jahresmeldung']").click()
            self.el("[aria-labelledby='overviewViewabmeldungLabel']")    .click()
            time.sleep(1)
            self.el("[aria-labelledby='overviewViewm30Label']")    .click()
#            self.el( "div:nth-child(3) div:nth-child(6) > div").click()
#            self.el( "div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div").click()
#            self.el( "div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div").click()
#            self.el( "div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div").click()


#        return()
        time.sleep(2)
        self.driver.switch_to.frame(1)
        time.sleep(1)

#        self.xp(".checkbox:nth-child(2) > label").click()
#            self.set_par("datensatzIdUrsprungsmeldung",             ".datensatzid")

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

#       Abmeldung / Jahresmeldung:

        if self.dataset["meldung"] in ("30","50"):

            if self.dataset["persgruppe"] == "109":
                self.set_par("besteuerungsArt",                ".pauschsteuer")
                self.set_par("firmaSteuernummer",              ".firmasteuernummer")
                self.set_par("identifikationsNrArbeitnehmer",  ".lohnstid")

            self.set_par("ende",                           ".ende")
#            self.set_par("entgeltRentenberechnung",        ".betrag")
#            self.set_par("waehrung",                       "E")
            self.set_par("entgelt",                        ".jahresgehalt")
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
            self.set_par("uvData.0.arbeitsentgelt",                 ".bruttogehalt")

        if "storno" in self.dataset and self.dataset["storno"][0] == "J":
        
            self.xp("//label[text()='Stornierung']").click()
            self.set_par("datensatzIdUrsprungsmeldung",             ".datensatzid")
         




#**************************************************************************************

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
            
#*************************************************************************************
            

if __name__ == "__main__":

    r            = Lohnst().setup_method("")
#    config_data  = [ os.popen("python3 -m fibu.xlsmanager memory oa ./15*/*.csv aktuell").read() ]  #  personal data
    kto          = konto.Konto()
    kto.read_config(kto.base_dir+"/*.data")
    kto.read_config("../*.data")
    kto.read_config("./sv.data")
    kto.read_config("*/sv.data")
    kto.read_config("./15*/*.csv")
    r.dataset = kto.dataset

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

        if arg2 and len(arg1) > 2:
            o    = arg1[-2:]
            arg1 = arg2
            arg2 = o

        if arg2:
            r.jahr = arg2
        else:
            r.jahr = ""
            
        if arg1:
            r.meldung = arg1
        else:
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
    
