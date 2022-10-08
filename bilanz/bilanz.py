#!/usr/bin/python3
#  coding:  utf8

import os,sys,re,glob,time

from konto.base.konto import Konto

#*********************************************************************************

class Bilanz (object):

    def __init__ (self):
    
        self.FORMAT1 = "%8.0f"
        self.FORMAT2 =  8
        self.FORMAT3 = "%8s"

        self.ktotyp =  ["^[^-]+","xxB12-3695","C13-3751","C13-3759","C13-3740","B12-1361","B12-1369","B11-1374",
                        "C11-3170","C12-3310","B12-1435","B23-1437","B12-1340","B12-3695","B12-3696","D1a-4401","D1a-4101",
                        "Do.-6011","Do.-6111","Do.-6816","Do.-6817","Do.-6818","D7f-6612",
                        "Bo.-ver","Bo.-kto","Bo.-umlagen","Bo.-1700",
                        "D..-4100","D..-4105","D..-4106","D..-4400"]
        
        kto          = Konto()
        self.dataset = kto.read_config()

#*********************************************************************************

    def mark (self,remark=""):

        t = time.perf_counter()
        if 't0' in vars(self):
            print ( ("%9.2f" % ((t-self.t0)*1000)) + " ms for:  " + remark )
        self.t0 = t

#*********************************************************************************

    def base_bilanz (self,*pars):     # open the csv and kto files and prepare for processing

        jahr = pars[0]
        try:
            name = self.dataset["name"]
        except:
            name = "buchhaltung"
            
        try:
            bez  = self.dataset["bez"]
        except:
            bez  = "___NAME___"

        WITH_BWA = 0
        if int(jahr) < 0:
            WITH_BWA = 1
            jahr = "%02u" % (-int(jahr))

        try:
            jahr1 = sys.argv[2]
        except:
            jahr1 = jahr
            
        while (0 == 0):

            self.base_bilanz1(name,bez,jahr,WITH_BWA) 

#            os.system("a2ps -B -1 -l 80 -o bilanz_" + jahr + "_" + bez + "_hauptteil.ps " + jahr + "_*md")
            os.system("a2ps -B -1 -l 172 -r -o bilanz_" + jahr + "_" + bez + "_hauptteil.ps " + jahr + "_*md")
            os.system("ps2pdf bilanz_" + jahr + "_" + bez + "_hauptteil.ps")
#            os.system("a2ps -B -1 -l 150 -r -o bilanz_" + jahr + "_" + bez + "_zusaetze.ps anlagen*" + jahr + ".md")
            os.system("a2ps -B -1 -l 172 -r -o bilanz_" + jahr + "_" + bez + "_zusaetze.ps anlagen*" + jahr + ".md")
            os.system("ps2pdf bilanz_" + jahr + "_" + bez + "_zusaetze.ps")
            for file in glob.glob("*.ps") + glob.glob("*.ps~") + glob.glob("*.kto"):
                os.unlink(file);

            if jahr == jahr1:
                break
            jahr = "%02u" % (int(jahr)+1)

#*****************************************************************************************************

    def base_bilanz1 (self,name,bez,jahr,WITH_BWA): 

        kto  = Konto(self.ktotyp)

        text = "BILANZ " + name + ", Jahr 20" + jahr
        kto.read_saldo("10-:"+jahr)
        text = text + "\nXXAKTIVA   " + kto.salden_text()

        kto.read_saldo("11-:"+jahr)
        text1 = "\nXXPASSIVA  " + kto.salden_text()
#        text1 = "\nXXPASSIVA  " + os.popen("grep -P '^(\S+|     ) +(\S+) *$' *kto").read()
        text1 = re.sub(r" (\-?\d+\.\d\d)","-\\1",text1,999999)  #  Minuszeichen
        text1 = re.sub(r" --","   ",text1,999999)
        text  = text + text1

        kto.read_saldo("12-."+jahr)
#        text1 = "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\f\nXXERTRAG " + os.popen("grep -P '^(\S+|     ) +(\S+) *$' *kto").read()
        text1 = "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\f\nXXERTRAG " + kto.salden_text()
        text1 = re.sub(r" (\-?\d+\.\d\d)","-\\1",text1,999999)  #  Minuszeichen
        text1 = re.sub(r" --","   ",text1,999999)
        text  = text + text1

        kto.read_saldo("13-."+jahr)
#        text  = text + "\nXXAUFWAND" + re.sub(r"Do","Xo",os.popen("grep -P '^(\S+|     ) +(\S+) *$' *kto").read(),99999999)
        text  = text + "\nXXAUFWAND" + re.sub(r"Do","Xo",kto.salden_text(),99999999)

#        print(text)
#        exit()


        monat_guv = []

        for monat in "123456789ABC"*WITH_BWA:
            kto.read_saldo("10-:"+jahr+monat)
            o1 = "\nAKTIVA   " + kto.salden_text()
#            o1 = "\nAKTIVA   " + os.popen("grep -P '^(\S+|     ) +(\S+) *$' *kto").read()
#            o1 = open(glob.glob("*kto")[0]).read()
            
            kto.read_saldo("11-:"+jahr+monat)
            o2 = "\nPASSIVA   " + kto.salden_text()
#            o2 = "\nPASSIVA   " + os.popen("grep -P '^(\S+|     ) +(\S+) *$' *kto").read()
#            o2 = open(glob.glob("*kto")[0]).read()
            o2 = re.sub(r" (\-?\d+\.\d\d)","-\\1",o2,999999)  #  Minuszeichen
            o2 = re.sub(r" --","   ",o2,999999)
            
            kto.read_saldo("12-."+jahr+monat)
            o3 = "\nERTRAG   " + kto.salden_text()
#            o3 = "\nERTRAG   " + os.popen("grep -P '^(\S+|     ) +(\S+) *$' *kto").read()
#            o3 = open(glob.glob("*kto")[0]).read()
            o3 = re.sub(r" (\-?\d+\.\d\d)","-\\1",o3,999999)  #  Minuszeichen
            o3 = re.sub(r" --","   ",o3,999999)
            
            kto.read_saldo("13-."+jahr+monat)
            o4 = "\nAUFWAND   " + kto.salden_text()
#            o4 = "\nAUFWAND   " + os.popen("grep -P '^(\S+|     ) +(\S+) *$' *kto").read()
            o4 = re.sub(r"Do","Xo",o4,999999)
            monat_guv.append( o1 + o2 + o3 + o4 ) # open(glob.glob("*kto")[0]).read() )

        text = re.sub(r"( .\d+\.\d\d)","                        \\1",text,99999999)
        text = re.sub(r"\nXX([A-Z]+)        ([^\n]+)","\n\n\n\\1\\2\n=======",text,9999)

        kto.read_saldo("14-."+jahr)
#        text  = text + "\n\n\f\nABSCHLUSS" + os.popen("grep -P '^(\S+|     ) +(\S+) *$' *kto").read()
        text  = text + "\n\n\f\nABSCHLUSS" + kto.salden_text()

        text = re.sub(r"( .\d+\.\d\d)","                        \\1",text,99999999)
        text = re.sub(r"\nXX([A-Z]+)        ([^\n]+)","\n\n\n\\1\\2\n=======\n",text,9999)

        Konto(self.ktotyp).kto("^12-."+jahr)
        einnahmen = open(glob.glob("*kto")[0]).read()

        Konto(self.ktotyp).kto("^13-."+jahr)
        ausgaben = open(glob.glob("*kto")[0]).read()

        Konto(self.ktotyp).kto("^10-A11-."+jahr)
        anlagen = open(glob.glob("*kto")[0]).read()

        Konto(self.ktotyp).kto("^11-C13-3060-."+jahr)
        ust = open(glob.glob("*kto")[0]).read()

#        print(text)
#        exit()

        text = re.sub(r"\n([^\-]{3}  +\-?\d+\.\d\d) *","\n\n\\1\n",text,99999999)

        text1 = ""
        for zeile in text.split("\n"):
            m   = re.search(r"^([ABC]\S\S|AXKTIVA|PXASSIVA|ERTRAG|AUFWAND|[DX][o\d]\S)(|\-\S+) (.*?)(\-?\d+\.\d\d) *$",zeile)
            if m:
                kto = m.group(1) + m.group(2)
                zeile = zeile + "                                                     "
                zeile = zeile[0:95]
                for monat in monat_guv:
                    m = re.search("\n"+kto + " +(.*?)(\-?\d+\.\d\d)",monat)
                    betrag = 0
                    if m:
                        betrag = round(float(m.group(2)))
                    betrag = self.FORMAT1 % betrag
                    zeile  = zeile + betrag
            text1 = text1 + zeile + "\n"

        text = re.sub(r"Xo","Do",text1,99999999)

#        print(text)

        text = re.sub(r"A11                                           ","\nANLAGEVERMOEGEN\n\n"+
                                                                        "A11: Sachanlagen - Betriebsausstattung        ",text,1)


        text = re.sub(r"A11-0300","XXX-0300",text,9999) 
        text = re.sub(r"A11-0675","XXX-0675",text,9999) 

        text = re.sub(r"A11-03","      Restwerte Wohnbauten:\n" +
                                "      ---------------------\n\nA11-03",text,1)
        text = re.sub(r"A11-06","\n      Restwerte Anlagen und Einrichtungen in Wohnbauten:\n" +
                                  "      --------------------------------------------------\n\nA11-06",text,1)

        text = re.sub(r"XXX-0300","A11-0300",text,9999) 
        text = re.sub(r"XXX-0675","A11-0675",text,9999) 

        if "Restwerte" in text:
            text = re.sub(r"A11-0675","\nA11-0675",text) 

        text = re.sub(r"A11-0144                                      ","  0144   Erstellte Softwareprodukte           ",text)
        text = re.sub(r"A11-0300                                      ","  0300   Wohnbauten                           ",text)
        text = re.sub(r"A11-0310                                        ","  0310   Immob. Schw.Gmuend, Lorcher Str.98, EGH",text)
        text = re.sub(r"A11-0311                                      ","  0311   Immob. Rheydt, Gertraudenstr. 73, ETW",text)
        text = re.sub(r"A11-0312                                      ","  0312   Immob. Stolberg, Niedergasse 27, MFH ",text)
        text = re.sub(r"A11-0316                                      ","  0316   Immob. Rheydt, Limitenstr. 27, ETW   ",text)
        text = re.sub(r"A11-0500                                      ","  0500   Betriebs- und Geschaeftsausstattung  ",text)
        text = re.sub(r"A11-0520                                      ","  0520   PKW                                  ",text)
        text = re.sub(r"A11-0560                                      ","  0560   Sonstige Transportmittel             ",text)
        text = re.sub(r"A11-0670                                      ","  0670   Geringwertige Wirtschaftsgueter      ",text)
        text = re.sub(r"A11-0675                                      ","  0675   Wirtschaftsgueter Sammelposten       ",text)
        text = re.sub(r"A11-0610                                        ","  0610   Anlag. Schw.Gmuend, Lorcher Str.98, EGH",text)
        text = re.sub(r"A11-0611                                      ","  0611   Anlag. Rheydt, Gertraudenstr. 73, ETW",text)
        text = re.sub(r"A11-0612                                      ","  0611   Anlag. Stolberg, Niedergasse 27, MFH ",text)
        text = re.sub(r"A11-0616                                      ","  0611   Anlag. Rheydt, Limitenstr. 27, ETW   ",text)


        text = re.sub(r"A12                                           ","\n"+
                                                                        "A12: Grundstueckswerte                        ",text,1)

        text = re.sub(r"A12-0210                                        ","  0210   Bodenw.Schw.Gmuend, Lorcher Str.98, EGH",text)
        text = re.sub(r"A12-0211                                      ","  0211   Bodenw Rheydt, Gertraudenstr. 73, ETW",text)
        text = re.sub(r"A12-0212                                      ","  0212   Bodenw.Stolberg, Niedergasse 27, MFH ",text)
        text = re.sub(r"A12-0216                                      ","  0216   Bodenw.Rheydt, Limitenstr. 27, ETW   ",text)


        text = re.sub(r"B11                                           ","\nUMLAUFVERMOEGEN\n\n"+
                                                                        "B11: Forderungen                              ",text,1)
        text = re.sub(r"B11-1210                                      ","  1210   Forderungen aus Lieferg.u.Leistungen ",text)
        text = re.sub(r"B11-1374                                      ","  1374   Mandanten Parkplaetze                ",text)
        text = re.sub(r"B11-1374-(\S+)                                ","     davon \\1:          ",text,999)


        text = re.sub(r"B12                                           ","\n"+
                                                                        "B12: sonstige Vermoegensgegenstaende          ",text,1)
        text = re.sub(r"B12-1310                                      ","  1310   Forderungen gg.GmbH-Gesellsch >1Jahr ",text)
        text = re.sub(r"B12-1340                                      ","  1340   Forderg.gg. Personal Lohn Gehalt     ",text)
        text = re.sub(r"B12-1340-(\S+)                                ","     davon \\1:          ",text,999)
        text = re.sub(r" +davon.*?\: +\-?\d\.\d\d *\n","",text,9999)
        text = re.sub(r"B12-1361                                      ","  1361   Forderg.aus SozVersich.ueberzahlungen",text)
        text = re.sub(r"B12-1361-1510                                 ","     davon DAK:          ",text)
        text = re.sub(r"B12-1361-1511                                 ","     davon AOK Hessen:   ",text)
        text = re.sub(r"B12-1361-1512                                 ","     davon Minijob:      ",text)
        text = re.sub(r"B12-1361-1513                                 ","     davon VBU:          ",text)
        text = re.sub(r"B12-1361-1514                                 ","     davon AOK Bayern:   ",text)
        text = re.sub(r"B12-1361-1515                                 ","     davon Mobiloil:     ",text)
        text = re.sub(r"B12-1361-1516                                 ","     davon Siemens BK:   ",text)
        text = re.sub(r"B12-1361-1517                                 ","     davon TechnikerKK:  ",text)
        text = re.sub(r"B12-1361-1518                                 ","     davon Barmer:       ",text)
        text = re.sub(r"B12-1361-1519                                 ","     davon Debeka:       ",text)
        text = re.sub(r"B12-1361-1520                                 ","     davon AOK Rhl.Pf.:  ",text)
        text = re.sub(r"B12-1361-1521                                 ","     davon AOK NordWest: ",text)
        text = re.sub(r"B12-1361-1522                                 ","     davon AOK Baden-W.: ",text)
        text = re.sub(r"B12-1361-1523                                 ","     davon IKK classic:  ",text)
        text = re.sub(r"B12-1361-1524                                 ","     davon Hanseatische: ",text)
        text = re.sub(r"B12-1369                                      ","  1369   Forderg.aus Erstatt.im Krankheitsfall",text)
        text = re.sub(r"B12-1369-1510                                 ","     davon DAK:          ",text)
        text = re.sub(r"B12-1369-1511                                 ","     davon AOK Hessen:   ",text)
        text = re.sub(r"B12-1369-1512                                 ","     davon Minijob:      ",text)
        text = re.sub(r"B12-1369-1513                                 ","     davon VBU:          ",text)
        text = re.sub(r"B12-1369-1514                                 ","     davon AOK Bayern:   ",text)
        text = re.sub(r"B12-1369-1515                                 ","     davon Mobiloil:     ",text)
        text = re.sub(r"B12-1369-1516                                 ","     davon Siemens BK:   ",text)
        text = re.sub(r"B12-1369-1517                                 ","     davon TechnikerKK:  ",text)
        text = re.sub(r"B12-1369-1518                                 ","     davon Barmer:       ",text)
        text = re.sub(r"B12-1369-1519                                 ","     davon Debeka:       ",text)
        text = re.sub(r"B12-1369-1520                                 ","     davon AOK Rhl.Pf.:  ",text)
        text = re.sub(r"B12-1369-1521                                 ","     davon AOK NordWest: ",text)
        text = re.sub(r"B12-1369-1522                                 ","     davon AOK Baden-W.: ",text)
        text = re.sub(r"B12-1369-1523                                 ","     davon IKK classic:  ",text)
        text = re.sub(r"B12-1369-1524                                 ","     davon Hanseatische: ",text)
        text = re.sub(r" +davon.*?\: +\-?0.\d\d *\n","",text,9999)
        text = re.sub(r"B12-1355                                      ","  1355   Mietkautionen                        ",text)
        text = re.sub(r"B12-1435                                      ","  1435   Forderungen aus Steuerueberzahlungen ",text)
        text = re.sub(r"B12-1435-1506                                        ","     davon Gewerbesteuer Fuerth:",text)
        text = re.sub(r"B12-1435-1507                                        ","     davon Forschungszulage:    ",text)
        text = re.sub(r"B12-1435-1508                                             ","     davon Umsatzsteuer Organschaft:",text)
        text = re.sub(r"B12-1435-1509                                        ","     davon Finanzamt Fuerth:    ",text)
        text = re.sub(r"B12-3695                                      ","  3695   Forderg. gg. Mitarbeitern, Auslagen  ",text)
        text2 = text
        text = re.sub(r"B12-3695-(\S+)                                ","     davon \\1:          ",text,999)
        text = re.sub(r" +davon.*?\: +\-?\d\.\d\d *\n","",text,9999)
        text = re.sub(r"B12-3696                                      ","  3696   Offene Vertragsstrafen               ",text)
        text = re.sub(r"B12-3696-([\S\-]+)                            ","     davon \\1:          ",text,999)
        text = re.sub(r"B12-1457                                      ","  1457   Forderung AAG KUG                    ",text)


        text = re.sub(r"B22                                           ","\n"+
                                                                        "B22: Bankkonten                               ",text,1)
        text = re.sub(r"B22-1435                                      ","  1435   Steuerkonten                         ",text)
        text = re.sub(r"B22-1435-1506                                        ","     davon Gewerbesteuer Fuerth:",text)
        text = re.sub(r"B22-1435-1508                                             ","     davon Umsatzsteuer Organschaft:",text)
        text = re.sub(r"B22-1435-1509                                        ","     davon Finanzamt Fuerth:    ",text)
        text = re.sub(r"B22-1600                                      ","  1600   Kassenbestand                        ",text)
        text = re.sub(r"B22-1615                                      ","  1615   Privatkredit Gesellschafter          ",text)
        text = re.sub(r"B22-1800                                      ","  1800   Commerzbank                          ",text)
        text = re.sub(r"B22-1802                                      ","  1802   Sparkasse Fuerth                     ",text)
        text = re.sub(r"B22-1803                                      ","  1803   Consors Bank                         ",text)
        text = re.sub(r"B22-1804                                      ","  1804   Flessabank Fuerth                    ",text)
        text = re.sub(r"B22-1805                                      ","  1805   VRBank Ostalb Immo Konto             ",text)
        text = re.sub(r"B22-1806                                      ","  1806   VRBank Ostalb IfT Konto              ",text)
        text = re.sub(r"B22-1807                                      ","  1807   VRBank Ostalb Firmenkreditkarte IfT  ",text)
        text = re.sub(r"B22-1811                                      ","  1811   Forecast Konto fuer Planung          ",text)
        text = re.sub(r"B22-1819                                      ","  1812   Bausparvertrag VRBank                ",text)
        text = re.sub(r"B22-1821                                      ","  1821   Konto Stolberg                       ",text)
        text = re.sub(r"B22-1840                                      ","  1840   Geschaeftsanteile VRBank             ",text)
        text = re.sub(r"B22-1851                                      ","  1851   Kapitalkonto Sparkasse Fuerth        ",text)
        text = re.sub(r"B22-1885                                      ","  1885   Transferkonto Bankueberweisungen     ",text)
        text = re.sub(r"B22-1890                                      ","  1890   Bestand gegen andere Geschaeftsfelder",text)
        text = re.sub(r"B22-1891                                      ","  1891   Transferkonto Finanzamt              ",text)

        text = re.sub(r"B23                                           ","\n"+
                                                                        "B23: Verfügbare Eigenmittel, Tagesgeld        ",text,1)
        text = re.sub(r"B23-1437                                      ","  1437   Steuerkonten                         ",text)
        text = re.sub(r"B23-1437-1506                                        ","     davon Gewerbesteuer Fuerth:",text)
        text = re.sub(r"B23-1437-1508                                             ","     davon Umsatzsteuer Organschaft:",text)
        text = re.sub(r"B23-1437-1509                                        ","     davon Finanzamt Fuerth:    ",text)
        text = re.sub(r"B23-1600                                      ","  1600   Kassenbestand                        ",text)
        text = re.sub(r"B23-1615                                      ","  1615   Privatkredit Gesellschafter          ",text)
        text = re.sub(r"B23-1800                                      ","  1800   Commerzbank                          ",text)
        text = re.sub(r"B23-1802                                      ","  1802   Sparkasse Fuerth                     ",text)
        text = re.sub(r"B23-1803                                      ","  1803   Consors Bank                         ",text)
        text = re.sub(r"B23-1804                                      ","  1804   Flessabank Fuerth                    ",text)
        text = re.sub(r"B23-1805                                      ","  1805   VRBank Ostalb Immo Konto             ",text)
        text = re.sub(r"B23-1806                                      ","  1806   VRBank Ostalb IfT Konto              ",text)
        text = re.sub(r"B23-1807                                      ","  1807   VRBank Ostalb Firmenkreditkarte IfT  ",text)
        text = re.sub(r"B23-1811                                      ","  1811   Forecast Konto fuer Planung          ",text)
        text = re.sub(r"B23-1819                                      ","  1812   Bausparvertrag VRBank                ",text)
        text = re.sub(r"B23-1821                                      ","  1821   Konto Stolberg                       ",text)
        text = re.sub(r"B23-1840                                      ","  1840   Geschaeftsanteile VRBank             ",text)
        text = re.sub(r"B23-1851                                      ","  1851   Kapitalkonto Sparkasse Fuerth        ",text)
        text = re.sub(r"B23-1885                                      ","  1885   Transferkonto Bankueberweisungen     ",text)
        text = re.sub(r"B23-1890                                      ","  1890   Bestand gegen andere Geschaeftsfelder",text)
        text = re.sub(r"B23-1891                                      ","  1891   Transferkonto Finanzamt              ",text)

        if "C11-2978" in text:
            text = re.sub(r"C11                                           ","\nVERLUSTVORTRAG\n\n"+
                                                                            "C11: Verlustvortrag                           ",text,1)
            text = re.sub(r"C11-2978                                      ","  2978   Verlustvortrag                       ",text)

        text = re.sub(r"C01                                           ","\nSTAMMKAPITAL\n\n"+
                                                                        "C01: Stammkapital                             ",text,1)
        text = re.sub(r"C01-2900                                      ","  2900   Stammeinlage                         ",text)


        text = re.sub(r"C02                                           ","\nEIGENKAPITAL\n\n"+
                                                                        "C02: Gewinnvortrag                            ",text,1)
        text = re.sub(r"C02-2970                                      ","  2970   Gewinnvortrag vor Verwendung         ",text)


        text = re.sub(r"C11                                           ","\nDARLEHEN\n\n"+
                                                                        "C11: Darlehen                                  ",text,1)
        text = re.sub(r"C11-3170                                      ","  3170           Darlehen Gesamt               ",text)
        text = re.sub(r"C11-3170-kreditgertrauden                           ","     davon Baudarlehen Gertraudenstr:  ",text)
        text = re.sub(r"C11-3170-kreditlimitenstr                           ","     davon Baudarlehen Limitenstr:     ",text)
        text = re.sub(r"C11-3170-kreditlorcherstr                           ","     davon Baudarlehen SchwGDLorcherS: ",text)
        text = re.sub(r"C11-3170-kreditstolberg                             ","     davon Baudarlehen Stolberg:       ",text)
        text = re.sub(r"C11-3170-kreditingdiba                              ","     davon Darlehen Ing-Diba:          ",text)
        text = re.sub(r"C11-3170-kreditnetbank                              ","     davon Darlehen Netbank:           ",text)
        text = re.sub(r"C11-3170-kreditvrsmart                              ","     davon Darlehen VR Smart:          ",text)
        text = re.sub(r"C11-3170-[a-z]+ +\-?0.00 *\n","",text,9999)


        text = re.sub(r"C12                                           ","\nKREDITE\n\n"+
                                                                        "C12: Kredite                                  ",text,1)
        text = re.sub(r"C12-3310                                      ","  3310           Kredite Gesamt               ",text)
        text = re.sub(r"C12-3310-reality                              ","     davon Kredit reality:   ",text)
        text = re.sub(r"C12-3310-schlotz                              ","     davon Kredit Dieter Schlotz:   ",text)
        text = re.sub(r"C12-3310-kreditvrsmart                        ","     davon Kredit VRSmart:          ",text)
        text = re.sub(r"C12-3310-kreditsigma                          ","     davon Kredit Sigma:            ",text)
        text = re.sub(r"C12-3310-gabriel                              ","     davon Kredit Christian Gabriel:",text)
        text = re.sub(r"C12-3310-guess                                ","     davon Kredit Guess/Foerster:   ",text)
        text = re.sub(r"C12-3310-[a-z]+ +\-?0.00 *\n","",text,9999)
        text = re.sub(r" +davon.*?\: +\-?0.00 *\n","",text,9999)


        text = re.sub(r"C13                                           ","\nVERBINDLICHKEITEN\n\n"+
                                                                        "C13: sonstige Verbindlichkeiten               ",text,1)
        text = re.sub(r"C13-3035                                      ","  3035   Rueckstellung Gewerbesteuer          ",text)
        text = re.sub(r"C13-3040                                      ","  3040   Rueckstellung Koerperschaftsteuer    ",text)
        text = re.sub(r"C13-3050                                      ","  3050   Rueckstellung Kapitalertragsteuer    ",text)
        text = re.sub(r"C13-3060                                      ","  3060   Rueckstellung Umsatzsteuer           ",text)
        text = re.sub(r"C13-3065                                      ","  3065   Rueckstellung Lohnsteuer             ",text)
        text = re.sub(r"C13-3740                                      ","  3740   Rueckstellung SozVersicherungstraeger",text)
        text = re.sub(r"C13-3740-1510                                 ","     davon DAK:          ",text)
        text = re.sub(r"C13-3740-1511                                 ","     davon AOK Hessen:   ",text)
        text = re.sub(r"C13-3740-1512                                 ","     davon Minijob:      ",text)
        text = re.sub(r"C13-3740-1513                                 ","     davon VBU:          ",text)
        text = re.sub(r"C13-3740-1514                                 ","     davon AOK Bayern:   ",text)
        text = re.sub(r"C13-3740-1515                                 ","     davon Mobiloil:     ",text)
        text = re.sub(r"C13-3740-1516                                 ","     davon Siemens BK:   ",text)
        text = re.sub(r"C13-3740-1517                                 ","     davon TechnikerKK:  ",text)
        text = re.sub(r"C13-3740-1518                                 ","     davon Barmer:       ",text)
        text = re.sub(r"C13-3740-1519                                 ","     davon Debeka:       ",text)
        text = re.sub(r"C13-3740-1520                                 ","     davon AOK Rhl.Pf.:  ",text)
        text = re.sub(r"C13-3740-1521                                 ","     davon AOK NordWest: ",text)
        text = re.sub(r"C13-3740-1522                                 ","     davon AOK Baden-W.: ",text)
        text = re.sub(r"C13-3740-1523                                 ","     davon IKK classic:  ",text)
        text = re.sub(r"C13-3740-1524                                 ","     davon Hanseatische: ",text)
        text = re.sub(r" +davon.*?\: +\-?0.\d\d *\n","",text,9999)
        text = re.sub(r"C13-3751                                      ","  3751   Verbindlichkeiten Unternehmenssteuern",text)
        text = re.sub(r"C13-3751-1502                                 ","     davon Umsatzsteuer: ",text)
        text = re.sub(r"C13-3751-1503                                 ","     davon Lohnsteuer:   ",text)
        text = re.sub(r"C13-3751-1505                                 ","     davon Koerpers.st.: ",text)
        text = re.sub(r"C13-3751-1506                                 ","     davon Gewerbesteuer:",text)
        text = re.sub(r"C13-3751-1507                                 ","     davon Quellensteuer:",text)
        text = re.sub(r" +davon.*?\: +\-?0.\d\d *\n","",text,9999)
        text = re.sub(r"C13-3759                                      ","  3759   Verbindlichkeiten Sozialversicherung ",text)
        text = re.sub(r"C13-3759-1510                                 ","     davon DAK:          ",text)
        text = re.sub(r"C13-3759-1511                                 ","     davon AOK Hessen:   ",text)
        text = re.sub(r"C13-3759-1512                                 ","     davon Minijob:      ",text)
        text = re.sub(r"C13-3759-1513                                 ","     davon VBU:          ",text)
        text = re.sub(r"C13-3759-1514                                 ","     davon AOK Bayern:   ",text)
        text = re.sub(r"C13-3759-1515                                 ","     davon Mobiloil:     ",text)
        text = re.sub(r"C13-3759-1516                                 ","     davon Siemens BK:   ",text)
        text = re.sub(r"C13-3759-1517                                 ","     davon TechnikerKK:  ",text)
        text = re.sub(r"C13-3759-1518                                 ","     davon Barmer:       ",text)
        text = re.sub(r"C13-3759-1519                                 ","     davon Debeka:       ",text)
        text = re.sub(r"C13-3759-1520                                 ","     davon AOK Rhl.Pf.:  ",text)
        text = re.sub(r"C13-3759-1521                                 ","     davon AOK NordWest: ",text)
        text = re.sub(r"C13-3759-1522                                 ","     davon AOK Baden-W.: ",text)
        text = re.sub(r"C13-3759-1523                                 ","     davon IKK classic:  ",text)
        text = re.sub(r"C13-3759-1524                                 ","     davon Hanseatische: ",text)
        text = re.sub(r" +davon.*?\: +\-?0.\d\d *\n","",text,9999)

        text = re.sub(r"C14                                           ","\nSONDER-RUECKSTELLUNGEN\n\n"+
                                                                        "C14: Sonder-Rueckstellungen                   ",text,1)
        text = re.sub(r"C14-2971                                      ","  2971   Sonderrueckstellung China            ",text)
        text = re.sub(r"C14-2972                                          ","  2972   Sonderruecklage Nachforderungen Haus Gera",text)




        text = re.sub(r"D1a                                           ","\nERLOESE\n\n"+
                                                                        "D1a: Umsatzerloese                            ",text,1)
        text = re.sub(r"D..-4100                                      ","  4100   Erloese ohne USt",text)
        text = re.sub(r"D..-4105                                      ","  4105   Steuerfreie Umsaetze durch Vermietung",text)
        text = re.sub(r"D..-4105-(\S+)                                    ","     davon \\1: ",text,999)
        text = re.sub(r" +davon.*?\: +\-?\d\.\d\d *\n","",text,9999)
        text = re.sub(r"D..-4106                                      ","  4106   Nebenkostenabrechnung, steuerfrei    ",text)
        text = re.sub(r"D..-4106-(\S+)                                    ","     davon \\1: ",text,999)
        text = re.sub(r" +davon.*?\: +\-?\d\.\d\d *\n","",text,9999)
        text = re.sub(r"D..-4110                                      ","  4110   Privatnutzung   ",text)
        text = re.sub(r"D..-4300                                      ","  4300   Erloese  7% USt ",text)
        text = re.sub(r"D..-4400                                      ","  4400   Erloese 19% USt ",text)
        text = re.sub(r"D..-4400-(\S+)                                    ","     davon \\1: ",text,999)

        text = re.sub(r"D..-4401                                      ","  4401   Erloese 19% USt durch Parkgebuehren",text)
        text = re.sub(r"D..-4401-(\S+)                                    ","     davon \\1: ",text,999)
        text = re.sub(r"D..-4101                                      ","  4101   Steuerfr. Ums durch Vertragsstrafen",text)
        text = re.sub(r"D..-4101-(\S+)                                    ","     davon \\1: ",text,999)
        text = re.sub(r" +davon.*?\: +\-?\d\.\d\d *\n","",text,9999)
        text = re.sub(r" +davon.*?\: +\-?\d\.\d\d *\n","",text,9999)





#        text = re.sub(r"D2a                                           ","\n"+
#                                                                        "D2a: Parkerloese                          ",text,1)
#        text = re.sub(r"D..-4500                                      ","  4500   Parkerloese 19% ",text)
#        text = re.sub(r"D..-4510                                      ","  4510   Strafgebuehr 0% ",text)


        text = re.sub(r"D3a                                           ","\nERTRAEGE\n\n"+
                                                                        "D3a: sonstige betriebliche Ertraege            ",text,1)
        text = re.sub(r"D..-4440                                      ","  4440   ZIM Foerderung                        ",text)
        text = re.sub(r"D..-4441                                      ","  4440   Einnahmenausgleich                    ",text)
        text = re.sub(r"D..-4442                                      ","  4440   Foerderung Kultur                     ",text)
        text = re.sub(r"D..-4945                                      ","  4945   Verlustvortrag                        ",text)
        text = re.sub(r"D..-4946                                      ","  4946   Aufloesung Sonder-Rueckstellung China ",text)
        text = re.sub(r"D..-4947                                      ","  4947   Verrechnungen sonstige Sachbezuege PKW",text)
        text = re.sub(r"D..-4970                                      ","  4970   Erstattung Krankheitsausfall          ",text)
        text = re.sub(r"D..-4982                                      ","  4982   Erstattung Krankheitsausfall          ",text)
        text = re.sub(r"D..-6075                                      ","  4982   Zuschuesse der Agenturen fuer Arbeit  ",text)
        text = re.sub(r"D..-7110                                      ","  7110   Zinsen auf Bodenwerte                 ",text)
        text = re.sub(r"D..-7141                                      ","  7141   Allgemeine Zinsen                     ",text)
        text = re.sub(r"D..-7111                                      ","  7111   Mieten                                ",text)

#        text = re.sub(r"D4a                                           ","\n"+
#                                                                        "D4a: Aufwaende Parken                         ",text,1)
#        text = re.sub(r"D..-6110                                      ","  6110   Gesetzliche Sozialaufwendungen       ",text)



        text = re.sub(r"D5a                                           ","\nPERSONALAUFWAND\n\n"+
                                                                        "D5a: Verguetungen fuer Personal                ",text,1)
        text = re.sub(r"D..-6010                                      ","  6010   Loehne und Gehaelter                  ",text)
        text = re.sub(r"D..-6011                                      ","  6011   Loehne und Gehaelter 12park           ",text)
        text = re.sub(r"D..-6011-(\S+)                                    ","     davon \\1: ",text,999)
        text = re.sub(r"D..-6020                                      ","  6020   freiberufliche Verguetung             ",text)
        text = re.sub(r"D..-6021                                      ","  6021   Aktivierung lohnbezogener Gueter      ",text)


        text = re.sub(r"D5b                                           ","\n"+
                                                                        "D5b: soziale Abgaben                            ",text,1)
        text = re.sub(r"D..-6110                                      ","  6110   Gesetzliche Sozialaufwendungen         ",text)
        text = re.sub(r"D..-6111-(\S+)                                    ","     davon \\1: ",text,999)
        text = re.sub(r"D..-6111                                      ","  6111   Gesetzliche Sozialaufwendungen 12park  ",text)


        text = re.sub(r"D5c                                           ","\n"+
                                                                        "D5c: Aktivierung gehaltsbezogener Gueter        ",text,1)
        text = re.sub(r"D..-6021                                      ","  6021   Aktivierung erstellter Gueter          ",text)

        text = re.sub(r"D6a                                           ","\nABSCHREIBUNGEN\n\n"+
                                                                        "D6a: auf immaterielles Vermoegen u.Sachanlagen",text,1)
        text = re.sub(r"D..-6219                                        ","  6219   Sonderabschreibungen                   ",text)
        text = re.sub(r"D..-6220                                        ","  6220   Abschreibungen auf Sachanlagen         ",text)
        text = re.sub(r"D..-6240                                        ","  6240   Abschreibungen auf Sachanlagen 5 Jahre ",text)
        text = re.sub(r"D..-6242                                        ","  6242   Abschreibungen auf Sachanlagen 10 Jahre",text)
        text = re.sub(r"D..-6245                                        ","  6245   Abschreibungen auf Sachanlagen 50 Jahre",text)


        text = re.sub(r"D7a                                           ","\nSONSTIGE BETRIEBLICHE AUFWENDUNGEN\n\n"+
                                                                        "D7a: Raumkosten                               ",text,1)
        text = re.sub(r"D..-6310                                      ","  6310   Miete, unbewegliche Wirtschaftsgueter",text)
        text = re.sub(r"D..-6325                                      ","  6325   Gas, Strom, Wasser, Oel              ",text)
        text = re.sub(r"D..-6326                                      ","  6326   Heizablesung                         ",text)
        text = re.sub(r"D..-6330                                      ","  6330   Reinigung                            ",text)
        text = re.sub(r"D..-6340                                      ","  6340   Gas                                  ",text)
        text = re.sub(r"D..-6341                                      ","  6341   Strom                                ",text)
        text = re.sub(r"D..-6342                                      ","  6342   Wasser                               ",text)
        text = re.sub(r"D..-6343                                      ","  6343   Abwasser                             ",text)
        text = re.sub(r"D..-6344                                      ","  6344   Oel                                  ",text)
        text = re.sub(r"D..-6345                                      ","  6345   Muell                                ",text)
        text = re.sub(r"D..-6350                                      ","  6350   Hausmeister und Wartung              ",text)


        text = re.sub(r"D7b                                           ","\n"+
                                                                        "D7b: Versicherungen, Beitraege und Abgaben    ",text,1)
        text = re.sub(r"D..-6405                                      ","  6405   Versicherungen von Gebaeuden         ",text)
        text = re.sub(r"D..-6420                                      ","  6420   Beitraege                            ",text)
        text = re.sub(r"D..-6430                                      ","  6430   Sonstige Abgaben                     ",text)
        text = re.sub(r"D..-6436                                      ","  6436   Abzugf.Verspaetungszuschl./Zwangsgeld",text)


        text = re.sub(r"D7c                                           ","\n"+
                                                                        "D7c: Reparaturen und Instandhaltungen         ",text,1)
        text = re.sub(r"D..-5100                                      ","  5100   Einkauf v.Roh.Hilfs.u.Betriebsstoffen",text)
        text = re.sub(r"D..-6450                                      ","  6450   Reparaturen u.Instandhalt. von Bauten",text)
        text = re.sub(r"D..-6470                                      ","  6470   Reparaturen von Betriebsausstattung  ",text)
        text = re.sub(r"D..-6485                                      ","  6485   Schornsteinfeger                     ",text)
        text = re.sub(r"D..-6490                                      ","  6490   Sonst.Reparaturen u.Instandhaltungen ",text)


        text = re.sub(r"D7d                                           ","\n"+
                                                                        "D7d: Fahrzeugkosten                           ",text,1)
        text = re.sub(r"D..-6520                                      ","  6520   Kfz-Versicherungen                   ",text)
        text = re.sub(r"D..-6530                                      ","  6530   Laufende Kfz-Betriebskosten          ",text)
        text = re.sub(r"D..-6540                                      ","  6540   Kfz-Reparaturen                      ",text)
        text = re.sub(r"D..-6560                                      ","  6560   Mietleasing Kfz                      ",text)
        text = re.sub(r"D..-6570                                      ","  6570   Sonstige Kfz-Kosten                  ",text)
        text = re.sub(r"D..-6595                                      ","  6595   Unfall-Rueckverguetung               ",text)


        text = re.sub(r"D7e                                           ","\n"+
                                                                        "D7e: Werbe- und Reisekosten                   ",text,1)
        text = re.sub(r"D..-6600                                      ","  6600   Werbekosten                          ",text)
        text = re.sub(r"D..-6601                                      ","  6601   Personal-Sachleistungen              ",text)
        text = re.sub(r"D..-6611                                      ","  6611   Abzugsf.Zuwend.an Dritte ohne Beleg  ",text)
        text = re.sub(r"D..-6612                                      ","  6612   Ermaessigung Vertragstrafen          ",text)
        text = re.sub(r"D..-6612-(\S+)                                    ","     davon \\1: ",text,999)
        text = re.sub(r"D..-6640                                      ","  6640   Bewirtungskosten                     ",text)
        text = re.sub(r"D..-6643                                      ","  6643   Aufmerksamkeiten                     ",text)
        text = re.sub(r"D..-6644                                      ","  6644   Nicht abzugsfaehige Bewirtungskosten ",text)
        text = re.sub(r"D..-6660                                      ","  6660   Reisekosten Uebernachtungsaufwand    ",text)
        text = re.sub(r"D..-6663                                      ","  6663   Reisekosten Fahrtkosten              ",text)



        text = re.sub(r"D7f                                           ","\n"+
                                                                        "D7f: verschiedene betriebliche Kosten         ",text,1)
        text = re.sub(r"D..-5840                                      ","  5840   Zoll                                 ",text)
        text = re.sub(r"D..-6770                                      ","  6770   Verkaufsprovisionen                  ",text)
        text = re.sub(r"D..-6800                                      ","  6800   Porto                                ",text)
        text = re.sub(r"D..-6805                                      ","  6805   Telefon                              ",text)
        text = re.sub(r"D..-6815                                      ","  6815   Buerobedarf                          ",text)
        text = re.sub(r"D..-6816                                      ","  6816   Parkscheine fuer Tests               ",text)
        text = re.sub(r"D..-6816-(\S+)                                ","     davon \\1: ",text,999)
        text = re.sub(r"D..-6817                                      ","  6817   Anteilige Abgabe fuer Parkscheine    ",text)
        text = re.sub(r"D..-6817-(\S+)                                ","     davon \\1: ",text,999)
        text = re.sub(r"D..-6818                                      ","  6818   Anteilige Abgabe fuer Vertragsstrafen",text)
        text = re.sub(r"D..-6818-(\S+)                                ","     davon \\1: ",text,999)
        text = re.sub(r"D..-6820                                      ","  6820   Buecher                              ",text)
        text = re.sub(r"D..-6821                                      ","  6821   Fortbildungskosten                   ",text)
        text = re.sub(r"D..-6822                                      ","  6822   Freiwillige Sozialleistungen         ",text)
        text = re.sub(r"D..-6825                                      ","  6825   Rechts- und Beratungskosten          ",text)
        text = re.sub(r"D..-6826                                      ","  6826   Foerderberatung                      ",text)
        text = re.sub(r"D..-6838                                      ","  6838   Verwaltungskosten Immobilien         ",text)
        text = re.sub(r"D..-6845                                      ","  6845   Ausstattung und Kleingeraete         ",text)
        text = re.sub(r"D..-6850                                      ","  6850   Diverse Kosten                       ",text)
        text = re.sub(r"D..-6851                                      ","  6851   Nicht naeher bestimmte Kosten        ",text)
        text = re.sub(r"D..-6855                                      ","  6855   Nebenkosten des Geldverkehrs         ",text)
        text = re.sub(r"D..-6859                                      ","  6859   Aufwend. f.Abraum u.Abfallbeseitigung",text)



        text = re.sub(r"D7g                                           ","\n"+
                                                                        "D7g: Aktivierungskonto                        ",text,1)
        text = re.sub(r"D..-6986                                      ","  6986   Durchlaufkonto Abschreibungen        ",text)


        text = re.sub(r"D8a                                           ","\n"+
                                                                        "D8a: Aufloesung Vortraege und Rueckstellungen ",text,1)
        text = re.sub(r"D..-4930                                      ","  4930   Aufloesung Verlustvortrag            ",text)
        text = re.sub(r"D..-4931                                      ","  4931   Sonder-Rueckstellung China           ",text)
        text = re.sub(r"D..-4932                                      ","  4932   Sonderruecklage Haus Gera            ",text)


        text = re.sub(r"D9a                                           ","\n"+
                                                                        "D9a: Zinsen und aehnliche Aufwendungen        ",text,1)
        text = re.sub(r"D..-7300                                      ","  7300   Zinsen                               ",text)
        text = re.sub(r"D..-7301                                      ","  7301   Grundschuldgebuehr                   ",text)
        text = re.sub(r"D..-7303                                      ","  7303   Steuerl.abzugsf.Nebenleist.z.Steuern ",text)

        text = re.sub(r"D9b                                           ","\n"+
                                                                        "D9b: Grundbesitzabgaben                       ",text,1)
        text = re.sub(r"D..-7680                                      ","  7680   Grundsteuer                          ",text)
        text = re.sub(r"D..-7810                                      ","  7810   Heiz-u.Betriebskostenrueckzahlungen  ",text)


        text = re.sub(r"([BD])o0                                           ","\n"+
                                                                        "\\1o0: Schwaebisch Gmuend, Lorcher Str.         ",text,9)

        text = re.sub(r"([BD])o1                                           ","\n"+
                                                                        "\\1o1: Rheydt, Gertraudenstr.                   ",text,9)

        text = re.sub(r"([BD])o2                                           ","\n"+
                                                                        "\\1o2: Stolberg, Niedergasse                    ",text,9)

        text = re.sub(r"([BD])o6                                           ","\n"+
                                                                        "\\1o6: Rheydt, Limitenstr.                      ",text,9)

        text = re.sub(r"([BD])o3                                           ","\n"+
                                                                        "\\1o3: Mietwohnung Wien, Burggasse              ",text,9)

        text = re.sub(r"([BD])oa                                           ","\n"+
                                                                        "\\1oa: 12park MANDANTEN                         ",text,9)

        text = re.sub(r"([BD])ob                                           ","\n"+
                                                                        "\\1ob: 12park ALLGEMEIN                         ",text,9)

        text = re.sub(r"Bo.-1700                                                    ",
                                                                        "      Vertragsstrafen ausstehend        ",text,99)
        text = re.sub(r"Bo.-ver                                                     ",
                                                                        "      Vorauszahlungen Versorger         ",text,99)
        text = re.sub(r"Bo.-kto                                                     ",
                                                                        "      Vorauszahlungen Mieter            ",text,99)
        text = re.sub(r"Bo.-umlagen                                                 ",
                                                                        "      umzulegende Betriebs-u.Nebenkosten",text,99)
        text = re.sub(r"Bo.-(ver|kto|umlagen|1700)-(\S+)                                        ","         davon \\2:  ",text,999)




        for i in (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20):
            text = re.sub(r"\n  \d\d\d\d.*? \-?0.00 [\-0\. ]*\n","\n",text,99999999)
            text = re.sub(r"\n +davon.*? \-?0.\d\d [\-0\. ]*\n","\n",text,99999999)

#        print(text)
#        return()

        text = re.sub(r"Daa    ","\nUNTERNEHMENSSTEUERN\n\n"+
                                                                        "Daa: Koerperschaft- und Gewerbesteuer          ",text,1)
        text = re.sub(r"Daa-7603                 ","  7603   Koerperschaftsteuer                   ",text)
        text = re.sub(r"Daa-7608                 ","  7608   Solidaritaetszuschlag zur KoerpSteuer ",text)
        text = re.sub(r"Daa-7610                 ","  7610   Gewerbesteuer                         ",text)


        text = re.sub(r"Dba                      ","\nENTNAHME\n\n"+
                                                           "Dba: Ausschuettungen und Quellensteuer        ",text,1)
        text = re.sub(r"Dba-7790                 ","  7790   Ausschuettung an Gesellschafter      ",text)
        text = re.sub(r"Dba-3700                 ","  3700   Quellensteuer                        ",text)
        text = re.sub(r"Dba-3708                 ","  3708   Solidaritaetszuschlag zur Quellensteu",text)

        text = re.sub(r"Dca                      ","\nJAHRESERGEBNIS\n\n"+
                                                                        "Dca: Jahresergebnis nach Steu.u.Ausschuettung ",text,1)
        text = re.sub(r"Dca-7639                 ","  7639   Jahres-Nettoueberschuss              ",text)


        for key1 in self.dataset:
            if not key1.startswith("bilanzreplace"):
                continue
            m = re.search(r"^(.*),(.*)$",self.dataset[key1])
            a = m.group(1)
            b = m.group(2)
            c = max(len(a),len(b))
            a = (a+"                                                                   ")[0:c]
            b = (b+"                                                                   ")[0:c]
            if not m:
                continue
            text = text.replace(a,b)

#        print(text)

        text1 = ""
        for zeile in text.split("\n"):
            if re.search(r"^\=+$",zeile):
                text1 = text1 + zeile + "\n"
                continue
            zeile1 = zeile
            if re.search(r"^BILANZ ",zeile):
                zeile1 = zeile + "\n" + ("=" * len(zeile))
            m = re.search(r"^([A-Z].*?) +( \-?\d+\.\d\d)(.*)$",zeile)
            if m:
                zeile1 = ("%-50s" % m.group(1)) + ("%13s" % m.group(2))
#                if re.search(r"^[A-Z]+$",m.group(1)):
#                    zeile1 = zeile1 + "\n" + ("-" * len(zeile1)) # m.group(1))
                zeile1 = zeile1 + "                                    "
                zeile1 = zeile1[0:75] + m.group(3)[-12*self.FORMAT2:]
            m = re.search(r"^( +\d\d\d\d.*?) +( \-?\d+\.\d\d)(.*)$",zeile)
            if m:
                zeile1 = ("%-54s" % m.group(1)) + ("%13s" % m.group(2))
                zeile1 = zeile1 + "                                    "
                zeile1 = zeile1[0:75] + m.group(3)[-12*self.FORMAT2:]
            m = re.search(r"^( +davon.*?) +( \-?\d+\.\d\d)(.*)$",zeile)
            if m:
                zeile1 = ("%-39s" % m.group(1)) + ("%13s" % m.group(2))
                zeile1 = zeile1 + "                                    "
                zeile1 = zeile1[0:75] + m.group(3)[-12*self.FORMAT2:]
            text1 = text1 + zeile1 + "\n"
            
        if WITH_BWA == 1:
            text_monate = ""
            for mm in "JA FE MR AP MA JN JL AU SE OC NO DE".split(" "):
                text_monate = text_monate + (self.FORMAT3 % mm)
#            text1 = re.sub(r"(AUFWAND +\-?\d+\.\d\d)","\\1            "  + text_monate,text1)
            text1 = re.sub(r"ANLAGEVERMOEGEN",  "ANLAGEVERMOEGEN  " + " "*58 + text_monate+"\n"+"-"*171,text1)
            text1 = re.sub(r"STAMMKAPITAL",     "STAMMKAPITAL     " + " "*58 + text_monate+"\n"+"-"*171,text1)
            text1 = re.sub(r"ERLOESE",          "ERLOESE          " + " "*58 + text_monate+"\n"+"-"*171,text1)
            text1 = re.sub(r"UMLAUFVERMOEGEN",  "UMLAUFVERMOEGEN  " + " "*58 + text_monate+"\n"+"-"*171,text1)
            text1 = re.sub(r"PERSONALAUFWAND",  "PERSONALAUFWAND  " + " "*58 + text_monate+"\n"+"-"*171,text1)

        file = jahr + "_bilanz_"+bez+"__20" + jahr
        open(file + ".md","w").write(text1)

        file = "anlagen_einnahmen_ausgaben_umsatz_vorsteuer_"+bez+"__20" + jahr

        text1 = ( "Anlagen, Einnahmen, Ausgaben, Umsatz- und Vorsteuer zu " + name + " 20" +jahr + ":\n" +
                  ("=" * len("Anlagen, Einnahmen, Ausgaben, Umsatz- und Vorsteuer zu " + name + " 20" +jahr + ":")) + "\n\n"
                  "ANLAGEN:\n=======\n\n" + anlagen + "\n\n\n" + 
                  "EINNAHMEN:\n=========\n\n" + einnahmen + "\n\n\n" + 
                  "AUSGABEN:\n========\n\n" + ausgaben + "\n\n\n" + 
                  "UMSATZ- UND VORSTEUER:\n======================\n\n" + ust )
        open(file + ".md","w").write(text1)


#**********************************************************************************************

if __name__ == "__main__":

    Bilanz().base_bilanz(*(sys.argv[1:]))
    
