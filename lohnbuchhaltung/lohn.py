#  coding: utf-8

import os,sys,re,glob,random

from konto.lohnbuchhaltung import lohnsteuer

#************************************************************************************

class Lohn (object):

    def __init__(self,lohnkto="13-6000",sozkto="13-6010",kugkto=""):

        self.lohnkto = lohnkto
        self.sozkto  = sozkto
        self.kugkto  = kugkto

#        bezeichner  = [
#            
#            'LS'        ,  "Lohnsteuer",                                       "11-1503-LS",
#            'SZ'        ,  "Solidaritaetszuschlag",                            "11-1503-SZ",
#            'KI'        ,  "Kirchensteuer",                                    "11-1503-KI",
#            'AN-KV-S'   ,  "Arbeitnehmerbeitrag  Krankenversicherung",         "11-XXXX-KV-S-AN",
#            'AN-KV-Z'   ,  "Arbeitnehmerzuschlag Krankenversicherung",         "11-XXXX-KV-Z-AN",
#            'AN-RV'     ,  "Arbeitnehmerbeitrag  Rentenversicherung",          "11-XXXX-RV-AN",
#            'AN-AV'     ,  "Arbeitnehmerbeitrag  Arbeitslosenversicherung",    "11-XXXX-AV-AN",
#            'AN-PV-S'   ,  "Arbeitnehmerbeitrag  Pflegeversicherung",          "11-XXXX-PV-S-AN",
#            'AN-PV-Y'   ,  "Arbeitnehmerzuschlag Pflegeversicherung",          "11-XXXX-PV-Y-AN",
#            'AR-KV-S'   ,  "Arbeitgeberbeitrag   Krankenversicherung",         "11-XXXX-KV-S-AR",
#            'AR-KV-Z'   ,  "Arbeitgeberzuschlag  Krankenversicherung",         "11-XXXX-KV-Z-AR",
#            'AR-RV'     ,  "Arbeitgeberbeitrag   Rentenversicherung",          "11-XXXX-RV-AR",
#            'AR-AV'     ,  "Arbeitgeberbeitrag   Arbeitslosenversicherung",    "11-XXXX-AV-AR",
#            'AR-PV'     ,  "Arbeitgeberbeitrag   Pflegeversicherung",          "11-XXXX-PV-AR",
#            'AR-ST'     ,  "Pauschalsteuer geringfuegig Beschaeftigte",        "11-XXXX-ST-AR",
#            'AR-PS'     ,  "Pauschalsteuer kurzfristig Beschaeftigte",         "11-XXXX-PS-AR",
#            'AR-U1'     ,  "Arbeitgeber-Umlage   krankheitsbedingter Ausfall", "11-XXXX-U1-AR",
#            'AR-U2'     ,  "Arbeitgeber-Umlage   Mutterschutz",                "11-XXXX-U2-AR",
#            'AR-U3'     ,  "Arbeitgeber-Umlage   Insolvenzschutz",             "11-XXXX-U3-AR",
#            
#            ]
            
        bezeichner  = [
            
            'LS'        ,  "Lohnsteuer",                                       "11-C13-3065-LS",
            'SZ'        ,  "Solidaritaetszuschlag",                            "11-C13-3065-SZ",
            'KI'        ,  "Kirchensteuer",                                    "11-C13-3065-KI",
            'AN-KV-S'   ,  "Arbeitnehmerbeitrag  Krankenversicherung",         "11-C13-3740-XXXX-KV-S-AN",
            'AN-KV-Z'   ,  "Arbeitnehmerzuschlag Krankenversicherung",         "11-C13-3740-XXXX-KV-Z-AN",
            'AN-RV'     ,  "Arbeitnehmerbeitrag  Rentenversicherung",          "11-C13-3740-XXXX-RV-AN",
            'AN-AV'     ,  "Arbeitnehmerbeitrag  Arbeitslosenversicherung",    "11-C13-3740-XXXX-AV-AN",
            'AN-PV-S'   ,  "Arbeitnehmerbeitrag  Pflegeversicherung",          "11-C13-3740-XXXX-PV-S-AN",
            'AN-PV-Y'   ,  "Arbeitnehmerzuschlag Pflegeversicherung",          "11-C13-3740-XXXX-PV-Y-AN",
            'AR-KV-S'   ,  "Arbeitgeberbeitrag   Krankenversicherung",         "11-C13-3740-XXXX-KV-S-AR",
            'AR-KV-Z'   ,  "Arbeitgeberzuschlag  Krankenversicherung",         "11-C13-3740-XXXX-KV-Z-AR",
            'AR-RV'     ,  "Arbeitgeberbeitrag   Rentenversicherung",          "11-C13-3740-XXXX-RV-AR",
            'AR-AV'     ,  "Arbeitgeberbeitrag   Arbeitslosenversicherung",    "11-C13-3740-XXXX-AV-AR",
            'AR-PV'     ,  "Arbeitgeberbeitrag   Pflegeversicherung",          "11-C13-3740-XXXX-PV-AR",
            'AR-ST'     ,  "Pauschalsteuer geringfuegig Beschaeftigte",        "11-C13-3740-XXXX-ST-AR",
            'AR-PS'     ,  "Pauschalsteuer kurzfristig Beschaeftigte",         "11-C13-3065-PS",
            'AR-PZ'     ,  "Pauschal-Soli  kurzfristig Beschaeftigte",         "11-C13-3065-PZ",
            'AR-PK'     ,  "Pauschal-KiSt  kurzfristig Beschaeftigte",         "11-C13-3065-PK",
            'AR-U1'     ,  "Arbeitgeber-Umlage   krankheitsbedingter Ausfall", "11-C13-3740-XXXX-U1-AR",
            'AR-U2'     ,  "Arbeitgeber-Umlage   Mutterschutz",                "11-C13-3740-XXXX-U2-AR",
            'AR-U3'     ,  "Arbeitgeber-Umlage   Insolvenzschutz",             "11-C13-3740-XXXX-U3-AR",

            'KN-KV-S'   ,  "KUG Arbeitnehmerbeitrag  Krankenversicherung",         "11-C13-3740-XXXX-KV-S-AN",
            'KN-KV-Z'   ,  "KUG Arbeitnehmerzuschlag Krankenversicherung",         "11-C13-3740-XXXX-KV-Z-AN",
            'KN-RV'     ,  "KUG Arbeitnehmerbeitrag  Rentenversicherung",          "11-C13-3740-XXXX-RV-AN",
            'KN-PV-S'   ,  "KUG Arbeitnehmerbeitrag  Pflegeversicherung",          "11-C13-3740-XXXX-PV-S-AN",
            'KN-PV-Y'   ,  "KUG Arbeitnehmerzuschlag Pflegeversicherung",          "11-C13-3740-XXXX-PV-Y-AN",
            'KR-KV-S'   ,  "KUG Arbeitgeberbeitrag   Krankenversicherung",         "11-C13-3740-XXXX-KV-S-AR",
            'KR-KV-Z'   ,  "KUG Arbeitgeberzuschlag  Krankenversicherung",         "11-C13-3740-XXXX-KV-Z-AR",
            'KR-RV'     ,  "KUG Arbeitgeberbeitrag   Rentenversicherung",          "11-C13-3740-XXXX-RV-AR",
            'KR-PV'     ,  "KUG Arbeitgeberbeitrag   Pflegeversicherung",          "11-C13-3740-XXXX-PV-AR",
            ]
            
        self.abgabenarten = bezeichner[::3]
        self.bezeichner   = dict(zip(bezeichner[::3],bezeichner[1::3]))
        self.gegenkonto   = dict(zip(bezeichner[::3],bezeichner[2::3]))
        self.bezeichner['LOHN-AR']  = "Arbeitgeberanteil    Gehalt"
        self.bezeichner['LOHN-KUG'] = "Arbeitgeberanteil    KUG"

#        try:
#            self.fibu.rules
#        except:
#            self.fibu.rules = self.fibu

        self.gleitzone = {
         '12A': 400, '12B': 800,
         '15A': 450, '15B': 850,
         
         2007: 0.7673,
         2008: 0.7732, 2009: 0.7472,
         2010: 0.7585, 2011: 0.7435,
         2012: 0.7491, 2013: 0.7605,
         2014: 0.7605, 2015: 0.7585,
         2016: 0.7547, 2017: 0.7547,
         2018: 0.7547
         
             }  #  Gleitzonenfaktor     FIBU-GLEITZONE-002-VALID
                          #  FIBU-BEMESSUNGSGRENZEN-002-VALID
         
#        self.rv_obergrenze = {2007: 5800.0, 2008: 5800.0, 2009: 5800.0, 2010: 5800.0,
#                              2011: 5800.0, 2012: 5800.0, 2013: 5800.0,
#                              2014: 5950.0, 2015: 6050.0, 2016: 6200.0,
#                              2017: 6350.0, 2018: 6500.0}
#        self.kv_obergrenze = {2007: 3937.5, 2008: 3937.5, 2009: 3937.5, 2010: 3937.5,
#                              2011: 3937.5, 2012: 3937.5, 2013: 3937.5,
#                              2014: 4050.0, 2015: 4125.0, 2016: 4237.5,
#                              2017: 4350.0, 2018: 4425}


                          #  FIBU-BEMESSUNGSGRENZEN-002

#*************************************************************************

    def kknr (self,kk):
    
        kk = kk.upper()
        kk = re.sub(r"\n"," ",kk,99999999)
    
        if " DAK" in kk:
            return("1510","DAK")
        elif "AOK HESSEN" in kk:
            return("1511","AOKHES")
        elif " AOK RHEINL" in kk:
            return("1520","AOKRPS")
        elif " AOK NORD" in kk:
            return("1521","AOKNWE")
        elif " MINIJOB" in kk or " KNAPPSCHAFT" in kk:
            return("1512","MINIJO")
        elif re.search("( BKK_?VER|[- ]VBU)",kk):
            return("1513","VBU")
        elif " AOK BAYERN" in kk:
            return("1514","AOKBAY")
        elif re.search("( BKK_?MOBIL| MOBILOI?L?| BKKMOIL|LFD.\s*NR.\s*ERFASSUNG)",kk):
            return("1515","MOBILO")
        elif re.search("( BKK_?SIEMENS | SBK )",kk):
            return("1516","SBK")
        elif " TECHNIKER" in kk or " TKK" in kk or " TECHNKK" in kk:
            return("1517","TKK")
        elif " BARMER" in kk:
            return("1518","BARMER")
        elif " DEBEKA" in kk:
            return("1519","DEBEKA")
        return("1528","UNKNOWN")

#*************************************************************************

    def parse_lohndaten (self,buchungsdaten_text,ktoslip,ktolstb):

        self.lstfile = {}
        self.lsttext = {}

        buchungen         = []
        lohndaten         = {}
        gesetzte_betraege = {}
        ktoslips          = {}
        ukto              = "-"
        
        diffs = {}
        for art in self.abgabenarten:
            diffs[art] = 0.00


#   1.   Daten einlesen aus Lohnbescheinigungen

        for slip in ktoslip:
            erg = self.read_lohnbescheinigung(slip)
            if erg:
                jm                    = erg[0]
                slipdata              = erg[1]
                ktoslips[jm]          = slip
                if not jm == "000001":
                    lohndaten[jm]            = slipdata
                    lohndaten[jm]['ZAHL']    = []
                    lohndaten[jm]['LFAKTOR'] = '1'

        jms = list(lohndaten.keys())
        jms.sort()


#   2.   Daten einlesen aus Konto
        
        export_zahl = {}
        export_sum  = {}
        rest_lines  = []

        for zeile in buchungsdaten_text.split("\n"):

            m  = re.search('^(\d\d\d\d)(\d\d)(\d\d) +(\-?\d+\.\d\d\*?\d?) +(\S*?)\-([A-Z\-]+\d?) +\S+ +(\-?\d+\.\d\d) +(.*)', zeile)
            if not m:
                rest_lines.append(zeile)
                continue

            ukto = m.group(5)

#            print(zeile)
#            print("================",m.group(5))

            jm     = m.group(1) + m.group(2)
            betrag = "%3.2f" % eval(m.group(4))
            art    = m.group(6)
            rem    = m.group(8)
            
            if art == "ZAHL":     #   Zahlungen
                buchungen.append(zeile)
                if not jm in export_zahl:
                    export_zahl[jm] = ""
                    export_sum[jm]  = 0.00
                export_sum[jm]  = export_sum[jm]  + float(betrag)
                betrag = m.group(3) + "." + m.group(2) + ".  " + ("%11.2f" % float(betrag)) 
                while (0 == 0):
                    export_zahl[jm] = export_zahl[jm] + betrag + "  " + rem[0:75] + "\n"
                    rem    = re.sub(r"^ +","",rem[75:])
                    betrag = "                   "
                    if rem == "":
                        break
                        
            elif art == "LOHN-AN":  #   and not "KUG-Berechnung" in rem:
                if not jm in lohndaten:
                    lohndaten[jm] = {}
                if not 'LOHN1' in lohndaten[jm]:
                    lohndaten[jm]['LOHN1'] = []
                m = re.search("(\d+)fach ",rem)
                if m:
                    lohndaten[jm]['LFAKTOR'] = m.group(1)
                    lohndaten[jm]['LOHN1'].append("%3.2f" % (- float(betrag)/float(m.group(1)) ) )
                else:
                    lohndaten[jm]['LFAKTOR'] = "1"
                    lohndaten[jm]['LOHN1'].append("%3.2f" % (- float(betrag) ) )
                lohndaten[jm]['LOHN1'].append(rem)
                if 'KV' in rem:
                    lohndaten[jm]['UEKV'] = 1
                if 'RV' in rem:
                    lohndaten[jm]['UERV'] = 1
                m = re.search("KUG(SOZ|)(\d\d).*?(\d+)([,\.]\d\d|)",rem)
                if m:
                    lohndaten[jm]['kugjahr'] = m.group(2)
                    lohndaten[jm]['kugdiff'] = abs(float(re.sub(r",",".",m.group(3)+m.group(4))))
                    lohndaten[jm]['kugausz'] = abs(float(betrag))
                else:
                    lohndaten[jm]['kugausz'] = 0.0

            else:
                m = re.search(r"( *\(.*gesetzt.*?)(\-?\d+\.\d\d)(.*\).*)",rem)
                if m:
                    if jm not in gesetzte_betraege:
                        gesetzte_betraege[jm] = {}
                    gesetzte_betraege[jm][art] = (float(m.group(2)),m.group(1)+m.group(2)+m.group(3))

#  3.   Alle Buchungszeitraeume durchgehen:

        jm0 = "000001"
        jms = list(lohndaten.keys())
        jms.sort()

        betraege = {}
        for jm in jms:

            jahr        = jm[0:4]
            monat       = jm[4:6]
            
#  4.   Lohnsumme berechnen

            if not jm0[0:4] == jm[0:4]:
                lohnsumme   = 0.0
                ls_sum      = 0.0
                sz_sum      = 0.0
                ki_sum      = 0.0
                monate      = 0
                ch_merk     = None
                jahressumme = {}
                for art in self.abgabenarten:
                    jahressumme[art] = 0.00
                jm0       = jm

            betraege[jm] = {}
            lst_exists = True
            if not 'LOHN-AN' in lohndaten[jm]:   #  wenn noch keine Lohnsteuerbescheinigung vorliegt
                lohndaten[jm]['LOHN-AN'] = lohndaten[jm]['LOHN1']
                lst_exists = False
                

            lohn = 0.0
            for entry in lohndaten[jm]['LOHN-AN']:
            
                if not 'MERK' in lohndaten[jm]:
                    m = re.search(r"(\d\d\d\d[r\-]*)/(\d\d\d\d)",entry)
                    if m:
                        lohndaten[jm]['MERK'] = m.group(1)
                        lohndaten[jm]['NR']   = m.group(2)
                        self.set_rahmendaten(lohndaten[jm],jahr,monat)
                        
                if not 'STKL' in lohndaten[jm]:
                    m = re.search(r" (\d)/(\-?[0-9\.\-]+)/([0-9\.]+)",entry)
                    if m:
                        lohndaten[jm]['STKL']   = m.group(1)
                        lohndaten[jm]['KINDER'] = m.group(2)
                        lohndaten[jm]['KIST']   = m.group(3)
                m = re.search(r" (\d\d\d\d)\.(\d\d\d\d)",entry)
                if m:
                    lohndaten[jm]['KLIMIT'] = "%3.2f" % float(m.group(1))
                    lohndaten[jm]['RLIMIT'] = "%3.2f" % float(m.group(2))
                try:
                    lohn = lohn + float(entry)
                except:
                    pass
                    
            if 'kugausz' in lohndaten[jm]:
                lohn = lohn - lohndaten[jm]['kugausz']  #  KUG ist kein Lohn
            lohnsumme = lohnsumme + lohn   #  Lohn
            monate    = monate + 1

#  4.   Lohnsteuer berechnen

            try:
                stkl = int(lohndaten[jm]['STKL'])
            except:
                print("No data for STKL in " + jm)
            kist = lohndaten[jm]['KIST']
            merk       = lohndaten[jm]['MERK']
            if not merk[0] == "0":
                kv_zuschlag_f_lst_berechnung = float(lohndaten[jm]['ZV'])  #  average 'ZU' 
                kv_zuschlag_f_lst_berechnung = float(lohndaten[jm]['ZU'])
            else:
                kv_zuschlag_f_lst_berechnung = 0.0
            if float(lohndaten[jm]['KINDER']) < 0:
                kv_zuschlag_f_lst_berechnung = kv_zuschlag_f_lst_berechnung + float(lohndaten[jm]['PZ'])

            if ch_merk == 0:
                ch_merk = [stkl,kv_zuschlag_f_lst_berechnung,kist]
            elif not ch_merk == 1:
                if not ch_merk == [stkl,kv_zuschlag_f_lst_berechnung,kist]:
                    ch_merk = 1

#            exec('import pap.lst' + jahr)

            kinderfreibetrag = 0
            
            ls = 0.00
            sz = 0.00
            ki = 0.00
            
            if stkl > 0:
                for i in (1,2):
                    stobj = eval('lohnsteuer.lst' + jahr + '.Lst' + jahr + '()')
                    stobj.setKrv(0)
                    stobj.setLzz(2)
                    stobj.setR(int(float(kist)>0))
                    stobj.setRe4( max(0, int ( (float(lohn)-float(kinderfreibetrag)) *100) ) )
                    stobj.setStkl(stkl)
                    try:
                        stobj.setKvz(kv_zuschlag_f_lst_berechnung)
                    except Exception as e:
                        str(e)
                    stobj.setZkf(max(0.0,float(lohndaten[jm]['KINDER'])))
                    stobj.MAIN()
#                    kinderfreibetrag = float(stobj.KFB)/12     #   nicht klar, wozu ndiese Berechnung gemacht wurde

#                print("XX", int ( (float(lohn)-float(kinderfreibetrag)) *100) )
                ls = 0.01 * float( stobj.getLstlzz() )
                sz = 0.01 * float( stobj.getSolzlzz() )
                ki = 0.01 * ( float(stobj.getBk()) + float(stobj.getBks()) + float(stobj.getBkv())) * (0.01 * float(kist))
                
#                print(lohndaten[jm])
#                print(jm,ls,sz,ki)
            
            if monate == 12 and type(ch_merk) == type([]):  #  Jahresausgleich nur dann machen,
                stobj.setLzz(1)                             #  wenn alle 12 Monate bei IfT und sich keine Merkmale
                stobj.setRe4( int(lohnsumme*100) )          #  geaendert haben
                stobj.MAIN()
                jahres_ls = 0.01 * float( stobj.getLstlzz() )
                jahres_sz = 0.01 * float( stobj.getLstlzz() )
                jahres_ki = 0.01 * ( float(stobj.getBk()) + float(stobj.getBks()) + float(stobj.getBkv())) * float(kist)
                ls = jahres_ls - ls_sum
                sz = jahres_sz - ls_sum
                ki = jahres_ki - ls_sum
            else:
                ls_sum = ls_sum + ls
                sz_sum = sz_sum + sz
                ki_sum = ki_sum + ki
            betraege[jm]['LS'] = "%3.2f" % ls
            betraege[jm]['SZ'] = "%3.2f" % sz
            betraege[jm]['KI'] = "%3.2f" % ki
            
#  5.  Sozialversicherung berechnen
            
#            restlohnrv = max(0,12*float(lohndaten[jm]['RLIMIT']) - lohnsumme)
#            restlohnkv = max(0,12*float(lohndaten[jm]['KLIMIT']) - lohnsumme)
#            lohnrv     = min(lohn,restlohnrv)
#            lohnkv     = min(lohn,restlohnkv)

            lohnkv     = min(lohn,float(lohndaten[jm]['KLIMIT']))
            lohnrv     = min(lohn,float(lohndaten[jm]['RLIMIT']))
            if 'UEKV' in lohndaten[jm]:   #   wenn aufgrund von Lohnsteigerungen im Jahr die
                lohnkv = lohnrv           #   Beitragsbemessungsgrenzen keine Anwendung finden sollen
            if 'UERV' in lohndaten[jm]:
                lohnkv = lohn
                lohnrv = lohn

            merk       = lohndaten[jm]['MERK']
            mode       = "s"  #   Standard
            kinder     = lohndaten[jm]['KINDER']

#            print(merk,stkl)
            if merk[0:4] == "1100" or merk[0:4] == "6500" and stkl == 0:
                mode     = "g"   #   geringfuegig beschaeftigt
                merk     = "1100" + merk[4:]
            if merk[0:4] == "1110" or merk[0:4] == "6100" and stkl == 0:
                mode     = "h"   #   geringfuegig beschaeftigt, mit Rentenversicherung
                merk     = "1110" + merk[4:]
            elif merk[0:4] == "0000":   #  kurzfristig beschaeftigt
                if stkl == 0:
                    mode    = "p"   #   Pauschalversteuerung 25 vH, ohne U1 und U2
                else:
                    mode    = "k"   #   Individualversteuerung
            if float(kinder) < 0:
                kinder = "0"
                mode   = re.sub(r"s","o",mode)   #   ueber 23, keine Kinder

            betraege[jm]['AN-KV-S'] = "%3.2f" % ( 0.01 * float(lohndaten[jm]['KV']) * lohnkv * int(mode in "so")  * int(merk[0]) )
            krankengeld             = "%3.2f" % ( 0.01 * float(lohndaten[jm]['KG']) * lohnkv * int(mode in "so")  * int(merk[0]) )
            betraege[jm]['AN-KV-Z'] = "%3.2f" % ( 0.01 * float(lohndaten[jm]['ZU']) * lohnkv * int(mode in "so")  * int(merk[0]) )
            betraege[jm]['AR-KV-S'] = "%3.2f" % ( 0.01 * float(lohndaten[jm]['KV']) * lohnkv * int(mode in "sogh")* int(merk[0]) )
            betraege[jm]['AR-KV-Z'] = "%3.2f" % ( 0.01 * float(lohndaten[jm]['ZA']) * lohnkv * int(mode in "sogh")* int(merk[0]) )

            betraege[jm]['AN-RV']   = "%3.2f" % ( 0.01 * float(lohndaten[jm]['RV']) * lohnrv * int(mode in "so")  * int(merk[1]) +
                                                  0.01 * float(lohndaten[jm]['AV']) * lohnrv * int(mode in "h")   * int(merk[1]) )
            betraege[jm]['AR-RV']   = "%3.2f" % ( 0.01 * float(lohndaten[jm]['RV']) * lohnrv * int(mode in "sogh")* int(merk[1]) )

            betraege[jm]['AN-AV']   = "%3.2f" % ( 0.01 * float(lohndaten[jm]['AV']) * lohnrv * int(mode in "so")  * int(merk[2]) )
            betraege[jm]['AR-AV']   = "%3.2f" % ( 0.01 * float(lohndaten[jm]['AV']) * lohnrv * int(mode in "so")  * int(merk[2]) )

            betraege[jm]['AN-PV-S'] = "%3.2f" % ( 0.01 * float(lohndaten[jm]['PV']) * lohnkv * int(mode in "so")  * int(merk[3]) )
            betraege[jm]['AN-PV-Y'] = "%3.2f" % ( 0.01 * float(lohndaten[jm]['PZ']) * lohnkv * int(mode in "o")   * int(merk[3]) )
            betraege[jm]['AR-PV']   = "%3.2f" % ( 0.01 * float(lohndaten[jm]['PV']) * lohnkv * int(mode in "so")  * int(merk[3]) )

            betraege[jm]['AR-ST']   = "%3.2f" % ( 0.01 * float(lohndaten[jm]['ST']) * lohn * int(mode in "gh") )
            betraege[jm]['AR-PS']   = "%3.2f" % ( 0.01 * float(lohndaten[jm]['PS']) * lohn * int(mode in "p") )
            betraege[jm]['AR-PZ']   = "%3.2f" % ( 0.01 * float(lohndaten[jm]['SOLIANTEIL']) * 
                                                         float(lohndaten[jm]['PS']) * lohn * int(mode in "p") )
            betraege[jm]['AR-PK']   = "%3.2f" % ( 0.01 * 0.01  * float(kist) * 
                                                         float(lohndaten[jm]['PS']) * lohn * int(mode in "p") )

            betraege[jm]['AR-U1']   = "%3.2f" % ( 0.01 * float(lohndaten[jm]['U1']) * lohn  * int(mode not in "") )
            betraege[jm]['AR-U2']   = "%3.2f" % ( 0.01 * float(lohndaten[jm]['U2']) * lohn  * int(mode not in "") )
            betraege[jm]['AR-U3']   = "%3.2f" % ( 0.01 * float(lohndaten[jm]['U3']) * lohn  * int(mode not in "") )

            if "r" in merk:
                betraege[jm]['AN-RV']   = "0.00"
                betraege[jm]['AN-AV']   = "0.00"
            if "-" in merk:
                betraege[jm]['AN-KV-S'] = "%3.2f" % ( float(betraege[jm]['AN-KV-S']) - float(krankengeld) )
                if 'AR-KV-S' in betraege[jm]:
                    betraege[jm]['AR-KV-S'] = "%3.2f" % ( float(betraege[jm]['AR-KV-S']) - float(krankengeld) )
                else:
                    betraege[jm]['AR-KV']   = "%3.2f" % ( float(betraege[jm]['AR-KV']) - float(krankengeld) )
            

#            if 'FIX' in lohndaten[jm] and lohndaten[jm]['FIX'] == 1:
#                for art in self.abgabenarten:
#                    betraege[jm][art] = 0.00
#                    for o in lohndaten[jm][art]:
#                        betraege[jm][art] = betraege[jm][art] + float(o)
#                        break

#  7.  Sozialversicherung Kurzarbeitergeld:

            if 'kugdiff' in lohndaten[jm]:     #   Sozialversicherung des KUG muss der Arbeitgeber tragen:
#                print("KUG",lohndaten[jm]['kugdiff'],lohn)
                lohn_eigen  = lohn
                lohn_fiktiv = (lohndaten[jm]['kugdiff'] - lohn)
                lohn        = 0.8 * lohn_fiktiv
            else:
                lohn        = 0.0
                lohn_eigen  = 0.0
                lohn_fiktiv = 0.0
            lohnkv = min(lohn,float(lohndaten[jm]['KLIMIT']))
            lohnrv = min(lohn,float(lohndaten[jm]['RLIMIT']))
#            print(lohnkv,lohnrv)

            lohndaten[jm]['LOHNFIKTIV'] = "%3.2f" % ( lohn + lohn_eigen)
            betraege[jm]['KN-KV-S'] = "%3.2f" % ( 0.01 * float(lohndaten[jm]['KV']) * lohnkv * int(mode in "so")  * int(merk[0]) )
#            print(betraege[jm]['KN-KV-S'],lohndaten[jm]['KN-KV-S'])
            krankengeld             = "%3.2f" % ( 0.01 * float(lohndaten[jm]['KG']) * lohnkv * int(mode in "so")  * int(merk[0]) )
            betraege[jm]['KN-KV-Z'] = "%3.2f" % ( 0.01 * float(lohndaten[jm]['ZU']) * lohnkv * int(mode in "so")  * int(merk[0]) )
            betraege[jm]['KR-KV-S'] = "%3.2f" % ( 0.01 * float(lohndaten[jm]['KV']) * lohnkv * int(mode in "sogh")* int(merk[0]) )
            betraege[jm]['KR-KV-Z'] = "%3.2f" % ( 0.01 * float(lohndaten[jm]['ZA']) * lohnkv * int(mode in "sogh")* int(merk[0]) )
   
            betraege[jm]['KN-RV']   = "%3.2f" % ( 0.01 * float(lohndaten[jm]['RV']) * lohnrv * int(mode in "so")  * int(merk[1]) +
                                              0.01 * float(lohndaten[jm]['AV']) * lohnrv * int(mode in "h")   * int(merk[1]) )
            betraege[jm]['KR-RV']   = "%3.2f" % ( 0.01 * float(lohndaten[jm]['RV']) * lohnrv * int(mode in "sogh")* int(merk[1]) )

            betraege[jm]['KN-AV']   = "%3.2f" % ( 0.01 * float(lohndaten[jm]['AV']) * lohnrv * int(mode in "so")  * int(merk[2]) )
            betraege[jm]['KR-AV']   = "%3.2f" % ( 0.01 * float(lohndaten[jm]['AV']) * lohnrv * int(mode in "so")  * int(merk[2]) )

            betraege[jm]['KN-PV-S'] = "%3.2f" % ( 0.01 * float(lohndaten[jm]['PV']) * lohnkv * int(mode in "so")  * int(merk[3]) )
            betraege[jm]['KN-PV-Y'] = "%3.2f" % ( 0.01 * float(lohndaten[jm]['PZ']) * lohnkv * int(mode in "o")   * int(merk[3]) )
            betraege[jm]['KR-PV']   = "%3.2f" % ( 0.01 * float(lohndaten[jm]['PV']) * lohnkv * int(mode in "so")  * int(merk[3]) )

            if "-" in merk:
                betraege[jm]['KN-KV-S'] = "%3.2f" % ( float(betraege[jm]['KN-KV-S']) - float(krankengeld) )
                if 'KR-KV-S' in betraege[jm]:
                    betraege[jm]['KR-KV-S'] = "%3.2f" % ( float(betraege[jm]['KR-KV-S']) - float(krankengeld) )
                else:
                    betraege[jm]['KR-KV']   = "%3.2f" % ( float(betraege[jm]['KR-KV']) - float(krankengeld) )
                        

#   8.   KUG-Anteile hinzurechnen


#            betraege[jm]['AR-KV-S'] = "%3.2f" % ( float(betraege[jm]['AR-KV-S']) + float(betraege[jm]['KN-KV-S']) 
#                                                         + float(betraege[jm]['KR-KV-S'])  )
#            betraege[jm]['AR-KV-Z'] = "%3.2f" % ( float(betraege[jm]['AR-KV-Z']) + float(betraege[jm]['KN-KV-Z']) 
#                                                         + float(betraege[jm]['KR-KV-Z'])  )
#            betraege[jm]['AR-PV']   = "%3.2f" % ( float(betraege[jm]['AR-PV'])   + float(betraege[jm]['KN-PV-S']) 
#                                                         + float(betraege[jm]['KR-PV'])  )
#            betraege[jm]['AR-RV']   = "%3.2f" % ( float(betraege[jm]['AR-RV'])   + float(betraege[jm]['KN-RV'])   
#                                                         + float(betraege[jm]['KR-RV'])  )
#            
#            kug_sozialbeitraege     = ( float(betraege[jm]['KN-KV-S']) + float(betraege[jm]['KR-KV-S'])
#                                        float(betraege[jm]['KN-KV-Z']) + float(betraege[jm]['KR-KV-Z'])
#                                        float(betraege[jm]['KN-PV'])   + float(betraege[jm]['KR-PV'])
#                                        float(betraege[jm]['KN-RV'])   + float(betraege[jm]['KR-RV'])  )

            for art in self.abgabenarten:
                try:
                    betraege[jm][art] = "%3.2f" % gesetzte_betraege[jm][art][0]
                except:
                    pass

#   9.  Korrekturen berechnen

            if not lst_exists:
                for art in self.abgabenarten:
                    lohndaten[jm][art] = [ betraege[jm][art], "%3.2f" % diffs[art] ]
                    diffs[art]         = 0.00
                    jahressumme[art]   = -99999999
                    
            else:
                for art in self.abgabenarten:
                    sum = 0.00
                    for o in lohndaten[jm][art]:
                        try:
                            sum = sum + float(o)
                        except:
                            pass
                    jahressumme[art] = jahressumme[art] + sum
                    diffs[art] = diffs[art] + ( float(betraege[jm][art]) - sum )




#    8.  Buchungen schreiben

        jm0         = "000001"
        jahressumme = {}
        if jm0 in ktoslips:
            ktoslip0     = ktoslips["000001"]
            export_slip0 = open(ktoslip0).read()
        else:
            ktoslip0     = ""
            export_slip0 = ""
        
        
        for jm in jms:
            
            if jm in ktoslips:
                ktoslip0     = ktoslips[jm]
                export_slip0 = open(ktoslip0).read()

            export_slip  = ""
            day          = "03"
            lohnsumme    = 0.00
            kugausz      = 0.00
            an_soz       = 0.00
            ar_soz       = 0.00
            kug_soz      = 0.00
            st_soz       = 0.00

            if not jm0[0:4] == jm[0:4]:
                jahressumme = {}
                for art in (self.abgabenarten + [1,2,3,4,5,6,7,8]):
                    jahressumme[art] = 0.00
                jm0 = jm

            fiktives_gehalt = 0.00
            if 'LOHNFIKTIV' in lohndaten[jm]:
                fiktives_gehalt = float(lohndaten[jm]['LOHNFIKTIV'])

            agentur_zahlt_sozialabgaben = 0
            while (0 == 0):
                if len(lohndaten[jm]['LOHN-AN']) == 0:
                    break
                betrag = "%3.2f" % (-float(lohndaten[jm]['LOHN-AN'].pop(0)))
                remark = "Gehalt"
                if len(lohndaten[jm]['LOHN-AN']) > 0:
                    try:
                        float(lohndaten[jm]['LOHN-AN'][0])
                    except:
                        remark = lohndaten[jm]['LOHN-AN'].pop(0)
                if "KUGSOZ" in remark:
                    agentur_zahlt_sozialabgaben = 1
                if "KUG" in remark:
                    kugausz = kugausz - float(betrag)
                buchungen.append(jm + day + "  " + betrag + "*" + lohndaten[jm]['LFAKTOR'] + "  " + ukto + "-LOHN-AN  "
                             + [self.lohnkto,self.kugkto+"-LOHN"][int("KUG" in remark)]
                             + "-" + self.employee + "  0.00  " + remark)
                lohnsumme   = lohnsumme - float(betrag)
                export_slip = export_slip + "LOHN-AN " + ("%11.2f" % -float(betrag)) + "   " + remark + "\n"
                day         = "%02u" % (int(day)+1)

            export_slip = export_slip + ("LOHN-AR -ARBEITGEBER-   Arbeitgeberabgaben, davon " +
                                          ["","erstattete "][agentur_zahlt_sozialabgaben] +
                                          "KUG-Sozialabgaben:" +  " -ARBEITG_KUG-\n\n")

            o  = "keine Zahlungen\n"
			
            if jm in export_zahl:
                o  = export_zahl[jm]
            export_slip = export_slip + "Zahlungen:\n\n" + o
            export_slip = export_slip + "\nSteuern:       Aktuell    Vormonate    Jahressummen\n\n"

            lohn_ar         = [0.00,0.00]
            lohn_kug        = [0.00,0.00]
            art0            = ""
            vorletzter_wert = [0,0,0]
            for art in self.abgabenarten:
                if not art0 == art[0:2] and art[0:2] == "AN":
                    export_slip = export_slip + "\nSozialabgaben Arbeitnehmer:\n\n"
                if not art0 == art[0:2] and art[0:2] == "AR":
                    export_slip = export_slip + "\nSozialabgaben Arbeitgeber:\n\n"
                art0 = art[0:2]
                if not art in list(lohndaten[jm].keys()):
                    continue
                day          = "12"
                add          = ""
                buchungen1   = []
                consider_b   = False
                export_zeile = (art + "          ")[0:9]

                sum1         = 0.00
                letzter_wert = []  #  fuer jahressummenbildung
                for lssoz_str in lohndaten[jm][art]:

                    lssoz        = float(lssoz_str)
                    betrag       = float(betraege[jm][art])

                    if abs(betrag) > 0.001 or abs(lssoz) > 0.001:
                        consider_b = True

                    if add == "":
                        if jm in gesetzte_betraege and art in gesetzte_betraege[jm]:
#                            lssoz      = float(gesetzte_betraege[jm][art][0])
                            add        = gesetzte_betraege[jm][art][1]
                            consider_b = True
                        elif  abs( betrag - lssoz ) > 0.001:
                            add        = " (berechnet " + betraege[jm][art] + ")"
                            consider_b = True

                    sum1         = sum1 + lssoz
                    letzter_wert.append("%13.2f" % lssoz)
                    export_zeile = export_zeile + letzter_wert[-1]
                        
                    kto2  = re.sub(r"XXXX",lohndaten[jm]['NR'],self.gegenkonto[art])
                    zeile = jm + day + "  " + ("%3.2f"%lssoz) + "*" + lohndaten[jm]['LFAKTOR'] + "  " + ukto + "-" + art + "  " 
                    zeile = zeile + kto2 + "-" + self.employee + "  0.00  " + self.bezeichner[art] + add
                    if art[0:2] == "AR":
                        lohn_ar[int("Vor" in add)] = lohn_ar[int("Vor" in add)] - lssoz
                        ar_soz = ar_soz + lssoz
                    elif art[0:2] == "KN" or art[0:2] == "KR":
                        lohn_kug[int("Vor" in add)] = lohn_kug[int("Vor" in add)] - lssoz
                        kug_soz = kug_soz + lssoz
                    elif art[0:2] == "AN":
                        an_soz = an_soz + lssoz
                    elif art[0:2] == "AN":
                        an_soz = an_soz + lssoz
                    else:
                        st_soz = st_soz + lssoz
                    day   = "%02u" % (int(day)+1)
                    add   = ", Vormonate"
                    zeile = re.sub(r" 11-1512-PS"," 11-1503-PS",zeile)
                    if not ("Vormonate" in zeile and abs(lssoz) < 0.001):
                        buchungen1.append(zeile)

                jahressumme[art] = jahressumme[art] + sum1
                letzter_wert.append("%13.2f" % jahressumme[art])
                export_zeile     = export_zeile + letzter_wert[-1]
                export_zeile     = export_zeile + "   " + self.bezeichner[art]
                

                if consider_b:
                    for o in buchungen1:
                        buchungen.append(o)
                if re.search(r"^AR-KV-Z +0\.00 +0\.00 +0\.00 ",export_zeile):
                    continue
                export_slip = export_slip + export_zeile + "\n"
                if art in ("AN-KV-Z","AN-PV-Y","AR-KV-Z"):
                    export_zeile = art[0:5] + "     " + ( 
                        ( "(" + "%11.2f" % (float(vorletzter_wert[0]) + float(letzter_wert[0])) ) + ")" +
                        ( "(" + "%11.2f" % (float(vorletzter_wert[1]) + float(letzter_wert[1])) ) + ")" +
                        ( "(" + "%11.2f" % (float(vorletzter_wert[2]) + float(letzter_wert[2])) ) + ")" +
                          {"AN-KV-Z": "  Arbeitnehmer Gesamt  Krankenversicherung",
                           "AN-PV-Y": "  Arbeitnehmer Gesamt  Pflegeversicherung",
                           "AR-KV-Z": "  Arbeitgeber Gesamt   Krankenversicherung"
                           }[art] )
                    export_zeile = re.sub("\(( +)",'\\1'+"(",export_zeile,99)
                    export_slip = export_slip + export_zeile + "\n"
                vorletzter_wert = letzter_wert
                    
            
            ar = self.bezeichner['LOHN-AR']
            if abs(lohn_ar[0]) > 0.001 or abs(lohn_ar[1]) > 0.001:
                buchungen.append(jm + "10  " + ("%3.2f"%lohn_ar[0]) + "*" + lohndaten[jm]['LFAKTOR'] + "  " + ukto + "-LOHN-AR  " +
                                    self.sozkto + "-" + self.employee + "  0.00  " + ar)
            if abs(lohn_ar[1]) > 0.001:
                buchungen.append(jm + "11  " + ("%3.2f"%lohn_ar[1]) + "*" + lohndaten[jm]['LFAKTOR'] + "  " + ukto + "-LOHN-AR  " +
                                    self.sozkto + "-" + self.employee + "  0.00  " + ar + ", Vormonate")

            kug = self.bezeichner['LOHN-KUG'] + ["",", Erstattung durch Arbeitsagentur"][agentur_zahlt_sozialabgaben]
            if abs(lohn_kug[0]) > 0.001 or abs(lohn_kug[1]) > 0.001:
                buchungen.append(jm + "10  " + ("%3.2f"%lohn_kug[0]) + "*" + lohndaten[jm]['LFAKTOR'] + "  " + ukto + "-LOHN-KUG  " +
                                    [self.sozkto,self.kugkto+"-SOZ"][agentur_zahlt_sozialabgaben]
                                    + "-" + self.employee + "  0.00  " + kug)
            if abs(lohn_kug[1]) > 0.001:
                buchungen.append(jm + "11  " + ("%3.2f"%lohn_kug[1]) + "*" + lohndaten[jm]['LFAKTOR'] + "  " + ukto + "-LOHN-KUG  " +
                                    [self.sozkto,self.kugkto+"-SOZ"][agentur_zahlt_sozialabgaben]
                                    + "-" + self.employee + "  0.00  " + kug + ", Vormonate")

            netto = lohnsumme - st_soz - an_soz
            try:
                ausz = float(export_sum[jm])
            except:
                ausz = 0.00
            ueber = ausz - netto

            jahressumme[1] = jahressumme[1] + lohnsumme
            jahressumme[2] = jahressumme[2] + st_soz
            jahressumme[3] = jahressumme[3] + an_soz
            jahressumme[4] = jahressumme[4] + netto
            jahressumme[5] = jahressumme[5] + ausz
            jahressumme[6] = jahressumme[6] + ueber
            jahressumme[7] = jahressumme[7] + fiktives_gehalt
            jahressumme[8] = jahressumme[8] + kugausz

            export_slip  = export_slip + "\n"
            if (abs(jahressumme[7]) > 0.00001):
                export_zeile = "fiktives Gehalt bei KUG:(" + ("%10.2f" % fiktives_gehalt) + ")(" + ("%11.2f" % jahressumme[7]) + ")\n\n"
                export_zeile = re.sub("\(( +)",'\\1'+"(",export_zeile,99)
                export_slip  = export_slip + export_zeile 
            export_slip  = export_slip + "Gehalt Brutto:        " + ("%13.2f" % (lohnsumme-kugausz)) + ("%13.2f" % (jahressumme[1]-jahressumme[8])) + "\n"
            export_slip  = export_slip + "minus Steuern:        " + ("%13.2f" % st_soz)    + ("%13.2f" % jahressumme[2]) + "\n"
            export_slip  = export_slip + "minus Sozialabgaben:  " + ("%13.2f" % an_soz)    + ("%13.2f" % jahressumme[3]) + "\n"
            export_slip  = export_slip + "                            -------      -------\n"
            export_slip  = export_slip + "Gehalt Netto:         " + ("%13.2f" % (netto-kugausz))     + ("%13.2f" % (jahressumme[4]-jahressumme[8])) + "\n"
            if (abs(jahressumme[8]) > 0.00001):
                export_slip = export_slip + "Zahlung KUG:          " + ("%13.2f" % kugausz) + ("%13.2f" % jahressumme[8]) + "\n"
            export_slip  = export_slip + "                            -------      -------\n"
            if (abs(jahressumme[8]) > 0.00001):
                export_zeile = "Netto plus KUG gesamt:" + ("%13.2f" % netto) + "" + ("%13.2f" % jahressumme[1]) + "\n"
                export_zeile = re.sub("\(( +)",'\\1'+"(",export_zeile,99)
                export_slip  = export_slip + export_zeile 
            export_slip  = export_slip + "Auszahlung:           " + ("%13.2f" % ausz)      + ("%13.2f" % jahressumme[5]) + "\n"
            export_slip  = export_slip + "                            -------      -------\n"
            export_slip  = export_slip + "Ueberzahlung:         " + ("%13.2f" % ueber)     + ("%13.2f" % jahressumme[6]) + "        (Werte in Klammern: nachrichtlich)\n"
            export_slip  = re.sub(r"-ARBEITGEBER-",("%11.2f" % (ar_soz+kug_soz)),export_slip)
            export_slip  = re.sub(r"-ARBEITG_KUG-",("%3.2f" % kug_soz),export_slip)
            
            m = re.search(r"^(.*?)(LOHN-AN.*?Ueberzahlung.*?\n)(.*)$",export_slip0,re.DOTALL)
            if m:
                export_slip = m.group(1) + export_slip + m.group(3)

            export_slip = re.sub(r" \d\d\/\d\d\d\d"," "+jm[4:6]+"/"+jm[0:4],export_slip)
            
            export_slip = re.sub(r", davon [a-z]* ?KUG-[^\n]+ 0.00 *","",export_slip,9999)
            export_sl0  = export_slip
            export_slip = re.sub(r"\n(KN|KR)\S+ +0.00 +0.00 +0.00 +([^\n]+)","",export_slip,9999)
            if re.search(r"\n(KN|KR)",export_slip):
                export_slip = re.sub(r"\n(LS|SZ|KI|AR-ST|AR-PS) +0.00 +0.00 +0.00 +([^\n]+)","",export_sl0,9999)
                export_slip = re.sub(r", davon [a-z]* ?KUG-[^\n]+ 0.00 *","",export_slip,9999)
                if not re.search("\n(LS|SZ|KI)   ",export_slip,re.DOTALL):
                    export_slip = re.sub(r"\nSteuern:( .*)\n","\nAbgaben:\\1    [KEINE STEUERN]",export_slip,re.DOTALL)
                export_slip = re.sub(r"\n(LOHN-KUG) +0.00 +([^\n]+)","",export_slip,9999)

            if jm in ktoslips:
                self.lstfile[jm] = None
                self.lsttext[jm] = None
            else:
                m = re.search(r"^(.*?\D)(\d\d\d\d)(\D+)(\d\d)(\D.*)$",ktoslip0)
                if m:
                    self.lstfile[jm] = m.group(1) + jm[0:4] + m.group(3) + jm[4:6] + m.group(5)
                else:
                    self.lstfile[jm] = "lohnbescheinigung_" +jm[0:4] + "_" + jm[4:6] + ".md"
                self.lsttext[jm] = export_slip

#                print ("---->   ",jm)
#                print(self.lstfile[jm])
#                print(self.lsttext[jm])

        self.diff = ""
        is_null   = True
        for art in self.abgabenarten:
            betrag          = "%13.2f" % diffs[art]
            self.diff = self.diff + (art+"           ")[0:9] + betrag + "\n"
            if abs(diffs[art]) > 0.001:
                is_null = False
        if is_null:
            self.diff = ""
            
        
        return ("\n".join(rest_lines+buchungen)+"\n")
        

        
#*************************************************************************

    def read_lohnbescheinigung (self,slip):
    
        text    = ""
        monate  = "JA|FE|MR|AP|MA|JN|JL|AU|SE|OC|NO|DE|01|02|03|04|05|06|07|08|09|10|11|12"
        abgaben = "|".join(self.abgabenarten+['LOHN-AN','ZAHL'])
        
        m             = re.search(r"^(.*)[\\\/](.*)[\\\/]*$",os.path.abspath("."))
        self.employee = m.group(2)

        m = re.search(r"(\d\d\d\d)_("+monate+")",slip)
        if not m:
            return(None)
        
        jahr  = m.group(1)
        monat = "%02u" % ( (monate.split("|").index(m.group(2)) % 12) + 1 )
        text  = open(slip).read()
        text  = re.sub("AR-KV ","AR-KV-S ",text)
        erg   = { "FIX": int("FIX" in text) }

        for zeile in text.split("\n"):
            m = re.search(r"^("+abgaben+").*? (\-?\d+)[,\.](\d\d) *(.*?) *$",zeile)
            if m:
                abgabe = m.group(1)
                betrag = m.group(2)+"."+m.group(3)
                if not abgabe in erg:
                    erg[abgabe] = []
                erg[abgabe].append(betrag)
                if len(m.group(4)) > 0:
                    rem = m.group(4)
                    m   = re.search(r"^ *(\-?\d+)[,\.](\d\d) .*$",rem)
                    if m:
                        erg[abgabe].append(m.group(1)+"."+m.group(2))
                    else:
                        erg[abgabe].append(rem)

        for art in self.abgabenarten:
            if not art in erg:
                erg[art] = ["0.0","0.0","0.0"]
                
        return(jahr+monat,erg)

#*************************************************************************

    def set_rahmendaten (self,jw,jahr,monat):
    
        if monat[0] == "1":
            monat = { "10": "A", "11": "B", "12": "C"}[ monat ]
        else:
            monat = monat[1]

        jw['KKNAME'] = {
                         "1510": "DAK",
                         "1512": "MINIJO",
                         "1513": "BKKFUT",
                         "1514": "AOKHES",
                         "1515": "MOBILO",
                         "1516": "SBK",
                         "1517": "TKK7",
                         "1518": "BARMER",
                         "1519": "DEBEKA",
                         "1520": "AOKRP5",
                         "1521": "AOKNW5",
                         "1522": "AOKBW5",
                         "1523": "IKKCLA",
                         "1524": "HEK" 
                         } [ jw['NR'] ]


        jw['ZA'] = "0.0"
        jw['SOLIANTEIL'] = 0.055
        

        if jahr == "2007":
        
            jw['RLIMIT']  = "5800"
            jw['KLIMIT']  = "3937.50"
            jw['RV'] = ["9.95","15"]  [ int( jw['NR'] == "1512" ) ] 
            jw['AV'] = ["2.1" ,"3.6"] [ int( jw['NR'] == "1512" ) ] 
            jw['KV'] = { "1510": "7.25", "1512" : "13",  "1513": "6.95", "1515": "6.45"} [ jw['NR'] ]  
            jw['KG'] = "0.0"
            jw['ZU'] = { "1510": "0.9",  "1512" : "0.0", "1513": "0.9",  "1515": "0.9"}  [ jw['NR'] ]  
            jw['ZV'] = "0.9"
            jw['PV'] = "0.85"
            jw['PZ'] = "0.25"
            jw['U1'] = { "1510": "1.2",  "1512" : "0.1",  "1513": "1.6",  "1515": "1.1"}  [ jw['NR'] ]  
            jw['U2'] = { "1510": "0.18", "1512" : "0.0",  "1513": "0.1",  "1515": "0.15"} [ jw['NR'] ]  
            jw['U3'] = "0.0"

            '''
PERSON         LST   SZ  KS   KK      KNR   PL ST   RVN   AVN   KVN  PVN  ZUN   KIN  ART  RVR   AVR  KVR  PVR   U1    U2   U3
-----------------------------------------------------------------------------------------------------------------------------
arjasanow      0       0  0   Mini    1512  25  0     0    0     0     0   0     0  999     0    0     0    0    0     0    0
cpkettner      1     5.5  0  Mobiloil 1515   0  0  9.95  2.1  6.45  0.85 0.9  0.25  999  9.95  2.1  6.45 0.85  1.1  0.15    0
dblaesche      0       0  0   Mini    1512  25  0     0    0     0     0   0     0  999     0    0     0    0    0     0    0
etoo           0       0  0   Mini    1512  25  0     0    0     0     0   0     0  999     0    0     0    0    0     0    0
jclaussnitzer  0       0  0   Mini    1512  25  0     0    0     0     0   0     0  999     0    0     0    0    0     0    0
jengewald      1       0  0   Mini    1512   0  2     0    0     0     0   0     0  991    15    0    13    0  0.1     0    0
jkoch          0       0  0   Mini    1512  25  0     0    0     0     0   0     0  999     0    0     0    0    0     0    0
klaewer        1     5.5  0   DAK     1510   0  0  9.95  2.1  7.25  0.85 0.9  0.25  331  9.95  2.1  7.25 0.85  1.2  0.18    0
oppenl         0       0  0   Mini    1512  25  0     0    0     0     0   0     0  999     0    0     0    0    0     0    0
20071201       1     5.5  8e BKKfutur 1513   0  0  9.95  2.1  6.95  0.85 0.9  0.25  999  9.95  2.1  6.95 0.85  1.6  0.10    0
tfelder        0       0  0   Mini    1512  25  0     0    0     0     0   0     0  999     0    0     0    0    0     0    0
tjungblut      0       0  0   Mini    1512  25  0     0    0     0     0   0     0  999     0    0     0    0    0     0    0
ulerich        0       0  0   Mini    1512  25  0     0    0     0     0   0     0  999     0    0     0    0    0     0    0
wkapraun       0       0  0   Mini    1512  25  0     0    0     0     0   0     0  999     0    0     0    0    0     0    0
-----------------------------------------------------------------------------------------------------------------------------
'''

        if jahr == "2008":
        
            for zeitraum in ("123456","789ABC"):
                if monat in zeitraum:
                    break

            jw['RLIMIT']  = "5800"
            jw['KLIMIT']  = "3937.50"
            jw['RV'] = ["9.95","15"]   [ int( jw['NR'] == "1512" ) ] 
            jw['AV'] = ["1.65" ,"3.6"] [ int( jw['NR'] == "1512" ) ] 
            jw['KV'] = { "1510": "7.25", "1512" : "13",  "1513": "7.05", "1518": "7.2"} [ jw['NR'] ]  
            jw['KG'] = "0.0"
            jw['ZU'] = { "1510": "0.9",  "1512" : "0.0", "1513": "0.9",  "1518": "0.9"}  [ jw['NR'] ]  
            jw['ZV'] = "0.9"
            jw['PV'] = { "123456": "0.85", "789ABC": "0.975"} [zeitraum]
            jw['PZ'] = "0.25"
            jw['U1'] = { "1510": "1.2",  "1512" : "0.1",  "1513": "1.2",  "1518": "1.0"}  [ jw['NR'] ]  
            jw['U2'] = { "1510": "0.15", "1512" : "0.0",  "1513": "0.1",  "1518": "0.15"} [ jw['NR'] ]  
            jw['U3'] = "0.0"


            '''
PERSON         LST   SZ  KS  PL  KK     KNR    RVN   AVN  KVN   PVN  ZUN   KIN  ART  RVR   AVR  KVR  PVR  ST   U1    U2   U3
----------------------------------------------------------------------------------------------------------------------------
arjasanow      0       0  0  25  Minijob 1512     0    0    0     0    0     0  999     0    0    0    0   0    0     0    0
20081001       6     5.5  0   0  BEK     1518  9.95    0    0     0    0     0  999  9.95    0    0    0   0  1.0  0.15    0
20081201       6     5.5  0   0  BEK     1518  9.95    0    0     0    0     0  999  9.95    0    0    0   0  1.0  0.15    0
axrxjasanow       1     5.5  0   0  BEK     1518  9.95 1.65  7.2  0.85  0.9  0.25  999  9.95 1.65  7.2 0.85   0  1.0  0.15    0
ashawky        0       0  0  25  Minijob 1512     0    0    0     0    0     0  999     0    0    0    0   0    0     0    0
cnawrot        0       0  0  25  Minijob 1512     0    0    0     0    0     0  999     0    0    0    0   0    0     0    0
dblaesche      0       0  0  25  Minijob 1512     0    0    0     0    0     0  999     0    0    0    0   0    0     0    0
hmaamoun       0       0  0  25  Minijob 1512     0    0    0     0    0     0  999     0    0    0    0   0    0     0    0
hzaazou        0       0  0  25  Minijob 1512     0    0    0     0    0     0  999     0    0    0    0   0    0     0    0
jclaussnitzer  0       0  0  25  Minijob 1512     0    0    0     0    0     0  999     0    0    0    0   0    0     0    0
jengewald      1       0  0   0  Minijob 1512     0    0    0     0    0     0  991    15    0   13    0   2  0.1     0    0
jkaiser        0       0  0  25  Minijob 1512     0    0    0     0    0     0  999     0    0    0    0   0    0     0    0
jkoch          0       0  0  25  Minijob 1512     0    0    0     0    0     0  999     0    0    0    0   0    0     0    0
jschuladen     0       0  0  25  Minijob 1512     0    0    0     0    0     0  999     0    0    0    0   0    0     0    0
klangschwager  0       0  0  25  Minijob 1512     0    0    0     0    0     0  999     0    0    0    0   0    0     0    0
mtruemper      0       0  0  25  Minijob 1512     0    0    0     0    0     0  999     0    0    0    0   0    0     0    0
mweber         0       0  0  25  Minijob 1512     0    0    0     0    0     0  999     0    0    0    0   0    0     0    0
oppenl         1     5.5  8e  0 BKKfutur 1513  9.95 1.65 7.05  0.85  0.9  0.25  999  9.95 1.65 7.05 0.85   0  1.2  0.10    0
20080701       1     5.5  8e  0 BKKfutur 1513  9.95 1.65 7.05 0.975  0.9  0.25  999  9.95 1.65 7.05 0.975  0  1.2  0.10    0
sgeier         0       0  0  25  Minijob 1512     0    0    0     0    0     0  999     0    0    0    0   0    0     0    0
stockbauer     0       0  0   0  Minijob 1512     0    0    0     0    0     0  991    15    0   13    0   2  0.1     0    0
tfelder        0       0  0  25  Minijob 1512     0    0    0     0    0     0  999     0    0    0    0   0    0     0    0
20080601       6     5.5  8e  0  DAK     1510  9.95 1.65 7.25  0.85  0.9  0.25  999  9.95 1.65 7.25  0.85  0  1.2  0.15    0
20080701       6     5.5  8e  0  DAK     1510  9.95 1.65 7.25 0.975  0.9  0.25  999  9.95 1.65 7.25 0.975  0  1.2  0.15    0
20081201       6     5.5  8e  0  DAK     1510  9.95 1.65 7.25 0.975  0.9  0.25  999  9.95 1.65 7.25 0.975  0  1.2  0.15    0
tjungblut      0       0  0  25  Minijob 1512     0    0    0     0    0     0  999     0    0    0    0   0    0     0    0
20081001       6     5.5  0   0  DAK     1510  9.95 1.65 7.25 0.975  0.9  0.25  999  9.95 1.65 7.25 0.975  0  1.2  0.15    0
20081201       6     5.5  0   0  DAK     1510  9.95 1.65 7.25 0.975  0.9  0.25  999  9.95 1.65 7.25 0.975  0  1.2  0.15    0
tkinzl         0       0  0  25  Minijob 1512     0    0    0     0    0     0  999     0    0    0    0   0    0     0    0
20081001       0       0  0   0  Minijob 1512     0    0    0     0    0     0  991    15    0   13    0   2  0.1     0    0
wkapraun       0       0  0  25  Minijob 1512     0    0    0     0    0     0  999     0    0    0    0   0    0     0    0
wsarhan        0       0  0  25  Minijob 1512     0    0    0     0    0     0  999     0    0    0    0   0    0     0    0
----------------------------------------------------------------------------------------------------------------------------
'''

        if jahr == "2009":
        
            for zeitraum in ("123456","789ABC"):
                if monat in zeitraum:
                    break

            jw['RLIMIT']  = "5800"
            jw['KLIMIT']  = "3937.50"
            jw['RV'] = ["9.95","15"]  [ int( jw['NR'] == "1512" ) ] 
            jw['AV'] = ["1.4" ,"3.6"] [ int( jw['NR'] == "1512" ) ] 
            jw['KV'] = [ {"123456": "7.3", "789ABC": "7.0"}[zeitraum], "13"]  [ int( jw['NR'] == "1512" ) ] 
            jw['KG'] = ["0.3","0.0"] [ int( jw['NR'] == "1512" ) ] 
            jw['ZU'] = { "1510": "0.9",  "1512" : "0.0", "1518": "0.9"}  [ jw['NR'] ]  
            jw['ZV'] = "0.9"
            jw['PV'] = "0.975"
            jw['PZ'] = "0.25"
            jw['U1'] = { "1510": "1.8",  "1512" : "0.6",  "1518": "1.4"}  [ jw['NR'] ]  
            jw['U2'] = { "1510": "0.2",  "1512" : "0.07", "1518": "0.22"} [ jw['NR'] ]  
            jw['U3'] = "0.1"


            '''
PERSON         LST   SZ  KS  PL  KK     KNR    RVN   AVN  KVN  PVN   ZUN   KIN  ART  RVR   AVR  KVR  PVR  ST   U1    U2   U3
----------------------------------------------------------------------------------------------------------------------------
arjasanow      6     5.5  0e  0  BEK     1518  9.95    0    0     0    0     0  999  9.95    0    0    0   0  1.4  0.22  0.1
20090301       6     5.5  0   0  BEK     1518  9.95    0    0     0    0     0  999  9.95    0    0    0   0  1.4  0.22  0.1
axrxjasanow      1     5.5  0   0  BEK     1518  9.95  1.4  7.3 0.975  0.9  0.25  999  9.95  1.4  7.3 0.975  0  1.4  0.22  0.1
dkullick       1       0  0   0  Minijob 1512     0    0    0     0    0     0  991    15    0   13    0   2  0.6  0.07  0.1
jengewald      1       0  0   0  Minijob 1512     0    0    0     0    0     0  991    15    0   13    0   2  0.6  0.07  0.1
klangschwager  0       0  0  25  Minijob 1512     0    0    0     0    0     0  999     0    0    0    0   0    0     0    0
srodenberg     0       0  0  25  Minijob 1512     0    0    0     0    0     0  999     0    0    0    0   0    0     0    0
tfelder        6     5.5  8e  0  DAK     1510  9.95  1.4  7.3 0.975  0.9  0.25  999  9.95  1.4  7.3 0.975  0  1.8   0.2  0.1
tjungblut      1       0  0   0  Minijob 1512     0    0    0     0    0     0  991    15    0   13    0   2  0.6  0.07  0.1
ukrohn         1       0  0   0  Minijob 1512     0    0    0     0    0     0  991    15    0   13    0   2  0.6  0.07  0.1
wsarhan        0       0  0  25  Minijob 1512     0    0    0     0    0     0  999     0    0    0    0   0    0     0    0
----------------------------------------------------------------------------------------------------------------------------
'''


        if jahr == "2010":
        
            jw['RLIMIT']  = "5800"
            jw['KLIMIT']  = "3937.50"
            jw['RV'] = ["9.95","15"]  [ int( jw['NR'] == "1512" ) ] 
            jw['AV'] = ["1.4" ,"3.6"] [ int( jw['NR'] == "1512" ) ] 
            jw['KV'] = ["7.0","13"]  [ int( jw['NR'] == "1512" ) ] 
            jw['KG'] = ["0.3","0.0"] [ int( jw['NR'] == "1512" ) ] 
            jw['ZU'] = { "1510": "0.9",  "1512" : "0.0", "1518": "0.9"}  [ jw['NR'] ]  
            jw['ZV'] = "0.9"
            jw['PV'] = "0.975"
            jw['PZ'] = "0.25"
            jw['U1'] = { "1510": "1.8",  "1512" : "0.6",  "1518": "1.4"}  [ jw['NR'] ]  
            jw['U2'] = { "1510": "0.2",  "1512" : "0.07", "1518": "0.22"} [ jw['NR'] ]  
            jw['U3'] = "0.41"


            '''
PERSON         LST   SZ  KS  PL KK     KNR    RVN   AVN  KVN  PVN   ZUN   KIN  ART  RVR   AVR  KVR  PVR  ST    U1    U2   U3
----------------------------------------------------------------------------------------------------------------------------
arjasanow      1     5.5  9   0 BEK     1513  9.95    0    0     0    0     0  999  9.95    0    0    0   0   1.4  0.22  0.1
jengewald      1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13    0   2   0.6  0.07 0.41
klangschwager  1       0  0  25 Minijob 1512     0    0    0     0    0     0  999     0    0    0    0   0     0     0    0
tfelder        1     5.5  9   0 DAK     1513  9.95  1.4  7.3 0.975  0.9  0.25  999  9.95  1.4  7.3 0.975  0   1.8   0.2 0.41
tjungblut      1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13    0   2   0.6  0.07 0.41
----------------------------------------------------------------------------------------------------------------------------
'''

        if jahr == "2011":
        
            jw['RLIMIT']  = "5800"
            jw['KLIMIT']  = "3937.50"
            jw['RV'] = ["9.95","15"]  [ int( jw['NR'] == "1512" ) ] 
            jw['AV'] = ["1.5" ,"3.6"] [ int( jw['NR'] == "1512" ) ] 
            jw['KV'] = ["7.3","13"]  [ int( jw['NR'] == "1512" ) ] 
            jw['KG'] = ["0.3","0.0"] [ int( jw['NR'] == "1512" ) ] 
            jw['ZU'] = { "1512" : "0.0",  "1514": "0.9",  "1515": "0.9", "1516": "0.9", "1517": "0.9", "1518": "0.9"}  [ jw['NR'] ]  
            jw['ZV'] = "0.9"
            jw['PV'] = "0.975"
            jw['PZ'] = "0.25"
            jw['U1'] = { "1512" : "0.6",  "1514": "1.6",  "1515": "3.5", "1516": "1.35", "1517": "1.7", "1518": "1.7"}  [ jw['NR'] ]  
            jw['U2'] = { "1512" : "0.14", "1514": "0.39", "1515": "0.36","1516": "0.21", "1517": "0.3", "1518": "0.33"} [ jw['NR'] ]  
            jw['U3'] = "0.0"


            '''
PERSON         LST   SZ  KS  PL KK     KNR    RVN   AVN  KVN   PVN  ZUN   KIN  ART  RVR   AVR  KVR   PVR ST    U1    U2   U3
----------------------------------------------------------------------------------------------------------------------------
arjasanow      1     5.5  0   0 BEK     1518  9.95    0    0     0    0     0  999  9.95    0    0     0  0   1.7  0.33    0
ccsengery      1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   0.6  0.14    0
ddienlin       1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   0.6  0.14    0
20111101       1     5.5  0   0 AOK     1514  9.95    0    0     0    0     0  999  9.95    0    0     0  0   1.6  0.39    0
dperic         1     5.5  8r  0 TechnKK 1517  9.95    0    0     0    0     0  999  9.95    0    0     0  0   1.7  0.3     0
hparfuss       3     5.5  0   0 BKKSiem 1516     0    0  7.0 0.975  0.9  0.25  999  9.95  1.5  7.0 0.975  0  1.35  0.21    0
jengewald      1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   0.6  0.14    0
jfriedrichs    1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   0.6  0.14    0
jkleckow       1     5.5  8e  0 BKKMOil 1515  9.95    0    0     0    0     0  999  9.95    0    0     0  0   3.5  0.36    0
mherrschel     1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   0.6  0.14    0
----------------------------------------------------------------------------------------------------------------------------
'''

        if jahr == "2012":
        
            jw['RLIMIT']  = "5800"
            jw['KLIMIT']  = "3937.50"
            jw['RV'] = ["9.8","15"]   [ int( jw['NR'] == "1512" ) ] 
            jw['AV'] = ["1.5" ,"3.6"] [ int( jw['NR'] == "1512" ) ] 
            jw['KV'] = ["7.3","13"] [ int( jw['NR'] == "1512" ) ] 
            jw['KG'] = ["0.3","0.0"] [ int( jw['NR'] == "1512" ) ] 
            jw['ZU'] = { "1512" : "0.0",  "1514": "0.9",  "1515": "0.9", "1516": "0.9", "1517": "0.9", "1518": "0.9"}  [ jw['NR'] ]  
            jw['ZV'] = "0.9"
            jw['PV'] = "0.975"
            jw['PZ'] = "0.25"
            jw['U1'] = { "1512" : "0.7",  "1514": "1.6",  "1515": "3.5", "1516": "1.35", "1517": "2.1",  "1518": "1.7"}  [ jw['NR'] ]  
            jw['U2'] = { "1512" : "0.14", "1514": "0.39", "1515": "0.36","1516": "0.28", "1517": "0.39", "1518": "0.33"} [ jw['NR'] ]  
            jw['U3'] = "0.04"

            '''
PERSON         LST   SZ  KS  PL KK     KNR    RVN   AVN  KVN   PVN  ZUN   KIN  ART  RVR   AVR  KVR   PVR ST    U1    U2   U3
----------------------------------------------------------------------------------------------------------------------------
arjasanow      1     5.5  0   0 BEK     1518   9.8    0    0     0    0     0  999   9.8    0    0     0  0   1.7  0.33 0.04
ccsengery      1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   0.7  0.14 0.04
ddienlin       1     5.5  0   0 AOK     1514   9.8    0    0     0    0     0  999   9.8    0    0     0  0   1.6  0.39 0.04
dperic         1     5.5  8r  0 TechnKK 1517   9.8    0    0     0    0     0  999   9.8    0    0     0  0   2.1  0.39 0.04
hparfuss       3     5.5  0   0 BKKSiem 1516     0    0  7.0 0.975  0.9  0.25  999   9.8  1.5  7.0 0.975  0  1.35  0.28 0.04
jengewald      1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   0.7  0.14 0.04
jfriedrichs    1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   0.7  0.14 0.04
jkleckow       1     5.5  8e  0 BKKMOil 1515   9.8    0    0     0    0     0  999   9.8    0    0     0  0   3.5  0.36 0.04
mherrschel     1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   0.7  0.14 0.04
vgabriel       1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   0.7  0.14 0.04
----------------------------------------------------------------------------------------------------------------------------
'''

        if jahr == "2013":
        
            jw['RLIMIT']  = "5800"
            jw['KLIMIT']  = "3937.50"
            jw['RV'] = ["9.45","15"]  [ int( jw['NR'] == "1512" ) ] 
            jw['AV'] = ["1.5" ,"3.6"] [ int( jw['NR'] == "1512" ) ] 
            jw['KV'] = ["7.3","13"]  [ int( jw['NR'] == "1512" ) ] 
            jw['KG'] = ["0.3","0.0"] [ int( jw['NR'] == "1512" ) ] 
            jw['ZU'] = { "1512" : "0.0",  "1516": "0.9", "1517": "0.9", "1518": "0.9", "1519": "0.9"}  [ jw['NR'] ]  
            jw['ZV'] = "0.9"
            jw['PV'] = "1.025"
            jw['PZ'] = "0.25"
            jw['U1'] = { "1512" : "0.7",  "1516": "1.35", "1517": "1.7",  "1518": "1.7",  "1519": "1.7"}  [ jw['NR'] ]  
            jw['U2'] = { "1512" : "0.14", "1516": "0.28", "1517": "0.33", "1518": "0.38", "1519": "0.34"} [ jw['NR'] ]  
            jw['U3'] = "0.15"

            '''
PERSON         LST   SZ  KS  PL KK     KNR    RVN   AVN  KVN   PVN  ZUN   KIN  ART  RVR   AVR  KVR   PVR ST    U1    U2   U3
----------------------------------------------------------------------------------------------------------------------------
arjasanow      1     5.5  0   0 BEK     1518  9.45    0    0     0    0     0  999  9.45    0    0     0  0   1.7  0.38 0.15
20130601       1     5.5  0   0 BEK     1518  9.45    0    0     0    0     0  999  9.45    0    0     0  0   1.7  0.38 0.15
20131001       1     5.5  0   0 BEK     1518  9.45  1.5  7.3 1.025  0.9     0  999  9.45  1.5  7.3 1.025  0   1.7  0.38 0.15
ccsengery      1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   0.7  0.14 0.15
ddienlin       1     5.5  0   0 Debeka  1519  9.45    0    0     0    0     0  999  9.45    0    0     0  0   1.7  0.34 0.15
dperic         1     5.5  8r  0 TechnKK 1517  9.45    0    0     0    0     0  999  9.45    0    0     0  0   1.7  0.33 0.15
hparfuss       3     5.5  0   0 BKKSiem 1516     0    0  7.0 1.025  0.9  0.25  999  9.45  1.5  7.0 1.025  0  1.35  0.28 0.15
jengewald      1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   0.7  0.14 0.15
jfriedrichs    1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   0.7  0.14 0.15
tjungblut      1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   0.7  0.14 0.15
mherrschel     1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   0.7  0.14 0.15
stschwarz      1.05  5.5  0   0 TechnKK 1517  9.45  1.5  7.3 1.025  0.9     0  999  9.45  1.5  7.3 1.025  0   1.7  0.33 0.15
swonneberger   3.20  5.5  0   0 TechnKK 1517  9.45  1.5  7.3 1.025  0.9     0  999  9.45  1.5  7.3 1.025  0   1.7  0.33 0.15
vgabriel       1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   0.7  0.14 0.15
lpschierer     1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   0.7  0.14 0.15
----------------------------------------------------------------------------------------------------------------------------
'''

        if jahr == "2014":


            jw['RLIMIT']  = "5950"
            jw['KLIMIT']  = "4050"
            jw['RV'] = ["9.45","15"]  [ int( jw['NR'] == "1512" ) ] 
            jw['AV'] = ["1.5" ,"3.6"] [ int( jw['NR'] == "1512" ) ] 
            jw['KV'] = ["7.3","13"]  [ int( jw['NR'] == "1512" ) ] 
            jw['KG'] = ["0.3","0.0"] [ int( jw['NR'] == "1512" ) ] 
            jw['ZU'] = { "1512" : "0.0",  "1516": "0.9", "1517": "0.9", "1518": "0.9", "1519": "0.9"}  [ jw['NR'] ]  
            jw['ZV'] = "0.9"
            jw['PV'] = "1.025"
            jw['PZ'] = "0.25"
            jw['U1'] = { "1512" : "0.7",  "1516": "1.35", "1517": "1.7",  "1518": "1.7",  "1519": "1.7"}  [ jw['NR'] ]  
            jw['U2'] = { "1512" : "0.14", "1516": "0.28", "1517": "0.33", "1518": "0.38", "1519": "0.37"} [ jw['NR'] ]  
            jw['U3'] = "0.15"

            '''

PERSON         LST   SZ  KS  PL KK     KNR    RVN   AVN  KVN   PVN  ZUN   KIN  ART  RVR   AVR  KVR   PVR ST    U1    U2   U3
----------------------------------------------------------------------------------------------------------------------------
arjasanow      1     5.5  0   0 BEK     1518  9.45  1.5  7.3 1.025  0.9     0  999  9.45  1.5  7.3 1.025  0   1.7  0.38 0.15
ccsengery      1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   0.7  0.14 0.15
ddienlin       1     5.5  0   0 Debeka  1519  9.45    0    0     0    0     0  999  9.45    0    0     0  0   1.7  0.37 0.15
dperic         1     5.5  8r  0 TechnKK 1517  9.45    0    0     0    0     0  999  9.45    0    0     0  0   1.7  0.33 0.15
hparfuss       1     5.5  0   0 BKKSiem 1516     0    0  7.3 1.025  0.9  0.25  999  9.45  1.5  7.3 1.025  0  1.35  0.28 0.15
jengewald      1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   0.7  0.14 0.15
jfriedrichs    1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   0.7  0.14 0.15
tjungblut      1     5.5  0   0 TechnKK 1517  9.45  1.5  7.3 1.025  0.9  0.25  999  9.45  1.5  7.3 1.025  0   1.7  0.33 0.15
mherrschel     1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   0.7  0.14 0.15
stschwarz      4.15  5.5  8r  0 TechnKK 1517  9.45  1.5  7.3 1.025  0.9     0  999  9.45  1.5  7.3 1.025  0   1.7  0.33 0.15
swonneberger   3.20  5.5  0   0 TechnKK 1517  9.45  1.5  7.3 1.025  0.9     0  999  9.45  1.5  7.3 1.025  0   1.7  0.33 0.15
vgabriel       1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   0.7  0.14 0.15
lpschierer     1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   0.7  0.14 0.15
rbetageri      1     5.5  0   0 TechnKK 1517  9.45  1.5  7.3 1.025  0.9  0.25  999  9.45  1.5  7.3 1.025  0   1.7  0.33 0.15
----------------------------------------------------------------------------------------------------------------------------
'''


#        if jahr == "2015a":
#        
#            jw['RLIMIT']  = "6050"
#            jw['KLIMIT']  = "4125"
#            jw['RV'] = ["9.35","15"] [ int( jw['NR'] == "1512" ) ] 
#            jw['AV'] = "1.5"
#            jw['KV'] = ["7.3","13"]  [ int( jw['NR'] == "1512" ) ] 
#            jw['ZU'] = { "1512" : "0.0",  "1517": "1.1", "1519": "1.1"}  [ jw['NR'] ]  
#            jw['ZV'] = "1.1"
#            jw['PV'] = "1.175"
#            jw['PZ'] = "0.25"
#            jw['U1'] = { "1512" : "0.7",  "1517": "1.6",  "1519": "1.6"}  [ jw['NR'] ]  
#            jw['U2'] = { "1512" : "0.24", "1517": "0.49", "1519": "0.37"} [ jw['NR'] ]  
#            jw['U3'] = "0.15"

        if jahr == "2015":
        
            jw['RLIMIT']  = "6050"
            jw['KLIMIT']  = "4125"
            jw['RV'] = ["9.35","15"]  [ int( jw['NR'] == "1512" ) ] 
            jw['AV'] = ["1.5" ,"3.6"] [ int( jw['NR'] == "1512" ) ] 
            jw['KV'] = ["7.3","13"]  [ int( jw['NR'] == "1512" ) ] 
            jw['KG'] = ["0.3","0.0"] [ int( jw['NR'] == "1512" ) ] 
            jw['ZU'] = { "1512" : "0.0",  "1517": "0.8", "1519": "1.1"}  [ jw['NR'] ]  
            jw['ZV'] = "0.9"
            jw['PV'] = "1.175"
            jw['PZ'] = "0.25"
            jw['U1'] = { "1512" : "1.0", "1517": "1.6",  "1519": "1.6"}  [ jw['NR'] ]  
            jw['U2'] = { "1512" : "0.3", "1517": "0.49", "1519": "0.37"} [ jw['NR'] ]  
            jw['U3'] = "0.15"

            '''
PERSON         LST   SZ  KS  PL KK     KNR    RVN   AVN  KVN   PVN  ZUN   KIN  ART  RVR   AVR  KVR   PVR ST    U1    U2   U3
----------------------------------------------------------------------------------------------------------------------------
ddienlin       1     5.5  0   0 Debeka  1519  9.35    0    0     0    0     0  999  9.35    0    0     0  0   1.6  0.37 0.15
rndengang      1     5.5  0   0 TechnKK 1517  9.35    0    0     0    0     0  999  9.35    0    0     0  0   1.6  0.49 0.15
hparfuss       1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   0.7  0.24 0.15
20150901       1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   1.0  0.30 0.15
jengewald      1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   0.7  0.24 0.15
20150901       1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   1.0  0.30 0.15
jfriedrichs    1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   0.7  0.24 0.15
20150901       1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   1.0  0.30 0.15
tjungblut      1     5.5  0   0 TechnKK 1517  9.35  1.5  7.3 1.175  0.8  0.25  999  9.35  1.5  7.3 1.175  0   1.6  0.49 0.15
stschwarz      4.15  5.5  8r  0 TechnKK 1517  9.35  1.5  7.3 1.175  0.8     0  999  9.35  1.5  7.3 1.175  0   1.6  0.49 0.15
swonneberger   3.20  5.5  0   0 TechnKK 1517  9.35  1.5  7.3 1.175  0.8     0  999  9.35  1.5  7.3 1.175  0   1.6  0.49 0.15
vgabriel       1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   0.7  0.24 0.15
20150901       1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   1.0  0.30 0.15
rbetageri      1     5.5  0   0 TechnKK 1517  9.35  1.5  7.3 1.175  0.8  0.25  999  9.35  1.5  7.3 1.175  0   1.6  0.49 0.15
sjain          1     5.5  0   0 TechnKK 1517  9.35  1.5  7.3 1.175  0.8  0.25  999  9.35  1.5  7.3 1.175  0   1.6  0.49 0.15
----------------------------------------------------------------------------------------------------------------------------
'''

        if jahr == "2016":
        
            jw['RLIMIT']  = "6200"
            jw['KLIMIT']  = "4237.5"
            jw['RV'] = ["9.35","15"]  [ int( jw['NR'] == "1512" ) ] 
            jw['AV'] = ["1.5" ,"3.6"] [ int( jw['NR'] == "1512" ) ] 
            jw['KV'] = ["7.3","13"]  [ int( jw['NR'] == "1512" ) ] 
            jw['KG'] = ["0.3","0.0"] [ int( jw['NR'] == "1512" ) ] 
            jw['ZU'] = { "1512" : "0.0",  "1514": "1.1",  "1517": "1.0", "1519": "1.1", "1520": "1.1" }   [ jw['NR'] ]  
            jw['ZV'] = "1.1"
            jw['PV'] = "1.175"
            jw['PZ'] = "0.25"
            jw['U1'] = { "1512" : "1.0", "1514": "1.5",  "1517": "1.6",  "1519": "1.4",  "1520": "1.5" }  [ jw['NR'] ]  
            jw['U2'] = { "1512" : "0.3", "1514": "0.43", "1517": "0.49", "1519": "0.37", "1520": "0.43" } [ jw['NR'] ]  
            jw['U3'] = "0.12"

            '''

PERSON         LST   SZ  KS  PL KK     KNR    RVN   AVN  KVN   PVN  ZUN   KIN  ART  RVR   AVR  KVR   PVR ST    U1    U2   U3
----------------------------------------------------------------------------------------------------------------------------
ddienlin       1     5.5  0   0 Debeka  1519  9.35    0    0     0    0     0  999  9.35    0    0     0  0   1.4  0.37 0.12
rndengang      1     5.5  0   0 TechnKK 1517  9.35    0    0     0    0     0  999  9.35    0    0     0  0   1.6  0.49 0.12
agosmann       1     5.5  0   0 TechnKK 1517  9.35    0    0     0    0     0  999  9.35    0    0     0  0   1.6  0.49 0.12
suschuster     6     5.5  0   0 TechnKK 1517  9.35    0    0     0    0     0  999  9.35    0    0     0  0   1.6  0.49 0.12
20161001       1.20  5.5  0   0 TechnKK 1517  9.35  1.5  7.3 1.175  1.0     0  999  9.35  1.5  7.3 1.175  0   1.6  0.49 0.12
hparfuss       1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   1.0  0.30 0.12
kfessmann      1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   1.0  0.30 0.12
jengewald      1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   1.0  0.30 0.12
jfriedrichs    1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   1.0  0.30 0.12
tjungblut      1     5.5  0   0 TechnKK 1517  9.35  1.5  7.3 1.175  1.0  0.25  999  9.35  1.5  7.3 1.175  0   1.6  0.49 0.12
swonneberger   3.20  5.5  0   0 TechnKK 1517  9.35  1.5  7.3 1.175  1.0     0  999  9.35  1.5  7.3 1.175  0   1.6  0.49 0.12
vgabriel       1       0  0   0 Minijob 1512     0    0    0     0    0     0  991    15    0   13     0  2   1.0  0.30 0.12
rbetageri      1     5.5  0   0 TechnKK 1517  9.35  1.5  7.3 1.175  1.0  0.25  999  9.35  1.5  7.3 1.175  0   1.6  0.49 0.12
sjain          3     5.5  0   0 TechnKK 1517  9.35  1.5  7.3 1.175  1.0  0.25  999  9.35  1.5  7.3 1.175  0   1.6  0.49 0.12
sdjomo         1     5.5  0   0 AOK     1514  9.35  1.5  7.3 1.175  1.1  0.25  999  9.35  1.5  7.3 1.175  0   1.5  0.43 0.12
20161001       1     5.5  0   0 AOK     1514  9.35    0    0     0    0     0  999  9.35    0    0     0  0   1.5  0.43 0.12
----------------------------------------------------------------------------------------------------------------------------
'''

#  DAK freiwillige versicherung: 674,05 / 121,80

        if jahr == "2017":
        
            jw['RLIMIT']  = "6350"
            jw['KLIMIT']  = "4350"
            jw['RV'] = ["9.35","15"]  [ int( jw['NR'] == "1512" ) ] 
            jw['AV'] = ["1.5" ,"3.6"] [ int( jw['NR'] == "1512" ) ] 
            jw['KV'] = ["7.3","13"]  [ int( jw['NR'] == "1512" ) ] 
            jw['KG'] = ["0.3","0.0"] [ int( jw['NR'] == "1512" ) ] 
            jw['ZU'] = { "1510": "1.5", "1512" : "0.0",  "1517": "1.0",  "1519": "1.1", "1521": "1.1", "1522": "1.1"}  [ jw['NR'] ]  
            jw['ZV'] = "1.1"
            jw['PV'] = "1.275"
            jw['PZ'] = "0.25"
            jw['U1'] = { "1510": 2.0,  "1512" : "0.9", "1517": "1.9",  "1519": "1.4" , "1521": "1.7" , "1522": "1.5"}  [ jw['NR'] ]  
            jw['U2'] = { "1510": 0.38, "1512" : "0.3", "1517": "0.49", "1519": "0.37", "1521": "0.46", "1522": "0.44"} [ jw['NR'] ]  
            jw['U3'] = "0.09"


        if jahr == "2018":
        
            jw['RLIMIT']  = "6500"
            jw['KLIMIT']  = "4425"
            jw['RV'] = ["9.3","15"]  [ int( jw['NR'] == "1512" ) ] 
            jw['AV'] = ["1.5" ,"3.6"] [ int( jw['NR'] == "1512" ) ] 
            jw['KV'] = ["7.3","13"]  [ int( jw['NR'] == "1512" ) ] 
            jw['KG'] = ["0.3","0.0"] [ int( jw['NR'] == "1512" ) ] 
            jw['ZU'] = { "1510": "1.5", "1512" : "0.0",  "1517": "0.9", "1518": "1.1",
                         "1519": "1.0", "1521": "1.0", "1522": "1.0", "1523": "1.2" }  [ jw['NR'] ]  
            jw['ZV'] = "1.0"
            jw['PV'] = "1.275"
            jw['PZ'] = "0.25"
            jw['U1'] = { "1510" : "2.2",  "1512" : "0.9", "1517": "1.9",  "1518": "2.1",
                         "1519": "1.8" , "1521": "1.9" , "1522": "1.5",  "1523": "1.7"  }  [ jw['NR'] ]  
            jw['U2'] = { "1510" : "0.47", "1512" : "0.3", "1517": "0.49",  "1518":  "0.45",
                         "1519": "0.45", "1521": "0.49", "1522": "0.44", "1523": "0.45" } [ jw['NR'] ]  
            jw['U3'] = "0.06"  #  Insolvenzumlage


        if jahr == "2019":
        
            jw['RLIMIT']  = "6700"
            jw['KLIMIT']  = "4537.50"
            jw['RV'] = ["9.3","15"]   [ int( jw['NR'] == "1512" ) ] 
            jw['AV'] = ["1.25" ,"3.6"] [ int( jw['NR'] == "1512" ) ] 
            jw['KV'] = ["7.3","13"]  [ int( jw['NR'] == "1512" ) ] 
            jw['KG'] = ["0.3","0.0"] [ int( jw['NR'] == "1512" ) ] 
            jw['ZU'] = { "1510": "0.75", "1512" : "0.0",  "1514" : "0.55", "1517": "0.35",
                         "1518": "0.55", "1522": "0.45", "1523": "0.6", "1524": "0.5" }  [ jw['NR'] ]  #  1523: ab Mai 0.5
            jw['ZA'] = { "1510": "0.75", "1512" : "0.0",  "1514" : "0.55", "1517": "0.35",
                         "1518": "0.55", "1522": "0.45", "1523": "0.6", "1524": "0.5" }  [ jw['NR'] ]  #  1523: ab Mai 0.5
            jw['ZV'] = "1.0"  # der DURCHSCHNITTLICHE Wert der Krankenkassen-Arbeitnehmerzuschlaege
            jw['PV'] = "1.525"
            jw['PZ'] = "0.25"
            jw['U1'] = { "1510" : "2.4",  "1512" : "0.9", "1514": "1.1", "1517": "1.9",
                         "1518":  "2.2", "1522": "1.4",  "1523": "1.7", "1524" : "2.4"  }  [ jw['NR'] ]  
            jw['U2'] = { "1510" : "0.47", "1512" : "0.24", "1514": "0.46", "1517": "0.47",
                         "1518":  "0.43", "1522": "0.41", "1523": "0.39", "1524": "0.60" } [ jw['NR'] ]  
            jw['U3'] = "0.06"

#   Gleitzonenrechner:  krankenkassen-direkt.de/kassen/beitraege/midijobrechner.de
#                       www.aok.de/fk/tools/rechner/minijob-und-uebergangsbereichsrechner-2019
#                       tk-lex.tk.de/web/guest/rechner
#   Zusatzbeitrag:      krankenkassen.de/gesetzliche-krankenkassen/krankenkasse-beitrag/kein-zusatzbeitrag 


        if jahr == "2020":
        
            jw['RLIMIT']  = "6900"
            jw['KLIMIT']  = "4687.50"
            jw['RV'] = ["9.3","15"]   [ int( jw['NR'] == "1512" ) ] 
            jw['AV'] = ["1.2" ,"3.6"] [ int( jw['NR'] == "1512" ) ] 
            jw['KV'] = ["7.3","13"]  [ int( jw['NR'] == "1512" ) ] 
            jw['KG'] = ["0.3","0.0"] [ int( jw['NR'] == "1512" ) ] 
            jw['ZU'] = { "1510": "0.75", "1512" : "0.0",  "1514" : "0.55", "1517": "0.35",
                         "1518": "0.55", "1522": "0.45", "1523": "0.6", "1524": "0.5"  }  [ jw['NR'] ]  #  1523: ab Mai 0.5
            jw['ZA'] = { "1510": "0.75", "1512" : "0.0",  "1514" : "0.55", "1517": "0.35",
                         "1518": "0.55", "1522": "0.45", "1523": "0.6", "1524": "0.5"  }  [ jw['NR'] ]  #  1523: ab Mai 0.5
            jw['ZV'] = "1.1"  # der DURCHSCHNITTLICHE Wert der Krankenkassen-Arbeitnehmerzuschlaege
            jw['PV'] = "1.525"
            jw['PZ'] = "0.25"
            jw['U1'] = { "1510" : "2.4",  "1512" : "0.9", "1514": "1.1", "1517": "2.0",
                         "1518":  "2.2", "1522": "1.4",  "1523": "1.7", "1524": "2.3"   }  [ jw['NR'] ]  
            jw['U2'] = { "1510" : "0.47", "1512" : "0.19", "1514": "0.46", "1517": "0.47",
                         "1518":  "0.43", "1522": "0.41", "1523": "0.39", "1524": "0.7"  } [ jw['NR'] ]  
            jw['U3'] = "0.06"



        if jahr == "2021":       #   DAK  Arbeitgeberservice  0231/8642569450
        
            jw['RLIMIT']  = "7100"
            jw['KLIMIT']  = "4837.50"
            jw['RV'] = ["9.3","15"]   [ int( jw['NR'] == "1512" ) ] 
            jw['AV'] = ["1.2" ,"3.6"] [ int( jw['NR'] == "1512" ) ] 
            jw['KV'] = ["7.3","13"]  [ int( jw['NR'] == "1512" ) ] 
            jw['KG'] = ["0.3","0.0"] [ int( jw['NR'] == "1512" ) ] 
            jw['ZU'] = { "1510": "0.75", "1512" : "0.0",  "1514" : "0.55", "1515": "0.645", "1517": "0.60",
                         "1518": "0.75", "1522": "0.45", "1523": "0.6" }  [ jw['NR'] ]  #  1523: ab Mai 0.5
            jw['ZA'] = { "1510": "0.75", "1512" : "0.0",  "1514" : "0.55", "1515": "0.645", "1517": "0.60",
                         "1518": "0.75", "1522": "0.45", "1523": "0.6" }  [ jw['NR'] ]  #  1523: ab Mai 0.5
            jw['ZV'] = "1.0"  # der DURCHSCHNITTLICHE Wert der Krankenkassen-Arbeitnehmerzuschlaege
            jw['PV'] = "1.275"
            jw['PZ'] = "0.25"
            jw['U1'] = { "1510" : "2.4",  "1512" : "0.9", "1514": "1.1", "1515": "2.2", "1517": "2.2",
                         "1518":  "2.2",  "1522": "1.4",  "1523": "1.7"  }  [ jw['NR'] ]  
            jw['U2'] = { "1510" : "0.65", "1512" : "0.24", "1514": "0.46", "1515": "0.49", "1517": "0.55",
                         "1518":  "0.53", "1522": "0.41", "1523": "0.39" } [ jw['NR'] ]  
            jw['U3'] = "0.12"



        jw['ST'] =  "2.0"
        jw['PS'] = "25.0"
            

#*************************************************************************

    def parse_tabletext (self,table_text):
        
        columns = [-100,-99,99999991,99999992,99999993]
        
        fehlerzeile = None
        for zeile0 in table_text.split("\n"):

            zeile = zeile0
            if zeile and zeile[0] == "#":
                continue
            offset  = 0
            
            while (0 == 0):
                m = re.search(r"^( *)(\S+)(.*)$",zeile)
                if not m:
                    break
                a      = offset + len(m.group(1))
                offset = offset + len(m.group(1)) + len(m.group(2))
                b      = offset - 1
                zeile  = m.group(3)
                
                zaehler = 0
                while (0 == 0):
                    zaehler = zaehler + 2
#                    print(111,a,b,columns[zaehler-1],columns[zaehler+0],columns[zaehler+1],columns[zaehler+2])
                    if a <= columns[zaehler+1]:
                        if not columns[zaehler-1] < a:
                            fehlerzeile = zeile0
                        elif b < columns[zaehler]:
#                            print (222,a,b)
                            columns.insert(zaehler,a)
                            columns.insert(zaehler+1,b)
                        elif b < columns[zaehler+2]:
#                            print (333,a,b)
                            columns[zaehler]   = min(a,columns[zaehler])
                            columns[zaehler+1] = max(b,columns[zaehler+1])
                        else:
                            fehlerzeile = zeile0
                        break
                        
                if fehlerzeile:
                    print(fehlerzeile)
                    return(fehlerzeile)
                    
        columns     = columns[3:-3][::2]
        columns[-1] = columns[-1] + 1
        tablerows   = []
        tablecols   = []
        addspaces   = " " * columns[-1]
        
        for zeile0 in table_text.split("\n"):
            zeile = (zeile0 + addspaces)[0:len(addspaces)]
            tablerow = []
            zaehler  = 0
            offset   = 0
            a        = 0
            for b in columns:
                tablerow.append(zeile[a:b+1])
                a = b+1
            tablerows.append(tablerow)
        
        tablecols = []
        for col in tablerows[0]:
            tablecols.append([])

        zaehler = 0
        for tablecol in tablecols:
            for tablerow in tablerows:
                tablecol.append(tablerow[zaehler])
            zaehler = zaehler + 1

        return(tablerows,tablecols)            

#*************************************************************************
#*************************************************************************

    def xxsozvers (self,ktodata):

        self.sort_sozvers = 'LO,SO,LS,SZ,KR,KE,KA,KI,PL,KV,RV,AV,PV,U1,U2,U3,ZA'.split(',')
        ee = []
        text = []
        for zeile in ktodata['CONTENT'].split('\n'):
            m = re.search('^(\\d\\d\\d\\d)(\\d\\d)(\\d\\d) +\\-?(\\d+\\.\\d\\d) +(\\S.*?)([a-z]+)(\\-?\\S*) +\\S+ +(\\-?\\d+\\.\\d\\d) +(.*)', zeile)
            if not m:
                text.append(zeile)
                continue
            jahr = m.group(1)
            monat = int(m.group(2)) - 1
            datum = m.group(1) + m.group(2) + m.group(3)
            betrag = float(m.group(4))
            anr = m.group(5)
            person = m.group(6)
            art = re.sub('^-', '', m.group(7))
            remark = m.group(9)
            ee.append([jahr, monat, datum, betrag, anr, person, art, remark, zeile])

        ee.sort(key=lambda x: x[5] + x[0] + '%02u' % x[1] + x[2] + x[5] + '%1u' % (1 + int('LOHN' in x or 'SOND' in x)))
        ee.append(['', 0, '', '', '', '', '', '', ''])
        person0 = ''
        jahr0 = ''
        monat0 = -9
        buchungen = []
        lsk = {}
        for entry in ee:
            jahr, monat, datum, betrag, anr, person, art, remark, zeile = tuple(entry)
            if not (person0 == person and monat0 == monat):
                if not person0 == '':
                    if not has_values:
                        buchungen.extend(self.sozvers_make_buchungen(person0, jahr0, monat0, datum0, remark0, betrag0, betragk, betragr, lsk))
                person0 = person
                monat0 = monat
                datum0 = datum
                betrag0 = 0.0
                betragk = 0.0
                betragr = 0.0
                remark0 = ''
                has_values = False
                if not jahr0 == jahr:
                    jahr0 = jahr
                    lsk = [0.0, 0.0, 0.0, 0.0]
            if art == 'ZAHL':
                text.append(zeile)
            elif art in ('LOHN', 'LOHN-Q', 'LOHN-R', 'LOHN-Z', 'LOHNG', 'LOHNH', 'SOND',
                         'SOND-Q', 'SOND-R', 'SOND-Z'):
                text.append(zeile)
                remark0 = remark0 + '| ' + remark
                datum0 = datum
                m = re.search('^(.*)\\-([KRZ])', art)
                if not m:
                    betrag0 = betrag0 + betrag
                    betragk = betragk + betrag
                    betragr = betragr + betrag
                else:
                    if m.group(2) == 'Q':
                        betrag0 = betrag0 + betrag
                        betragk = betragk + betrag
                        betragr = betragr + betrag
                    if m.group(2) == 'R':
                        betrag0 = betrag0 + betrag
                        betragr = betragr + betrag
                    if m.group(2) == 'Z':
                        betrag0 = betrag0 + betrag
            elif jahr not in ('2018', '2017', '2016'):
                text.append(zeile)
                has_values = True
                continue

        for buchung in buchungen:
            o = '  '.join(buchung)
            if 'KV-Z' in o:
                o = re.sub('KV-AN-', 'KV-ZU-', o)
            if 'PV-Y' in o:
                o = re.sub('PV-AN-', 'PV-KI-', o)
            text.append(o)

        ktodata['CONTENT'] = '\n'.join(text) + '\n'
        ktodata['CONTENT'] = re.sub('AR-Anteil', 'Arbeitgeber-Anteil', ktodata['CONTENT'], 99999999)
        ktodata['CONTENT'] = re.sub('AN-Anteil', 'Arbeitnehmer-Anteil', ktodata['CONTENT'], 99999999)
        ktodata['CONTENT'] = re.sub('korrigierte Soli', 'korrigierter Soli', ktodata['CONTENT'], 99999999)

#******************************************************************* 

    def xxsozvers_make_buchungen(self, person0, jahr0, monat0, datum0, remark0, betrag0, betragk, betragr, lsk):

        buchungen = []
        kinderlos = 0
        rvbefreit = 0
        red_betr = None
        sozvers_faktoren = []
        m = re.search('Gleitzone(\\d*)', remark0)
        if m:
            d = jahr0[0:-len(m.group(1))] + m.group(1)
            if int(d) < 2013:
                gl0 = self.gleitzone['12A']
                gl1 = self.gleitzone['12B']
            else:
                gl0 = self.gleitzone['15A']
                gl1 = self.gleitzone['15B']
            if gl0 < betrag < gl1:
                red_betrag = self.gleitzone[int(jahr0)] * 450 + (gl1 / (gl1 - gl0) - gl0 / (gl1 - gl0) * self.gleitzone[int(jahr0)]) * (betrag - 450)
                ag_anteil = {'RV': 0.0, 'AV': 0.0, 'KV': 0.0, 'PV': 0.0}
                gesamt = {'RV': 0.0, 'AV': 0.0, 'KV': 0.0, 'PV': 0.0}
        kv_zuschlag_fuer_lst_berechnung = 0.0
        m = re.search('([A-Za-z]+) *, +SV-AN\\: +([\\d\\.]+)\\/([\\d\\.]+)\\/([\\d\\.]+)\\/([\\d\\.]+)', remark0)
        if m:
#            kknr, kk = self.fibu.rules.kknr(' ' + remark0 + ' ')
            kknr, kk = self.kknr(' ' + remark0 + ' ')
            sozvers_faktoren = [[m.group(2), 'RV', ''], [m.group(3), 'AV', ''], [m.group(4), 'KV', '-S'], [m.group(5), 'PV', '-S']]
            m = re.search('Zuschl\\: +([\\d\\.]+)\\/([\\d\\.]+)', remark0)
            if m:
                sozvers_faktoren = sozvers_faktoren + [[m.group(1), 'KV', '-Z'], [m.group(2), 'PV', '-Y']]
                kv_zuschlag_fuer_lst_berechnung = float(m.group(1)) + float(m.group(2))
            sozvers_faktoren.append(None)
            m = re.search(' SV-AR\\: +([\\d\\.]+)\\/([\\d\\.]+)\\/([\\d\\.]+)\\/([\\d\\.]+)', remark0)
            if m:
                sozvers_faktoren = sozvers_faktoren + [[m.group(1), 'RV', ''], [m.group(2), 'AV', ''], [m.group(3), 'KV', ''], [m.group(4), 'PV', '']]
            m = re.search(' Uml\\: +([\\d\\.]+)\\/([\\d\\.]+)\\/([\\d\\.]+)', remark0)
            if m:
                sozvers_faktoren = sozvers_faktoren + [[m.group(1), 'U1', ''], [m.group(2), 'U2', ''], [m.group(3), 'U3', '']]
            ANR = 'AR'
            sozvers_faktoren.reverse()
        m = re.search('Pausch[sS]t +(\\d+).*kurzfri', remark0)
        if m:
            buchungen.append([datum0, '%3.2f' % (float(m.group(1)) * 0.01 * betrag0),
             '11-1500-AR-' + person0, '11-1503-PL-' + person0, '0.00', 'Pauschalsteuer'])
        else:
            m = re.search('Pausch[sS]t +(\\d+)', remark0)
            if m:
                buchungen.append([datum0, '%3.2f' % (float(m.group(1)) * 0.01 * betrag0),
                 '11-1500-AR-' + person0 + '-ST', '11-' + kknr + '-ST-AR-' + person0, '0.00', 'Pauschalsteuer Minijob'])
            for o in sozvers_faktoren:
                if o == None:
                    ANR = 'AN'
                elif float(o[0]) > 0.0001:
                    if o[1] in ('RV', 'AV', 'U1', 'U2'):
                        beitrag = float(o[0]) * 0.01 * betragr
                    elif o[1] in ('KV', 'PV'):
                        beitrag = float(o[0]) * 0.01 * betragk
                    else:
                        beitrag = float(o[0]) * 0.01 * betrag0
                    if red_betr:
                        if o[1] in ('RV', 'AV', 'KV', 'PV'):
                            gesamt[o[1]] = gesamt[o[1]] + float(o[0]) * 0.01 * red_betr
                            if ANR == 'AR':
                                ar_anteil[o[1]] = beitrag
                            if ANR == 'AN' and o[2] in ('', '-S'):
                                beitrag = gesamt[o[1]] - ag_anteil[o[1]]
                    if abs(beitrag) > 0.001:
                        buchungen.append([datum0, '%3.2f' % beitrag, '11-1500-' + ANR + '-' + person0 + '-' + o[1] + o[2],
                         '11-' + kknr + '-' + o[1] + '-' + ANR + '-' + person0, '0.00', ANR + '-Anteil ' + o[1] + ', ' + kk])
                    if o[1] == 'RV':
                        rvbefreit = rvbefreit + 1
                    if o[1] + o[2] == 'PV-Y':
                        kinderlos = 1

            lsk[0] = lsk[0] + betrag0
            m = re.search('StKl.*?(\\d)\\/([\\d\\.]+)\\/([\\d\\.]+)([reia]?).*([\\d\\.]+) +Kind', remark0)
            if m:
                if not datum0[7] == '7':
                    betrag1 = betrag0
                    intmode = 2
                else:
                    betrag1 = lsk[0]
                    intmode = 1
                stkl = m.group(1)
                soli = m.group(2)
                kirchensteuersatz = float(m.group(3)) * 0.01
                religion = m.group(4)
                kinder = m.group(5)
#                exec('import pap.lst' + jahr0)
                stobj = eval('lohnsteuer.lst' + jahr0 + '.Lst' + jahr0 + '()')
                stobj.setKrv(0)
                stobj.setKvz(kv_zuschlag_fuer_lst_berechnung)
                stobj.setLzz(int(intmode))
                if kirchensteuersatz > 0:
                    stobj.setR(1)
                else:
                    stobj.setR(0)
                stobj.setRe4(int(betrag1 * 100))
                stobj.setStkl(int(stkl))
                stobj.setZkf(float(kinder))
                stobj.MAIN()
                ls = 0.01 * float(stobj.getLstlzz())
                sz = 0.01 * float(stobj.getSolzlzz())
                ks = 0.01 * (float(stobj.getBk()) + float(stobj.getBks()) + float(stobj.getBkv())) * kirchensteuersatz
                korrektur = ''
                if intmode == 1:
                    ls = ls - lsk[1]
                    sz = sz - lsk[2]
                    ks = ks - lsk[3]
                    korrektur = 'Jahreskorrigierte '
                else:
                    lsk[1] = lsk[1] + ls
                    lsk[2] = lsk[2] + sz
                    lsk[3] = lsk[3] + ks
                buchungen.append([datum0, '%3.2f' % ls, '11-1500-AN-' + person0 + '-LS', '11-1503-LS-' + person0,
                 '0.00', korrektur + ' Lohnsteuer'])
                buchungen.append([datum0, '%3.2f' % sz, '11-1500-AN-' + person0 + '-SZ', '11-1503-SZ-' + person0,
                 '0.00', korrektur + 'Solidaritaetszuschlag'])
                o = '-K' + religion.upper()
                if not o == '-K':
                    buchungen.append([datum0, '%3.2f' % ks, '11-1500-AN-' + person0 + o, '11-1503' + o + '-' + person0,
                     '0.00', korrektur + 'Lohnsteuer'])

        return (buchungen)

#*************************************************************************

    def xxsozvers_sortidx(self, pattern):

        if pattern[2:4] in self.sort_sozvers:
            return pattern[0:2] + '%02u' % self.sort_sozvers.index(pattern[2:4])
        else:
            return pattern[0:2] + '99'

#*************************************************************************

    def xxread_lstb (self,jahr):
    
        text = ""
        for file in self.ktolstb:
            m = re.search(r"(\d\d\d\d)",file)
            if m:
                if jahr == m.group(1):
                    text = open(file).read()
                    break

        if text == "":
            return(None)
        
        erg = {}
        for abgabe in self.abgabenarten + ['LOHN']:
            erg[abgabe] = 0.00
            m = re.search(abgabe+".*?(\d+)[,\.](\d\d)",text)
            if m:
                erg[abgabe] = float(m.group(1)+"."+m.group(2))

        return(erg)

#*************************************************************************


if __name__ == "__main__":

    ktofile = glob.glob( "*.kto"  )[0]
    ktoslip = glob.glob( "gehaltsbescheinigung*.md" )
    ktolstb = glob.glob( "LStB*.md" )

    print(ktofile,ktoslip,ktolstb)


    lohn    = Lohn("13-D5a-6010","13-D5b-6110","10-B12-3695-kug")
    erg     = lohn.parse_lohndaten(open(ktofile).read(),ktoslip,ktolstb)

    open(ktofile,"w").write(erg)  # +"\n"+str(random.randint(1,10000))) 
    open("vormonate","w").write(lohn.diff)
    if lohn.diff == "":
        os.remove("vormonate")

    if len(sys.argv) > 1:
        for jm in sys.argv[1].split(","):
            if (len(jm) < 6):
                jm = "20" + jm
            if jm in lohn.lstfile and lohn.lstfile[jm]:
                open(lohn.lstfile[jm],"w").write(lohn.lsttext[jm])
    