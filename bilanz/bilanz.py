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
                        "C11-3170","C11-3170-[a-z]+","C12-3500","B12-1435","B23-1437","B21-1300","B12-1340","B12-3695","B12-3696","D3a-4600","D1a-4610",
                        "Do.-6011","Do.-6111","Do.-6816","Do.-6817","Do.-6818","D7f-6612","C02-2080","B23-1890","B25-[^\ ]+","X[EFGH]11-[^\- ]+","F11-001",
                        "Bo.-ver","Bo.-kto","Bo.-umlagen","Bo.-1700","C01-2900","D7f-6870","D7f-6870-[A-Z].*","B22-1827","B22-1829","B22-1892",
                        "D..-4100","D..-4105","D..-4106","D..-4400","D..-4505"]
                        
#        self.ebilanz = {}
#        self.taxo    = self.taxo_2022_02()
        
        kto          = Konto()
        self.dataset = kto.read_config()

#*********************************************************************************

    def mark (self,remark=""):

        t = time.perf_counter()
        if 't0' in vars(self):
            print ( ("%9.2f" % ((t-self.t0)*1000)) + " ms for:  " + remark )
        self.t0 = t

#*****************************************************************************************************

    def xxmap (self,text,kto1,kto2=None):
    
        kto1 = "%04u" % int(kto1)
        
        m = re.search(r"(  |-)" + kto1 + r" (.*?) +(\-?\d+\.\d\d) ",text)
    

        if kto2:
            kto2 = "%04u" % int(kto2)
        else:
            kto2 = kto1

        if not kto2 in self.ebilanz:
            self.ebilanz[kto2] = 0.00
            
        try:
            self.ebilanz[kto2] = self.ebilanz[kto2] + float(m.group(3))
        except:
            print(text)
            print(kto1,kto2,m)
            print(r"(  |-)" + kto1 + r" (.*?) +(\-?\d+\.\d\d) ")
            exit()
    
        return("")

#*********************************************************************************

    def base_bilanz (self,*pars):     # open the csv and kto files and prepare for processing

        jahr = pars[0]
        try:
            name = self.dataset["firmabez"]
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
            os.system("a2ps -B -1 -l 172 -r -o bilanz_" + jahr + "_" + bez + "_zusaetze.ps anlagen*" + jahr + ".md")
#            os.system("a2ps -B -1 -l 172 -r -o anlagen_" + jahr + "_" + bez + ".ps anlagen*" + jahr + ".txt")
            os.system("ps2pdf bilanz_" + jahr + "_" + bez + "_zusaetze.ps")
            os.system("cp " + jahr + "_*md bilanz_" + jahr + "_" + bez + "_hauptteil.txt")
            os.system("cp anlagen*" + jahr + ".md bilanz_" + jahr + "_" + bez + "_zusaetze.txt")
#            os.system("ps2pdf anlagen_" + jahr + "_" + bez + ".ps")
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

        kto.read_saldo("90-:"+jahr)
#        text1 = "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\f\nXXERTRAG " + os.popen("grep -P '^(\S+|     ) +(\S+) *$' *kto").read()
        text1 = "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\f\nXXGOODS  " + kto.salden_text()
        text1 = re.sub(r" (\-?\d+\.\d\d)","-\\1",text1,999999)  #  Minuszeichen
        text1 = re.sub(r" --","   ",text1,999999)
        text_add = text1

        kto.read_saldo("91-:"+jahr)
#        text  = text + "\nXXAUFWAND" + re.sub(r"Do","Xo",os.popen("grep -P '^(\S+|     ) +(\S+) *$' *kto").read(),99999999)
        text_add  = text_add + "\nXXVALUES " + re.sub(r"Do","Xo",kto.salden_text(),99999999)

        kto.read_saldo("92-."+jahr)
#        text1 = "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\f\nXXERTRAG " + os.popen("grep -P '^(\S+|     ) +(\S+) *$' *kto").read()
        text1 = "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\f\nXXGDIFF  " + kto.salden_text()
        text1 = re.sub(r" (\-?\d+\.\d\d)","-\\1",text1,999999)  #  Minuszeichen
        text1 = re.sub(r" --","   ",text1,999999)
        text_add = text_add + text1

        kto.read_saldo("93-."+jahr)
#        text  = text + "\nXXAUFWAND" + re.sub(r"Do","Xo",os.popen("grep -P '^(\S+|     ) +(\S+) *$' *kto").read(),99999999)
        text_add  = text_add + "\nXXVDIFF   " + re.sub(r"Do","Xo",kto.salden_text(),99999999)
        
        o1 = re.sub(r"0","",text_add,99999999)
        if not re.search(r"\d\.\d\d",o1):
            text_add = ""

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
#            monat_guv.append( o1 + o2 + o3 + o4 ) # open(glob.glob("*kto")[0]).read() )

            kto.read_saldo("90-:"+jahr+monat)
            o5 = "\nGOODS    " + kto.salden_text()
#            o5 = "\nERTRAG   " + os.popen("grep -P '^(\S+|     ) +(\S+) *$' *kto").read()
#            o5 = open(glob.glob("*kto")[0]).read()
            
            kto.read_saldo("91-:"+jahr+monat)
            o6 = "\nVALUES    " + kto.salden_text()
#            o6 = "\nAUFWAND   " + os.popen("grep -P '^(\S+|     ) +(\S+) *$' *kto").read()
#            o4 = re.sub(r"Do","Xo",o4,999999)

            kto.read_saldo("92-."+jahr+monat)
            o7 = "\nGDIFF   " + kto.salden_text()
#            o7 = "\nERTRAG   " + os.popen("grep -P '^(\S+|     ) +(\S+) *$' *kto").read()
#            o7 = open(glob.glob("*kto")[0]).read()
            o7 = re.sub(r" (\-?\d+\.\d\d)","-\\1",o7,999999)  #  Minuszeichen
            o7 = re.sub(r" --","   ",o7,999999)
            
            kto.read_saldo("93-."+jahr+monat)
            o8 = "\nVDIFF     " + kto.salden_text()
#            o8 = "\nAUFWAND   " + os.popen("grep -P '^(\S+|     ) +(\S+) *$' *kto").read()
            o8 = re.sub(r"Do","Xo",o8,999999)
            o8 = re.sub(r" (\-?\d+\.\d\d)","-\\1",o8,999999)  #  Minuszeichen
            o8 = re.sub(r" --","   ",o8,999999)
#            monat_guv.append( o1 + o2 + o3 + o4 ) # open(glob.glob("*kto")[0]).read() )

            monat_guv.append( o1 + o2 + o3 + o4 + o5 + o6 + o7 + o8 ) # open(glob.glob("*kto")[0]).read() )
#            print(jahr+monat)
#            print( o1 + o2 + o3 + o4 + o5 + o6 + o7 + o8 ) # open(glob.glob("*kto")[0]).read() )

#        text = re.sub(r"( .\d+\.\d\d)","                        \\1",text,99999999)
#        text = re.sub(r"\nXX([A-Z]+)        ([^\n]+)","\n\n\n\\1\\2\n=======",text,9999)

        kto.read_saldo("14-."+jahr)
#        text  = text + "\n\n\f\nABSCHLUSS" + os.popen("grep -P '^(\S+|     ) +(\S+) *$' *kto").read()
        text  = text + "\n\n\f\nABSCHLUSS" + kto.salden_text()

        text = text + text_add

        text = re.sub(r"( .\d+\.\d\d)","                                                      \\1",text,99999999)
        text = re.sub(r"\nXX([A-Z]+)        ([^\n]+)","\n\n\n\\1\\2\n=======\n",text,9999)

        Konto(self.ktotyp).kto("^12-."+jahr)
        einnahmen = open(glob.glob("*kto")[0]).read()

        Konto(self.ktotyp).kto("^13-."+jahr)
        ausgaben = open(glob.glob("*kto")[0]).read()

        Konto(self.ktotyp).kto("^10-A11-."+jahr)
        anlagen = open(glob.glob("*kto")[0]).read()

        Konto(self.ktotyp).kto("^11-C13-3060-."+jahr)
        ust = open(glob.glob("*kto")[0]).read()

 #       print(text)
 #       exit()

        text = re.sub(r"\n([^\-]{3}  +\-?\d+\.\d\d) *","\n\n\\1\n",text,99999999)

        text1 = ""
        for zeile in text.split("\n"):
            m   = re.search(r"^([ABCEFGH]\S\S|AXKTIVA|PXASSIVA|ERTRAG|AUFWAND|GOODS|VALUES|GDIFF|VDIFF|[DX][o\d]\S)(|\-\S+) (.*?)(\-?\d+\.\d\d) *$",zeile)
            if m:
                kto = m.group(1) + m.group(2)
                if len(zeile) > 95:
                    zeile = re.sub(r"          ","",zeile,1)
                if len(zeile) > 95:
                    zeile = re.sub(r"          ","",zeile,1)
                if len(zeile) > 95:
                    zeile = re.sub(r"    ","",zeile,1)
                zeile = zeile + "                                                     "
                zeile = zeile[0:95]
                for monat in monat_guv:
                    if kto.startswith("C02") or kto.startswith("D6a"):
                        continue
                    m = re.search("\n"+kto + " +(.*?)(\-?\d+\.\d\d)",monat)
                    betrag = 0
                    if m:
                        betrag = round(float(m.group(2)))
                    betrag = self.FORMAT1 % betrag
                    zeile  = zeile + betrag
            text1 = text1 + zeile + "\n"

        text = re.sub(r"Xo","Do",text1,99999999)

 #       print(text)
 #       exit()

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
        text = re.sub(r"A11-0310                                      ","  0310   Immob. Schw.Gmuend, Lorcher Str.98, EGH",text)
        text = re.sub(r"A11-0311                                      ","  0311   Immob. Rheydt, Gertraudenstr. 73, ETW",text)
        text = re.sub(r"A11-0312                                      ","  0312   Immob. Stolberg, Niedergasse 27, MFH ",text)
        text = re.sub(r"A11-0316                                      ","  0316   Immob. Rheydt, Limitenstr. 27, ETW   ",text)
        text = re.sub(r"A11-0500                                      ","  0500   Betriebs- und Geschaeftsausstattung  ",text)
        text = re.sub(r"A11-0520                                      ","  0520   PKW                                  ",text)
        text = re.sub(r"A11-0560                                      ","  0560   Sonstige Transportmittel             ",text)
        text = re.sub(r"A11-0670                                      ","  0670   Geringwertige Wirtschaftsgueter      ",text)
        text = re.sub(r"A11-0675                                      ","  0675   Wirtschaftsgueter Sammelposten       ",text)
        text = re.sub(r"A11-0610                                      ","  0610   Anlag. Schw.Gmuend, Lorcher Str.98, EGH",text)
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
        text = re.sub(r"B12-1500                                      ","  1500   Geschaeftsanteile VRBank             ",text)
        text = re.sub(r"B12-3695                                      ","  3695   Forderg. gg. Mitarbeitern, Auslagen  ",text)
        text2 = text
        text = re.sub(r"B12-3695-(\S+)                                ","     davon \\1:          ",text,999)
        text = re.sub(r" +davon.*?\: +\-?\d\.\d\d *\n","",text,9999)
        text = re.sub(r"B12-3696                                      ","  3696   Offene Vertragsstrafen               ",text)
        text = re.sub(r"B12-3696-([\S\-]+)                            ","     davon \\1:          ",text,999)
        text = re.sub(r"B12-1457                                      ","  1457   Forderung AAG KUG                    ",text)


        text = re.sub(r"B21                                           ","\n"+
                                                                        "B21: Kreditforderungen                        ",text,1)
        text = re.sub(r"B21-1300                                      ","  1300   Kreditforderungen                    ",text)
        text = re.sub(r"B21-1300-bebop                                ","     davon bebop Betrieb:    ",text)
        text = re.sub(r"B21-1300-immobilien                           ","     davon Immobilien:       ",text)
        text = re.sub(r"B21-1300-beratung                             ","     davon Beratung:         ",text)
        text = re.sub(r"B21-1300-privat                               ","     davon Privatbereich:    ",text)

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
        text = re.sub(r"B22-1827                                      ","  1827   Flessa Bank                          ",text)
        text = re.sub(r"B22-1827-(\S+)                                ","     davon \\1:          ",text,999)
        text = re.sub(r"B22-1829                                      ","  1829   Sparkasse Fuerth                     ",text)
        text = re.sub(r"B22-1829-(\S+)                                ","     davon \\1:          ",text,999)
        text = re.sub(r"B22-1837                                      ","  1837   Unicredit Bank Banja Luka            ",text)
        text = re.sub(r"B22-1851                                      ","  1851   Kapitalkonto Sparkasse Fuerth        ",text)
        text = re.sub(r"B22-1885                                      ","  1885   Transferkonto Bankueberweisungen     ",text)
        text = re.sub(r"B22-1886                                      ","  1885   Transferkonto Sonstige               ",text)
        text = re.sub(r"B22-1890                                      ","  1890   Bestand gegen andere Geschaeftsfelder",text)
        text = re.sub(r"B22-1891                                      ","  1891   Transferkonto Finanzamt              ",text)
        text = re.sub(r"B22-1892                                      ","  1892   Umbuchungen                          ",text)
        text = re.sub(r"B22-1892-(\S+)                                ","     davon \\1:          ",text,999)

        text = re.sub(r"B23                                           ","\n"+
                                                                        "B23: Verfuegbare Eigenmittel, Tagesgeld       ",text,1)
        text = re.sub(r"B23-1437                                      ","  1437   Steuerkonten                         ",text)
        text = re.sub(r"B23-1437-1506                                        ","     davon Gewerbesteuer Fuerth:",text)
        text = re.sub(r"B23-1437-1508                                             ","     davon Umsatzsteuer Organschaft:",text)
        text = re.sub(r"B23-1437-1509                                        ","     davon Finanzamt Fuerth:    ",text)
        text = re.sub(r"B23-1600                                      ","  1600   Kassenbestand                        ",text)
        text = re.sub(r"B23-1601                                      ","  1601   Kassenbestand cgabriel               ",text)
        text = re.sub(r"B23-1602                                      ","  1602   Kassenbestand dsrdic                 ",text)
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
        text = re.sub(r"B23-1890-(\S+)                                    ","     davon \\1: ",text,999)
        text = re.sub(r"B23-1891                                      ","  1891   Transferkonto Finanzamt              ",text)

        if "B24-2978" in text:
            text = re.sub(r"B24                                           ","\nVERLUSTVORTRAG\n\n"+
                                                                            "B24: Verlustvortrag                           ",text,1)
        text = re.sub(r"B24-2978                                      ","  2978   Verlustvortrag vor Verwendung        ",text)

        text = re.sub(r"B25-9501                                      ","  9501   EUR Value                            ",text)
        text = re.sub(r"B25-9501-(\S+)                                    ","     davon \\1: ",text,999)


        if "C11-297" in text:
            text = re.sub(r"C11                                           ","\nGEWINNVORTRAG\n\n"+
                                                                            "C11: Gewinn-/Verlustvortrag              ",text,1)
        text = re.sub(r"C11-2970                                      ","  2970   Gewinnvortrag vor Verwendung        ",text)
        text = re.sub(r"C11-2978                                      ","  2978   Verlustvortrag                      ",text)
        text = re.sub(r"C14-2971                                      ","  2971   Sonderrueckstellung China            ",text)
        text = re.sub(r"C14-2972                                      ","  2972   Sonderruecklage Nachforderg Haus Gera",text)

        text = re.sub(r"C01                                           ","\nSTAMMKAPITAL\n\n"+
                                                                        "C01: Stammkapital                             ",text,1)
        text = re.sub(r"C01-2900                                      ","  2900   Stammeinlage                         ",text)
        text = re.sub(r"C01-2900-(\S+)                                    ","     davon \\1: ",text,999)


        text = re.sub(r"C02                                           ","\nEIGENKAPITAL\n\n"+
                                                                        "C02: Kumulierte Erloese                       ",text,1)
        text = re.sub(r"C02-2080                                      ","  2080   Kumulierte Erloese vor Verwendung    ",text)
        text = re.sub(r"C02-2080-(\S+)                                    ","     davon \\1: ",text,999)


        text = re.sub(r"C11                                           ","\nDARLEHEN\n\n"+
                                                                        "C11: Darlehen                                  ",text,1)
        text = re.sub(r"C11-3170                                      ","  3170           Darlehen Gesamt               ",text)
        text = re.sub(r"C11-3170-kreditgertrauden                           ","     davon Baudarlehen Gertraudenstr:  ",text)
        text = re.sub(r"C11-3170-kreditlimitenstr                           ","     davon Baudarlehen Limitenstr:     ",text)
        text = re.sub(r"C11-3170-kreditlorcherstr                           ","     davon Baudarlehen SchwGDLorcherS: ",text)
        text = re.sub(r"C11-3170-kreditstolberg                             ","     davon Baudarlehen Stolberg:       ",text)
        text = re.sub(r"C11-3170-kreditingdiba                              ","     davon Darlehen Ing-Diba:          ",text)
        text = re.sub(r"C11-3170-kreditnetbank                              ","     davon Darlehen Netbank:           ",text)
        text = re.sub(r"C11-3170-kreditauxmoney                             ","     davon Darlehen DSL Bank:          ",text)
        text = re.sub(r"C11-3170-kreditvrsmart                              ","     davon Darlehen VR Smart:          ",text)
#        print(text)
        text = re.sub(r"C11-3170-[a-z]+ +\-?0.00 *\n","",text,9999)

        text = re.sub(r"(C11-3170-[a-z]+-)([a-z]+)  ","        (\\2)",text,9999)



        text = re.sub(r"C12                                           ","\nKREDITE\n\n"+
                                                                        "C12: Kredite                                  ",text,1)
        text = re.sub(r"C12-3310                                      ","  3310           Guess/Foerster               ",text)
        text = re.sub(r"C12-3500                                      ","  3500           Kredite Gesamt               ",text)
        text = re.sub(r"C12-3500-reality                              ","     davon Kredit reality:   ",text)
        text = re.sub(r"C12-3500-schlotz                              ","     davon Kredit Dieter Schlotz:   ",text)
        text = re.sub(r"C12-3500-kreditvrsmart                        ","     davon Kredit VRSmart:          ",text)
        text = re.sub(r"C12-3500-kreditsigma                          ","     davon Kredit Sigma:            ",text)
        text = re.sub(r"C12-3500-gabriel                              ","     davon Kredit Christian Gabriel:",text)
        text = re.sub(r"C12-3500-guess                                ","     davon Kredit Guess/Foerster:   ",text)
        text = re.sub(r"C12-3500-[a-z]+ +\-?0.00 *\n","",text,9999)
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

        text = re.sub(r"D..-4610                                      ","  4610   Erloese 19% USt durch Parkgebuehren",text)
        text = re.sub(r"D..-4610-(\S+)                                    ","     davon \\1: ",text,999)
        text = re.sub(r"D..-4601                                      ","  4401   Erloese 19% USt durch Parkgebuehren",text)
        text = re.sub(r" +davon.*?\: +\-?\d\.\d\d *\n","",text,9999)
        text = re.sub(r" +davon.*?\: +\-?\d\.\d\d *\n","",text,9999)





#        text = re.sub(r"D2a                                           ","\n"+
#                                                                        "D2a: Parkerloese                          ",text,1)
#        text = re.sub(r"D..-4500                                      ","  4500   Parkerloese 19% ",text)
#        text = re.sub(r"D..-4510                                      ","  4510   Strafgebuehr 0% ",text)


        text = re.sub(r"D3a                                           ","\nERTRAEGE\n\n"+
                                                                        "D3a: sonstige betriebliche Ertraege            ",text,1)
        text = re.sub(r"D..-4440                                      ","  4440   ZIM Foerderung                        ",text)
        text = re.sub(r"D..-4441                                      ","  4441   Einnahmenausgleich                    ",text)
        text = re.sub(r"D..-4442                                      ","  4442   Foerderung Kultur                     ",text)
        text = re.sub(r"D..-7720                                      ","  7720   Verlustvortrag                        ",text)
        text = re.sub(r"D..-7730                                      ","  7730   Gewinnvortrag Verwendung              ",text)
        text = re.sub(r"D..-7731                                      ","  7731   Aufloesung Sonder-Rueckstellung China ",text)
        text = re.sub(r"D..-4947                                      ","  4947   Verrechnungen sonstige Sachbezuege PKW",text)
        text = re.sub(r"D..-4970                                      ","  4970   Erstattung Krankheitsausfall          ",text)
        text = re.sub(r"D..-4982                                      ","  4982   Erstattung Krankheitsausfall          ",text)
        text = re.sub(r"D..-6075                                      ","  4982   Zuschuesse der Agenturen fuer Arbeit  ",text)
        text = re.sub(r"D..-7110                                      ","  7110   Zinsen auf Bodenwerte                 ",text)
        text = re.sub(r"D..-7141                                      ","  7141   Allgemeine Zinsen                     ",text)
        text = re.sub(r"D..-7011                                      ","  7011   Mieten                                ",text)
        text = re.sub(r"D..-4505                                      ","  4505   Sonstige Sonderbetriebseinnahmen",text)
        text = re.sub(r"D..-4505-(\S+)                                    ","     davon \\1: ",text,999)
        text = re.sub(r"D..-4600                                      ","  4600   Steuerfr. Ums durch Vertragsstrafen",text)
        text = re.sub(r"D..-4600-(\S+)                                    ","     davon \\1: ",text,999)

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
        text = re.sub(r"D..-6346                                      ","  6346   Fernwaerme                           ",text)
        text = re.sub(r"D..-6347                                      ","  6347   Fuchs GmbH                           ",text)
        text = re.sub(r"D..-6348                                      ","  6348   Abfindungen                          ",text)
        text = re.sub(r"D..-6350                                      ","  6350   Hausmeister und Wartung              ",text)
        text = re.sub(r"D..-6351                                      ","  6351   Knappschaft Minijob                  ",text)


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
        text = re.sub(r"D..-6575                                      ","  6575   Transportkosten                      ",text)
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
        text = re.sub(r"D..-6303                                      ","  6303   Fremdleistungen                      ",text)
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
        text = re.sub(r"D..-6837                                      ","  6837   Aufwendungen fuer Lizenzen u. Rechte ",text)
        text = re.sub(r"D..-6837-(\S+)                                ","     davon \\1: ",text,999)
        text = re.sub(r"D..-6838                                      ","  6838   Verwaltungskosten Immobilien         ",text)
        text = re.sub(r"D..-6845                                      ","  6845   Ausstattung und Kleingeraete         ",text)
        text = re.sub(r"D..-6850                                      ","  6850   Diverse Kosten                       ",text)
        text = re.sub(r"D..-6851                                      ","  6851   Nicht naeher bestimmte Kosten        ",text)
        text = re.sub(r"D..-6855                                      ","  6855   Nebenkosten des Geldverkehrs         ",text)
        text = re.sub(r"D..-6857                                      ","  6857   Retouren                             ",text)
        text = re.sub(r"D..-6859                                      ","  6859   Aufwend. f.Abraum u.Abfallbeseitigung",text)

        text = re.sub(r"D..-6870                                      ","  6870   Kirchenmusiktage                     ",text)
        text = re.sub(r"D..-6870-([^- ]+)                             ","\n     davon \\1:     ",text,999)
        text = re.sub(r"D..-6870-([^- ]+)-([^- ]+)                                  ","      davon \\2: ",text,999)
        text = re.sub(r"D..-6870-([^- ]+)-([^- ]+)-([^- ]+)                      ","       davon \\3: ",text,999)
        text = re.sub(r"D..-6870-([^- ]+)-([^- ]+)-([^- ]+)-([^- ]+)              ","        davon \\4: ",text,999)

        text = re.sub(r"D7g                                           ","\n"+
                                                                        "D7g: Aktivierungskonto                        ",text,1)
        text = re.sub(r"D..-6986                                      ","  6986   Durchlaufkonto Abschreibungen        ",text)


        text = re.sub(r"D8a                                           ","\n"+
                                                                        "D8a: Gewinnvortraege und Verwendung Verluste ",text,1)
        text = re.sub(r"D..-7700                                      ","  7700   Gewinnvortrag                        ",text)
        text = re.sub(r"D..-7740                                      ","  7740   Verlustvortrag Verwendung            ",text)
        text = re.sub(r"D..-7701                                      ","  7701   Sonder-Rueckstellung China           ",text)
        text = re.sub(r"D..-7702                                      ","  7702   Sonderruecklage Haus Gera            ",text)


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


        text = re.sub(r"E11                                           ","\nGOODS AND CURRENCIES\n\n"+
                                                                        "E11: Goods and currencies                     ",text,1)
        text = re.sub(r"E11-(\S+)                                     ","     xxyyzz.\\1                                ",text)

        text = re.sub(r"F11                                           ","\nVALUES\n\n"+
                                                                        "F11: Values of goods                          ",text,1)
        text = re.sub(r"F11-(\S+)                                     ","     xxyyzz.\\1                                ",text)

        text = re.sub(r"G11                                           ","\nGOODS RECEIPTS AND ISSUES\n\n"+
                                                                        "G11: Goods receipts and issues                ",text,1)
        text = re.sub(r"G11-(\S+)                                     ","     xxyyzz.\\1                                ",text)

        text = re.sub(r"H11                                           ","\nASSIGNED VALUE DIFFS\n\n"+
                                                                        "H11: Value differences                        ",text,1)
        text = re.sub(r"H11-(\S+)                                     ","     xxyyzz.\\1                                ",text)



        for i in (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20):  #  loeschen von Zeilen, die alle Null sind
            text = re.sub(r"\n +davon.*? \-?0.\d\d [\-0\. ]*\n","\n",text,99999999)

        text = re.sub(r"\n( +davon)","PROTECT\n\\1",text,99999999)
        for i in (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20):  #  loeschen von Zeilen, die alle Null sind
            text = re.sub(r"\n  \d\d\d\d.*? \-?0.00 [\-0\. ]*\n","\n",text,99999999)
        text = re.sub(r"PROTECT","",text,99999999)
        
        
        text = re.sub(r"\nXX([A-Z]+)","\\n\\1\\n=======",text,999999)
        

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
            m = re.search(r"^( +xxyyzz.*?) +( \-?\d+\.\d\d)(.*)$",zeile)
            if m:
                zeile1 = ("%-61s" % m.group(1)) + ("%13s" % m.group(2))
                zeile1 = zeile1 + "                                               "
                zeile1 = zeile1[0:82] + m.group(3)[-12*self.FORMAT2:]
            m = re.search(r"^( +\([a-z]+\)) +( \-?\d+\.\d\d)(.*)$",zeile)
            if m:
                zeile1 = ("%-18s" % m.group(1)) + ("%13s" % m.group(2))
                zeile1 = zeile1 + "                                                    "
                zeile1 = zeile1[0:75] + m.group(3)[-12*self.FORMAT2:]
            text1 = text1 + zeile1 + "\n"
            text1 = re.sub(r"xxyyzz\.","",text1,999999)
            
        text_monate = ""
        if WITH_BWA == 1:
            for mm in "JA FE MR AP MA JN JL AU SE OC NO DE".split(" "):
                text_monate = text_monate + (self.FORMAT3 % mm)
#            text1 = re.sub(r"(AUFWAND +\-?\d+\.\d\d)","\\1            "  + text_monate,text1)
            text1 = re.sub(r"ANLAGEVERMOEGEN",  "ANLAGEVERMOEGEN  " + " "*58 + text_monate+"\n"+"-"*171,text1)
            text1 = re.sub(r"STAMMKAPITAL",     "STAMMKAPITAL     " + " "*58 + text_monate+"\n"+"-"*171,text1)
            text1 = re.sub(r"ERLOESE",          "ERLOESE          " + " "*58 + text_monate+"\n"+"-"*171,text1)
            text1 = re.sub(r"EIGENKAPITAL",     "EIGENKAPITAL     " + " "*58 + text_monate+"\n"+"-"*171,text1)
            text1 = re.sub(r"UMLAUFVERMOEGEN",  "UMLAUFVERMOEGEN  " + " "*58 + text_monate+"\n"+"-"*171,text1)
            text1 = re.sub(r"PERSONALAUFWAND",  "PERSONALAUFWAND  " + " "*58 + text_monate+"\n"+"-"*171,text1)
            text1 = re.sub(r"GOODS AND CURRENCIES",  "GOODS AND CURRENCIES" + " "*55 + text_monate+"\n"+"-"*171,text1)


#-------------------- Kimutage  ---------------------------

        if "kimutage" == name:
        
            m = re.search(r"(^.*?)(PASSIVA.*?)(AUFWAND.*)(ABSCHLUSS.*)$",text1,re.DOTALL)
            text5 = m.group(1)
            text9 = m.group(2)
            text6 = m.group(3)
            text6 = re.sub(r"[\n\f]+$","",text6) + "\n"
            text6 = re.sub(r"\f","",text6)
            text6 = re.sub(r"\n\n\nD7f([^\n]+)","",text6)
            text6 = re.sub(r"\n\n  6870([^\n]+)\n","",text6)
            text5 = re.sub(r"\n\n\nAKTIVA([^\n]+)\n([^\n]+)\n\n","",text5)
            text0 = ""
            text1 = ""

            text0 = text0 + "          Verwendung Summen (nachrichtlich):\n\n\n"
            
            konten = {}
            for zeile in text5.split("\n"):
                m = re.search(r"^ +davon (\S+): +(\S+)",zeile)
                if not m:
                    continue
                if not m.group(1) in konten:
                    konten[m.group(1)] = 0.00
                konten[m.group(1)] = konten[m.group(1)] + float(m.group(2))
            kontenlist = list(konten.keys())
            kontenlist.sort()
            gesamt = 0.00
            for kto in kontenlist:
                gesamt = gesamt + konten[kto]
                text0 = text0 + "              " + kto + (" "*(10-len(kto))) + ("%13.2f" % konten[kto]) + "\n"
            text0 = text0 + "\n              " + "Gesamt" + (" "*(10-len("Gesamt"))) + ("%13.2f" % gesamt) + "\n"
            text0 = text0 + "\n\n\n\n"


            print(text6)
            
            text6 = re.sub("\n     davon (\S+):( +)(    )(\S+)(        )",  "\n  \\1\\2           \\4           ",text6,99999)
            text6 = re.sub("\n      davon (\S+):( +)(    )(\S+)(        )", "\n      \\1\\2             \\4      ",text6,99999)
            text6 = re.sub("\n       davon (\S+):( +)(    )(\S+)(        )", "\n          davon \\1\\2         \\4 ",text6,99999)
            text6 = re.sub("\n        davon (\S+):( +)(    )(\S+)(           )", "\n              (\\1)\\2              \\4",text6,99999)

            text6 = re.sub(r" (\-?\d+\.\d\d)","-\\1",text6,999999)  #  Minuszeichen
            text6 = re.sub(r" (\-?\d+) ","-\\1 ",text6,999999)  #  Minuszeichen
            text6 = re.sub(r" (\-?\d+)\n","-\\1\n",text6,999999)  #  Minuszeichen
            text6 = re.sub(r" --","   ",text6,999999)
            text6 = re.sub(r" (-0)( |\n)","  0\\2",text6,999999)  #  Minuszeichen
            
            ges0 = 0.00
            for unterkonten in ( ["Einnahmen","spende","einnahme","zuschuss","spende","mitgliedsbeitrag","mitgliedsbeitrag"],
                                 ["Ausgaben ","honorar","beitrag","bestand","werbung","ausgaben","notar","webhosting","kontogebuehr"] ):

                konten = {}
                for zeile in text6.split("\n"):
                    m = re.search(r"^ +([a-z]+|[a-z]+\-[a-z]+) +(\-?\d+\.\d\d) ",zeile)
                    if not m:
                        continue
                    if not m.group(1) in unterkonten:
                        continue
                    if not m.group(1) in konten:
                        konten[m.group(1)] = 0.00
                    konten[m.group(1)] = konten[m.group(1)] + float(m.group(2))
                kontenlist = list(konten.keys())
                kontenlist.sort()
                gesamt = 0.00
                text1 = text1 + "          " +  unterkonten[0] +" (nachrichtlich):                    ---XXX---\n\n"
                for kto in kontenlist:
                    gesamt = gesamt + konten[kto]
                    text1 = text1 + "                  " + kto + (" "*(20-len(kto))) + ("%13.2f" % konten[kto]) + "\n"
                text1 = re.sub(r"---XXX---","%13.2f" % gesamt,text1)
                ges0 = ges0 + gesamt
                text1 = text1 + "\n"
            text1 = text1[:-2] + "     " +  ("%13.2f" % ges0) + "  Ueberschuss\n"

            text3 = ""
            text0 = text0.split("\n")
            for zeile in text1.split("\n"):
                try:
                    zeile0 = text0.pop(0) + (" "*200)
                except:
                    zeile0 = (" "*200)
                text3 = text3 + zeile0[0:80] + zeile + "\n"

            text1 = text5 + text3 + "\f\n" + text6
            
            text1 = re.sub(r"AUFWAND ","PROJEKTE",text1)
            text1 = re.sub(r"(BILANZ [^\n]+?) *\n","\\1                                                 "+text_monate+"\n",text1)
            text1 = re.sub(r"(=====================[^\n]+?) *\n","\\1                                                     "+("-"*len(text_monate))[0:-4]+"\n",text1)
 

        file = jahr + "_bilanz_"+bez+"__20" + jahr
        open(file + ".md","w").write(text1)
        
#--------------  E-BILANZ: ----------------

#        text2 = {}
        text4    = ""
        faktor   = 1.0
        thisyear = 0.00
        lastyear = 0.00
        for zeile in text1.split("\n"):
            if "AKTIVA" in zeile:
                faktor = 1.0
            elif "PASSIVA" in zeile:
                faktor = -1.0
            elif "ERTRAG" in zeile:
                faktor = -1.0
            elif "AUFWAND" in zeile:
                faktor = 1.0
            elif "ABSCHLUSS" in zeile:
                faktor = 1.0
            m1 = re.search(r"  (\d+) (.*?) (\-?\d+\.\d\d)",zeile)
#            if not m1:
#                m1 = re.search(r"(ERTRAG|AUxxFWAND) +(\-?\d+\.\d\d)",zeile)
#                if m1:
#                    text4 = text4 + {"ERTRAG":"8001","AUFWAND":"8002"}[m1.group(1)] + ";" + ("%3.2f"%(abs(faktor*float(m1.group(2))))) + ";\"" + m1.group(1).strip() + "\"\n"
#                m1 = re.search(r"(ERxxTRAG|AUFWAND|D[ba]a: .*) +(\-?\d+\.\d\d)",zeile)
#                if m1:
#                    aufwand = aufwand + float(m1.group(2))
#                continue
            if m1:
                text4 = text4 + m1.group(1) + ";" + ("%3.2f"%(faktor*float(m1.group(3)))) + ";\"" + m1.group(2).strip() + "\"\n"
                if m1.group(1) == "2080":
                    thisyear = thisyear + float(m1.group(3))
                if m1.group(1) == "2900":
                    thisyear = thisyear + float(m1.group(3))
                    lastyear = lastyear + float(m1.group(3))
            else:
                m = re.search(r"^ +davon (\d\d)\: +(\-?\d+\.\d\d)",zeile)
                if m:
                    lastyear = -thisyear + float(m.group(2))
                
        text4 = text4 + "2085;" + ("%3.2f"%lastyear)  + ";\"Beginn Periode\"\n"
        text4 = text4 + "2087;" + ("%3.2f"%-thisyear) + ";\"Ende Periode\"\n"

#            kto  = m1.group(1)
#            kto2 = kto
#            m    = re.search(kto+"\;(.*?)\;",self.taxo)
#            if m:
#                kto2 = m.group(1)
#
#            kto3 = kto2
#            if kto3.startswith("-"):
#                kto3 = kto
#            kto3 = re.sub(r"^\+(.*?)\+","",kto3)
#            if not kto3 in text2:
#                text2[kto3] = 0.00
#            text2[kto3] = text2[kto3] + float(m1.group(3))
#            text4 = text4 + kto + "  " + ("%13.2f" % float(m1.group(3))) + "  " + kto2 + "  " + m1.group(2).strip() + "\n"
#            
#        text3 = ""
#        text2_key = list(text2.keys())
#        text2_key.sort()
#        for kto in text2_key:
#            text3 = text3 + kto + "=[" + ("%3.2f" % text2[kto]) + "]\n"
#
#        open("i" + file + ".ini","w").write(text3)

        open("j" + file + ".csv","w").write(text4)
        open("actual.csv","w").write(text4)
            
#------------------------------------------
        file = "anlagen_einnahmen_ausgaben_umsatz_vorsteuer_"+bez+"__20" + jahr

        text1 = ( "Anlagen, Einnahmen, Ausgaben, Umsatz- und Vorsteuer zu " + name + " 20" +jahr + ":\n" +
                  ("=" * len("Anlagen, Einnahmen, Ausgaben, Umsatz- und Vorsteuer zu " + name + " 20" +jahr + ":")) + "\n\n"
                  "ANLAGEN:\n=======\n\n" + anlagen + "\n\n\n" + 
                  "EINNAHMEN:\n=========\n\n" + einnahmen + "\n\n\n" + 
                  "AUSGABEN:\n========\n\n" + ausgaben + "\n\n\n" + 
                  "UMSATZ- UND VORSTEUER:\n======================\n\n" + ust )
        open(file + ".md","w").write(text1)


#**********************************************************************************************


    def xxtaxo_2022_02 (self):
    
        return('''    
0100;bs.ass.fixAss.intan.concessionBrands;P;entgeltlich erworbene Konzessionen, gewerbliche Schutzrechte und ähnliche Rechte und Werte sowie Lizenzen an solchen Rechten und Werten;Entgeltlich erworbene Konzessionen, gewerbliche Schutzrechte und ähnliche Rechte und Werte sowie Lizenzen an solchen Rechten und Werten Konzessionen Gewerbliche Schutzrechte Ähnliche Rechte und Werte EDV-Software Lizenzen an gewerblichen Schutzrechten und ähnlichen Rechten und Werten
0143;bs.ass.fixAss.intan.selfmade;P;Selbst geschaffene gewerbliche Schutzrechte und ähnliche Rechte und Werte;Selbst geschaffene immaterielle Vermögensgegenstände EDV-Software
0148;bs.ass.fixAss.intan.development;P;Immaterielle Vermögensgegenstände, in der Entwicklung befindliche immaterielle Vermögensgegenstände;Immaterielle Vermögensgegenstände in Entwicklung
0150;bs.ass.fixAss.intan.goodwill;P;Geschäfts-, Firmenoder Praxiswert;Geschäftsoder Firmenwert
0170;bs.ass.fixAss.intan.advPaym;P;Immaterielle Vermögensgegenstände, geleistete Anzahlungen;Geleistete Anzahlungen auf immaterielle Vermögensgegenstände Anzahlungen auf Geschäftsoder Firmenwert
0200;---xxx---;A;Grundstücke, grundstücksgleiche der Rechte und Bauten einschließlich der Bauten auf fremden Grundstücken, nicht zuordenbar;Grundstücke, grundstücksgleiche Rechte und Bauten einschließlich der Bauten auf fremden Grundstücken
0210;bs.ass.fixAss.tan.landBuildings.rightEquivalentToLandWithoutBuildings;P;Grundstücke, grundstücksgleiche Rechte und Bauten einschließlich der Bauten auf fremden Grundstücken, grundstücksgleiche Rechte ohne Bauten;Grundstücksgleiche Rechte ohne Bauten
0215;bs.ass.fixAss.tan.landBuildings.landWithoutBuildings;P;Grundstücke, grundstücksgleiche Rechte und Bauten einschließlich der Bauten auf fremden Grundstücken, unbebaute Grundstücke;Unbebaute Grundstücke
0220;bs.ass.fixAss.tan.landBuildings.rightEquivalentToLandWithoutBuildings;P;Grundstücke, grundstücksgleiche Rechte und Bauten einschließlich der Bauten auf fremden Grundstücken, grundstücksgleiche Rechte ohne Bauten;Grundstücksgleiche Rechte (Erbbaurecht, Dauerwohnrecht, unbebaute Grundstücke)
0225;bs.ass.fixAss.tan.landBuildings.landWithoutBuildings;P;Grundstücke, grundstücksgleiche Rechte und Bauten einschließlich der Bauten auf fremden Grundstücken, unbebaute Grundstücke;Grundstücke mit Substanzverzehr
0230;bs.ass.fixAss.tan.landBuildings.buildingsOnOwnLand.buildings;P;Grundstücke, grundstücksgleiche Rechte und Bauten einschließlich der Bauten auf fremden Grundstücken, Bauten auf eigenen Grundstücken und grundstücksgleichen Rechten, Gebäude-Anteil;Bauten auf eigenen Grundstücken und grundstücksgleichen Rechten
0235;bs.ass.fixAss.tan.landBuildings.buildingsOnOwnLand.land;P;Grundstücke, grundstücksgleiche Rechte und Bauten einschließlich der Bauten auf fremden Grundstücken, Bauten auf eigenen Grundstücken und grundstücksgleichen Rechten, Grund und Boden-Anteil;Grundstückswerte eigener bebauter Grundstücke
0240;bs.ass.fixAss.tan.landBuildings.buildingsOnOwnLand.buildings;P;Grundstücke, grundstücksgleiche Rechte und Bauten einschließlich der Bauten auf fremden Grundstücken, Bauten auf eigenen Grundstücken und grundstücksgleichen Rechten, Gebäude-Anteil;Geschäftsbauten Fabrikbauten
0260;bs.ass.fixAss.tan.landBuildings.buildingsOnOwnLand.misc;A;Grundstücke, grundstücksgleiche Rechte und Bauten einschließlich der Bauten auf fremden Grundstücken, Bauten auf eigenen Grundstücken und grundstücksgleichen Rechten, Grund und Boden-Anteil bzw. Gebäude-Anteil nicht zuordenbar;Andere Bauten
0270;bs.ass.fixAss.tan.landBuildings.buildingsOnOwnLand.buildings;P;Grundstücke, grundstücksgleiche Rechte und Bauten einschließlich der Bauten auf fremden Grundstücken, Bauten auf eigenen Grundstücken und grundstücksgleichen Rechten, Gebäude-Anteil;Garagen
0280;bs.ass.fixAss.tan.landBuildings.buildingsOnOwnLand.misc;A;Grundstücke, grundstücksgleiche Rechte und Bauten einschließlich der Bauten auf fremden Grundstücken, Bauten auf eigenen Grundstücken und grundstücksgleichen Rechten, Grund und Boden-Anteil bzw. Gebäude-Anteil nicht zuordenbar;Außenanlagen für Geschäfts-, Fabrikund andere Bauten Hofund Wegebefestigungen
0290;bs.ass.fixAss.tan.landBuildings.buildingsOnOwnLand.buildings;P;Grundstücke, grundstücksgleiche Rechte und Bauten einschließlich der Bauten auf fremden Grundstücken, Bauten auf eigenen Grundstücken und grundstücksgleichen Rechten, Gebäude-Anteil;Einrichtungen für Geschäfts-, Fabrikund andere Bauten Wohnbauten Garagen
0310;bs.ass.fixAss.tan.landBuildings.buildingsOnOwnLand.misc;A;Grundstücke, grundstücksgleiche Rechte und Bauten einschließlich der Bauten auf fremden Grundstücken, Bauten auf eigenen Grundstücken und grundstücksgleichen Rechten, Grund und Boden-Anteil bzw. Gebäude-Anteil nicht zuordenbar;Außenanlagen Hofund Wegebefestigungen
0320;bs.ass.fixAss.tan.landBuildings.buildingsOnOwnLand.buildings;P;Grundstücke, grundstücksgleiche Rechte und Bauten einschließlich der Bauten auf fremden Grundstücken, Bauten auf eigenen Grundstücken und grundstücksgleichen Rechten, Gebäude-Anteil;Einrichtungen für Wohnbauten
0330;bs.ass.fixAss.tan.landBuildings.buildingsOnNonOwnedLand;P;Grundstücke, grundstücksgleiche Rechte und Bauten einschließlich der Bauten auf fremden Grundstücken, Bauten auf fremden Grundstücken;Bauten auf fremden Grundstücken Geschäftsbauten Fabrikbauten Wohnbauten Andere Bauten Garagen Außenanlagen Hofund Wegebefestigungen Einrichtungen für Geschäfts-, Fabrik-, Wohnund andere Bauten
0400;bs.ass.fixAss.tan.machinery;P;technische Anlagen und Maschinen;Technische Anlagen und Maschinen Technische Anlagen Maschinen Transportanlagen und Ähnliches Maschinengebundene Werkzeuge Betriebsvorrichtungen
0500;bs.ass.fixAss.tan.otherEquipm.misc;A;andere Anlagen, Betriebsund Geschäftsausstattung, nicht zuordenbar;Andere Anlagen, Betriebsund Geschäftsausstattung
0510;bs.ass.fixAss.tan.otherEquipm.other;P;andere Anlagen, Betriebsund Geschäftsausstattung, andere Anlagen;Andere Anlagen
0520;bs.ass.fixAss.tan.otherEquipm.passengerCars;P;andere Anlagen, Betriebsund Geschäftsausstattung, PKW;Pkw
0540;bs.ass.fixAss.tan.otherEquipm.comVehicle;P;andere Anlagen, Betriebsund Geschäftsausstattung, LKW;Lkw
0560;bs.ass.fixAss.tan.otherEquipm.otherTransportMeans;P;andere Anlagen, Betriebsund Geschäftsausstattung, sonstige Transportmittel;Sonstige Transportmittel
0620;bs.ass.fixAss.tan.otherEquipm.factory;P;andere Anlagen, Betriebsund Geschäftsausstattung, Betriebsausstattung;Werkzeuge Betriebsausstattung
0635;bs.ass.fixAss.tan.otherEquipm.office;P;andere Anlagen, Betriebsund Geschäftsausstattung, Geschäftsausstattung;Geschäftsausstattung Ladeneinrichtung Büroeinrichtung
0660;bs.ass.fixAss.tan.otherEquipm.factory;P;andere Anlagen, Betriebsund Geschäftsausstattung, Betriebsausstattung;Gerüstund Schalungsmaterial
0670;bs.ass.fixAss.tan.otherEquipm.gwg;P;andere Anlagen, Betriebsund Geschäftsausstattung, GWG;Geringwertige Wirtschaftsgüter
0675;bs.ass.fixAss.tan.otherEquipm.gwgsammelposten;P;andere Anlagen, Betriebsund Geschäftsausstattung, Sammelposten GWG;Wirtschaftsgüter (Sammelposten)
0680;bs.ass.fixAss.tan.otherEquipm.otherbga;P;andere Anlagen, Betriebsund Geschäftsausstattung, Sonstige Betriebsund Geschäftsausstattung;Einbauten in fremde Grundstücke Sonstige Betriebsund Geschäftsausstattung
0700;bs.ass.fixAss.tan.inConstrAdvPaym;P;geleistete Anzahlungen und Anlagen im Bau;Geleistete Anzahlungen und Anlagen im Bau Anzahlungen auf Grund und Boden Geschäfts-, Fabrikund andere Bauten im Bau auf eigenen Grundstücken Anzahlungen auf Geschäfts-, Fabrikund andere Bauten auf eigenen Grundstücken Wohnbauten im Bau auf eigenen Grundstücken Anzahlungen auf Wohnbauten auf eigenen Grundstücken Geschäfts-, Fabrikund andere Bauten im Bau auf fremden Grundstücken Anzahlungen auf Geschäfts-, Fabrikund andere Bauten auf fremden Grundstücken Wohnbauten im Bau auf fremden Grundstücken Anzahlungen auf Wohnbauten auf fremden Grundstücken Technische Anlagen und Maschinen im Bau Anzahlungen auf technische Anlagen und Maschinen Andere Anlagen, Betriebsund Geschäftsausstattung im Bau Anzahlungen auf andere Anlagen, Betriebsund Geschäftsausstattung
0800;bs.ass.fixAss.fin.sharesInAffil.other;A;Anteile an verbundenen Unternehmen, nach Rechtsform nicht zuordenbar;Anteile an verbundenen Unternehmen (Anlagevermögen)
0803;bs.ass.fixAss.fin.sharesInAffil.partnerships.commPart.other;P;Anteile an verbundenen Unternehmen, Anteile an Personengesellschaften, Anteile an Mitunternehmerschaften, Beteiligung an sonstigen Mitunternehmerschaften;Anteile an verbundenen Unternehmen, Personengesellschaften
0804;bs.ass.fixAss.fin.sharesInAffil.corporations;P;Anteile an verbundenen Unternehmen, Anteile an Kapitalgesellschaften;Anteile an verbundenen Unternehmen, Kapitalgesellschaften
0805;bs.ass.fixAss.fin.sharesInAffil.partnerships.commPart.other;P;Anteile an verbundenen Unternehmen, Anteile an Personengesellschaften, Anteile an Mitunternehmerschaften, Beteiligung an sonstigen Mitunternehmerschaften;Anteile an herrschender oder mehrheitlich beteiligter Gesellschaft, Personengesellschaften
0808;bs.ass.fixAss.fin.sharesInAffil.corporations;P;Anteile an verbundenen Unternehmen, Anteile an Kapitalgesellschaften;Anteile an herrschender oder mehrheitlich beteiligter Gesellschaft, Kapitalgesellschaften
0809;bs.ass.fixAss.fin.sharesInAffil.other;A;Anteile an verbundenen Unternehmen, nach Rechtsform nicht zuordenbar;Anteile an herrschender oder mit Mehrheit beteiligter Gesellschaft
0810;bs.ass.fixAss.fin.loansToAffil.other;A;Ausleihungen an verbundene Unternehmen, nach Rechtsform nicht zuordenbar;Ausleihungen an verbundene Unternehmen
0813;bs.ass.fixAss.fin.loansToAffil.partnerships.other;P;Ausleihungen an verbundene Unternehmen, soweit Personengesellschaften, sonstige Ausleihungen;Ausleihungen an verbundene Unternehmen, Personengesellschaften
0814;bs.ass.fixAss.fin.loansToAffil.corporations;P;Ausleihungen an verbundene Unternehmen, soweit Kapitalgesellschaften;Ausleihungen an verbundene Unternehmen, Kapitalgesellschaften
0815;bs.ass.fixAss.fin.loansToAffil.soleProprietor;P;Ausleihungen an verbundene Unternehmen, soweit Einzelunternehmen;Ausleihungen an verbundene Unternehmen, Einzelunternehmen
0820;bs.ass.fixAss.fin.particip.other;A;Beteiligungen, sonstige Beteiligungen, nach Rechtsform nicht zuordenbar;Beteiligungen Typisch stille Beteiligungen
0840;bs.ass.fixAss.fin.particip.partnerships.commPart.silentAtyp;P;Beteiligungen, Beteiligungen an Personengesellschaften, Anteile an Mitunternehmerschaften, atypisch stille Beteiligung;Atypisch stille Beteiligungen
0850;bs.ass.fixAss.fin.particip.corporations;P;Beteiligungen, Beteiligungen an Kapitalgesellschaften;Beteiligungen an Kapitalgesellschaften
0860;bs.ass.fixAss.fin.particip.partnerships.commPart.other;P;Beteiligungen, Beteiligungen an Personengesellschaften, Anteile an Mitunternehmerschaften, Beteiligung an sonstigen Mitunternehmerschaften;Beteiligungen an Personengesellschaften
0880;bs.ass.fixAss.fin.loansToParticip.other;A;Ausleihungen an Unternehmen, mit denen ein Beteiligungsverhältnis besteht, nicht nach Rechtsform zuordenbar;Ausleihungen an Unternehmen, mit denen ein Beteiligungsverhältnis besteht
0883;bs.ass.fixAss.fin.loansToParticip.partnerships.other;P;Ausleihungen an Unternehmen, mit denen ein Beteiligungsverhältnis besteht, Ausleihungen an Personengesellschaften, sonstige Ausleihungen;Ausleihungen an Unternehmen, mit denen ein Beteiligungsverhältnis besteht, Personengesellschaften
0885;bs.ass.fixAss.fin.loansToParticip.corporations;P;Ausleihungen an Unternehmen, mit denen ein Beteiligungsverhältnis besteht, Ausleihungen an Kapitalgesellschaften;Ausleihungen an Unternehmen, mit denen ein Beteiligungsverhältnis besteht, Kapitalgesellschaften
0900;bs.ass.fixAss.fin.securities;P;Wertpapiere des Anlagevermögens;Wertpapiere des Anlagevermögens Wertpapiere mit Gewinnbeteiligungsansprüchen, die dem Teileinkünfteverfahren unterliegen Festverzinsliche Wertpapiere
0930;bs.ass.fixAss.fin.otherLoans.other;P;Sonstige Ausleihungen, übrige sonstige Ausleihungen;Übrige sonstige Ausleihungen Darlehen
0960;bs.ass.fixAss.fin.loansToSharehold.misc;A;Ausleihungen an Gesellschafter, nicht nach Rechtsform des Gesellschafters zuordenbar;Ausleihungen an Gesellschafter
0961;---xxx---;P;Ausleihungen an Gesellschafter, Ausleihungen an GmbH-Gesellschafter Ausleihungen an Gesellschafter, nicht nach Rechtsform des Gesellschafters zuordenbar;Ausleihungen an GmbH-Gesellschafter
0970;bs.ass.fixAss.fin.otherLoans.other;P;Sonstige Ausleihungen, übrige sonstige Ausleihungen;Ausleihungen an nahe stehende Personen
0980;bs.ass.fixAss.fin.otherFinAss.coopShares;P;Sonstige Finanzanlagen, Genossenschaftsanteile (langfristiger Verbleib);Genossenschaftsanteile zum langfristigen Verbleib
0990;bs.ass.fixAss.fin.otherFinAss.reInsurClaim;P;Sonstige Finanzanlagen, Rückdeckungsansprüche aus Lebensversicherungen (langfristiger Verbleib);Rückdeckungsansprüche aus Lebensversicherungen zum langfristigen Verbleib
1000;bs.ass.currAss.inventory.material;P;Roh-, Hilfsund Betriebsstoffe;Roh-, Hilfsund Betriebsstoffe (Bestand)
1040;bs.ass.currAss.inventory.inProgress;P;unfertige Erzeugnisse, unfertige Leistungen;Unfertige Erzeugnisse, unfertige Leistungen (Bestand) Unfertige Erzeugnisse (Bestand) Unfertige Leistungen (Bestand) In Ausführung befindliche Bauaufträge In Arbeit befindliche Aufträge
1100;bs.ass.currAss.inventory.finishedAndMerch;P;fertige Erzeugnisse und Waren;Fertige Erzeugnisse und Waren (Bestand) Fertige Erzeugnisse (Bestand) Waren (Bestand)
1180;bs.ass.currAss.inventory.advPaymPaid;P;Vorräte, geleistete Anzahlungen;Geleistete Anzahlungen auf Vorräte Geleistete Anzahlungen 7 % Vorsteuer Geleistete Anzahlungen 5 % Vorsteuer Geleistete Anzahlungen 16 % Vorsteuer Geleistete Anzahlungen 19 % Vorsteuer
1190;bs.ass.currAss.inventory.advPaymReceived;P;Vorräte, erhaltene Anzahlungen auf Bestellungen (offen aktivisch abgesetzt);Erhaltene Anzahlungen auf Bestellungen (von Vorräten offen abgesetzt)
1200;bs.ass.currAss.receiv.trade.other;P;Forderungen aus Lieferungen und Leistungen, übrige Forderungen;Forderungen aus Lieferungen und Leistungen Forderungen aus Lieferungen und Leistungen ohne Kontokorrent Forderungen aus Lieferungen und Leistungen ohne Kontokorrent Restlaufzeit bis 1 Jahr Forderungen aus Lieferungen und Leistungen ohne Kontokorrent Restlaufzeit größer 1 Jahr Wechsel aus Lieferungen und Leistungen Wechsel aus Lieferungen und Leistungen Restlaufzeit bis 1 Jahr Wechsel aus Lieferungen und Leistungen Restlaufzeit größer 1 Jahr Wechsel aus Lieferungen und Leistungen, bundesbankfähig Zweifelhafte Forderungen Zweifelhafte Forderungen Restlaufzeit bis 1 Jahr Zweifelhafte Forderungen Restlaufzeit größer 1 Jahr Einzelwertberichtigungen auf Forderungen Restlaufzeit bis 1 Jahr Einzelwertberichtigungen auf Forderungen Restlaufzeit größer 1 Jahr Pauschalwertberichtigung auf Forderungen Restlaufzeit bis 1 Jahr Pauschalwertberichtigung auf Forderungen Restlaufzeit größer 1 Jahr
1210;+1200+bs.ass.currAss.receiv.trade.other;P;Forderungen aus Lieferungen und Leistungen, übrige Forderungen;Forderungen aus Lieferungen und Leistungen Forderungen aus Lieferungen und Leistungen ohne Kontokorrent Forderungen aus Lieferungen und Leistungen ohne Kontokorrent Restlaufzeit bis 1 Jahr Forderungen aus Lieferungen und Leistungen ohne Kontokorrent Restlaufzeit größer 1 Jahr Wechsel aus Lieferungen und Leistungen Wechsel aus Lieferungen und Leistungen Restlaufzeit bis 1 Jahr Wechsel aus Lieferungen und Leistungen Restlaufzeit größer 1 Jahr Wechsel aus Lieferungen und Leistungen, bundesbankfähig Zweifelhafte Forderungen Zweifelhafte Forderungen Restlaufzeit bis 1 Jahr Zweifelhafte Forderungen Restlaufzeit größer 1 Jahr Einzelwertberichtigungen auf Forderungen Restlaufzeit bis 1 Jahr Einzelwertberichtigungen auf Forderungen Restlaufzeit größer 1 Jahr Pauschalwertberichtigung auf Forderungen Restlaufzeit bis 1 Jahr Pauschalwertberichtigung auf Forderungen Restlaufzeit größer 1 Jahr
1250;bs.ass.currAss.receiv.shareholders.misc;A;Forderungen und sonstige Vermögensgegenstände, Forderungen gegen Gesellschafter, Forderungen gegen Gesellschafter, nach Rechtsform des Gesellschafters nicht zuordenbar;Forderungen aus Lieferungen und Leistungen gegen Gesellschafter
1258;bs.ass.currAss.receiv.trade.other;P;Forderungen aus Lieferungen und Leistungen, übrige Forderungen;Gegenkonto zu sonstigen Vermögensgegenständen bei Buchungen über Debitorenkonto Gegenkonto 1221-1229,12401245,1250-1257,1270-1279,12901297 bei Aufteilung Debitorenkonto
1260;bs.ass.currAss.receiv.affil;P;Forderungen gegen verbundene Unternehmen;Forderungen gegen verbundene Unternehmen Forderungen gegen verbundene Unternehmen Restlaufzeit bis 1 Jahr Forderungen gegen verbundene Unternehmen Restlaufzeit größer 1 Jahr Besitzwechsel gegen verbundene Unternehmen Besitzwechsel gegen verbundene Unternehmen Restlaufzeit bis 1 Jahr Besitzwechsel gegen verbundene Unternehmen Restlaufzeit größer 1 Jahr Besitzwechsel gegen verbundene Unternehmen, bundesbankfähig Forderungen aus Lieferungen und Leistungen gegen verbundene Unternehmen Forderungen aus Lieferungen und Leistungen gegen verbundene Unternehmen Restlaufzeit bis 1 Jahr Forderungen aus Lieferungen und Leistungen gegen verbundene Unternehmen Restlaufzeit größer 1 Jahr Wertberichtigungen auf Forderungen gegen verbundene Unternehmen Restlaufzeit bis 1 Jahr Wertberichtigungen auf Forderungen gegen verbundene Unternehmen Restlaufzeit größer 1 Jahr
1280;bs.ass.currAss.receiv.particip;P;Forderungen gegen Unternehmen, mit denen ein Beteiligungsverhältnis besteht;Forderungen gegen Unternehmen, mit denen ein Beteiligungsverhältnis besteht Forderungen gegen Unternehmen, mit denen ein Beteiligungsverhältnis besteht Restlaufzeit bis 1 Jahr Forderungen gegen Unternehmen, mit denen ein Beteiligungsverhältnis besteht Restlaufzeit größer 1 Jahr Besitzwechsel gegen Unternehmen, mit denen ein Beteiligungsverhältnis besteht Besitzwechsel gegen Unternehmen, mit denen ein Beteiligungsverhältnis besteht Restlaufzeit bis 1 Jahr Besitzwechsel gegen Unternehmen, mit denen ein Beteiligungsverhältnis besteht Restlaufzeit größer 1 Jahr Besitzwechsel gegen Unternehmen, mit denen ein Beteiligungsverhältnis besteht, bundesbankfähig
1298;bs.ass.currAss.receiv.other.unpaidCapital;P;Forderungen und sonstige Vermögensgegenstände, eingeforderte noch ausstehende Kapitaleinlagen;Ausstehende Einlagen auf das gezeichnete Kapital, eingefordert (Forderungen, nicht eingeforderte ausstehende Einlagen s. Konto 2910)
1299;bs.ass.currAss.receiv.other.unpaidSupplementaryCalls;P;Forderungen und sonstige Vermögensgegenstände, eingeforderte Nachschüsse;Nachschüsse (Forderungen, Gegenkonto 2929)
1300;bs.ass.currAss.receiv.other.misc;A;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, nicht zuordenbar;Sonstige Vermögensgegenstände Sonstige Vermögensgegenstände Restlaufzeit bis 1 Jahr Sonstige Vermögensgegenstände Restlaufzeit größer 1 Jahr
1307;bs.ass.currAss.receiv.shareholders.gmbh;P;Forderungen und sonstige Vermögensgegenstände, Forderungen gegen Gesellschafter, Forderungen gegen GmbH-Gesellschafter;Forderungen gegen GmbH-Gesellschafter Forderungen gegen GmbH-Gesellschafter Restlaufzeit bis 1 Jahr Forderungen gegen GmbH-Gesellschafter Restlaufzeit größer 1 Jahr
1310;---xxx---;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, Forderungen und Darlehen an Organmitglieder Forderungen und sonstige Vermögensgegenstände, Forderungen gegen Gesellschafter, Forderungen gegen sonstige Gesellschafter r;Forderungen gegen Vorstandsmitglieder und Geschäftsführer Forderungen gegen Vorstandsmitglieder und Geschäftsführer Restlaufzeit bis 1 Jahr Forderungen gegen Vorstandsmitglieder und Geschäftsführer Restlaufzeit größer 1 Jahr Forderungen gegen Aufsichtsratsund Beiratsmitglieder Forderungen gegen Aufsichtsratsund Beiratsmitglieder Restlaufzeit bis 1 Jahr Forderungen gegen Aufsichtsratsund Beiratsmitglieder Restlaufzeit größer 1 Jahr Forderungen gegen sonstige Gesellschafter Forderungen gegen sonstige Gesellschafter Restlaufzeit bis 1 Jahr
1337;bs.ass.currAss.receiv.other.other;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, übrige sonstige Vermögensgegenstände;Forderungen gegen typisch stille Gesellschafter Forderungen gegen typisch stille Gesellschafter Restlaufzeit bis 1 Jahr Forderungen gegen typisch stille Gesellschafter Restlaufzeit größer 1 Jahr
1340;bs.ass.currAss.receiv.other.employees;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, Forderungen und Darlehen an Mitarbeiter;Forderungen gegen Personal aus Lohnund Gehaltsabrechnung Forderungen gegen Personal aus Lohnund Gehaltsabrechnung Restlaufzeit bis 1 Jahr Forderungen gegen Personal aus Lohnund Gehaltsabrechnung Restlaufzeit größer 1 Jahr Ansprüche aus betrieblicher Altersversorgung und Pensionsansprüche (Mitunternehmer)28)
1350;bs.ass.currAss.receiv.other.other;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, übrige sonstige Vermögensgegenstände;Kautionen Kautionen Restlaufzeit bis 1 Jahr Kautionen Restlaufzeit größer 1 Jahr Darlehen Darlehen Restlaufzeit bis 1 Jahr Darlehen Restlaufzeit größer 1 Jahr
1355;bs.ass.currAss.receiv.other.other;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, übrige sonstige Vermögensgegenstände;Kautionen Kautionen Restlaufzeit bis 1 Jahr Kautionen Restlaufzeit größer 1 Jahr Darlehen Darlehen Restlaufzeit bis 1 Jahr Darlehen Restlaufzeit größer 1 Jahr
1361;+1369+bs.ass.currAss.receiv.other.socInsur;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, Forderungen gegen Sozialversicherungsträger;Forderungen gegenüber Krankenkassen aus Aufwendungsausgleichsgesetz
1369;bs.ass.currAss.receiv.other.socInsur;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, Forderungen gegen Sozialversicherungsträger;Forderungen gegenüber Krankenkassen aus Aufwendungsausgleichsgesetz
1370;bs.ass.currAss.receiv.other.other;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, übrige sonstige Vermögensgegenstände;Durchlaufende Posten Fremdgeld Agenturwarenabrechnung
1376;bs.ass.currAss.receiv.other.vat;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, Umsatzsteuerforderungen;Nachträglich abziehbare Vorsteuer nach § 15a Abs. 2 UStG Zurückzuzahlende Vorsteuer nach § 15a Abs. 2 UStG
1378;bs.ass.currAss.receiv.other.reInsurClaim;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, Rückdeckungsansprüche aus Lebensversicherungen (kurzfristiger Verbleib);Ansprüche aus Rückdeckungsversicherungen
1380;bs.ass.currAss.receiv.other.other;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, übrige sonstige Vermögensgegenstände;Vermögensgegenstände zur Erfüllung von Pensionsrückstellungen und ähnlichen Verpflichtungen zum langfristigen Verbleib
1381;---xxx---;P;Aktiver Unterschiedsbetrag aus der Vermögensverrechnung r-;Vermögensgegenstände zur Saldierung mit Pensionsrückstellungen und ähnlichen Verpflichtungen zum langfristigen Verbleib nach § 246 Abs. 2 HGB
1382;bs.ass.currAss.receiv.other.other;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, übrige sonstige Vermögensgegenstände;Vermögensgegenstände zur Erfüllung von mit der Altersversorgung vergleichbaren langfristigen Verpflichtungen
1383;bs.ass.SurplusFromOffsetting;P;Aktiver Unterschiedsbetrag aus der Vermögensverrechnung;Vermögensgegenstände zur Saldierung mit der Altersversorgung vergleichbaren langfristigen Verpflichtungen nach § 246 Abs. 2 HGB
1390;bs.ass.currAss.receiv.other.other;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, übrige sonstige Vermögensgegenstände;GmbH-Anteile zum kurzfristigen Verbleib
1391;bs.ass.currAss.receiv.other.jointWork;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, Forderungen gegen Arbeitsgemeinschaften;Forderungen gegen Arbeitsgemeinschaften
1393;bs.ass.currAss.receiv.other.profSharRights;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, Genussrechte;Genussrechte
1394;bs.ass.currAss.receiv.other.secondaryPaym;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, Einzahlungsansprüche zu Nebenleistungen oder Zuzahlungen;Einzahlungsansprüche zu Nebenleistungen oder Zuzahlungen
1395;bs.ass.currAss.receiv.other.coopShares;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, Genossenschaftsanteile (kurzfristiger Verbleib);Genossenschaftsanteile zum kurzfristigen Verbleib
1396;bs.ass.currAss.receiv.other.vat;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, Umsatzsteuerforderungen;Nachträglich abziehbare Vorsteuer nach § 15a Abs. 1 UStG, bewegliche Wirtschaftsgüter Zurückzuzahlende Vorsteuer nach § 15a Abs. 1 UStG, bewegliche Wirtschaftsgüter Nachträglich abziehbare Vorsteuer nach § 15a Abs. 1 UStG, unbewegliche Wirtschaftsgüter Zurückzuzahlende Vorsteuer nach § 15a Abs. 1 UStG, unbewegliche Wirtschaftsgüter Abziehbare Vorsteuer Abziehbare Vorsteuer 7 % Abziehbare Vorsteuer aus innergemeinschaftlichem Erwerb Abziehbare Vorsteuer 5 %11) Abziehbare Vorsteuer aus innergemeinschaftlichem Erwerb 19 % Abziehbare Vorsteuer 16 %11) Abziehbare Vorsteuer 19 % Abziehbare Vorsteuer nach § 13b UStG 19 % Abziehbare Vorsteuer nach § 13b UStG Abziehbare Vorsteuer nach § 13b UStG 16 %11) Aufzuteilende Vorsteuer Aufzuteilende Vorsteuer 7 % Aufzuteilende Vorsteuer aus innergemeinschaftlichem Erwerb Aufzuteilende Vorsteuer aus innergemeinschaftlichem Erwerb 19 % Aufzuteilende Vorsteuer 5 %11) Aufzuteilende Vorsteuer 16 %11) Aufzuteilende Vorsteuer 19 % Aufzuteilende Vorsteuer nach §§ 13a und 13b UStG Aufzuteilende Vorsteuer nach §§ 13a und 13b UStG 16 %11) Aufzuteilende Vorsteuer nach §§ 13a und 13b UStG 19 % Forderungen aus UmsatzsteuerVorauszahlungen Umsatzsteuerforderungen Vorjahr Umsatzsteuerforderungen frühere Jahre
1427;bs.ass.currAss.receiv.other.otherTaxRec;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, andere Forderungen gegen Finanzbehörden;Forderungen aus entrichteten Verbrauchsteuern
1431;bs.ass.currAss.receiv.other.vat;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, Umsatzsteuerforderungen;Abziehbare Vorsteuer aus der Auslagerung von Gegenständen aus einem Umsatzsteuerlager Abziehbare Vorsteuer aus innergemeinschaftlichem Erwerb von Neufahrzeugen von Lieferanten ohne Umsatzsteuer-Identifikationsnummer Entstandene Einfuhrumsatzsteuer Vorsteuer in Folgeperiode/im Folgejahr abziehbar
1435;bs.ass.currAss.receiv.other.tradeTaxOverpayment;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, Gewerbesteuerüberzahlungen;Forderungen aus Gewerbesteuerüberzahlungen
1436;bs.ass.currAss.receiv.other.vat;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, Umsatzsteuerforderungen;Vorsteuer aus Erwerb als letzter Abnehmer innerhalb eines Dreiecksgeschäfts
1440;bs.ass.currAss.receiv.other.other;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, übrige sonstige Vermögensgegenstände;Steuererstattungsansprüche gegenüber anderen Ländern
1450;bs.ass.currAss.receiv.other.corpTaxOverpayment;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, Körperschaftsteuerüberzahlungen;Körperschaftsteuerrückforderung
1456;bs.ass.currAss.receiv.other.otherTaxRec;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, andere Forderungen gegen Finanzbehörden;Forderungen an das Finanzamt aus abgeführtem Bauabzugsbetrag
1457;bs.ass.currAss.receiv.other.other;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, übrige sonstige Vermögensgegenstände;Forderungen gegenüber Bundesagentur für Arbeit Geldtransit
1484;bs.ass.currAss.receiv.other.vat;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, Umsatzsteuerforderungen;Vorsteuer nach allgemeinen Durchschnittssätzen UStVA Kz. 6311)
1490;bs.ass.currAss.receiv.other.other;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, übrige sonstige Vermögensgegenstände;Verrechnungskonto Ist-Versteuerung Forderungen gegen Gesellschaft/Gesamthand28)
1495;bs.eqLiab.liab.other.other;P;sonstige Verbindlichkeiten, übrige sonstige Verbindlichkeiten;Verrechnungskonto erhaltene Anzahlungen bei Buchung über Debitorenkonto
1498;bs.ass.currAss.receiv.other.other;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, übrige sonstige Vermögensgegenstände;Überleitungskonto Kostenstellen
1500;bs.ass.currAss.securities.affil;P;Anteile an verbundenen Unternehmen (Umlaufvermögen);Anteile an verbundenen Unternehmen (Umlaufvermögen) Anteile an herrschender oder mit Mehrheit beteiligter Gesellschaft
1510;bs.ass.currAss.securities.other;P;Wertpapiere des Umlaufvermögens, sonstige Wertpapiere des Umlaufvermögens;Sonstige Wertpapiere Finanzwechsel Andere Wertpapiere mit unwesentlichen Wertschwankungen Wertpapieranlagen im Rahmen der kurzfristigen Finanzdisposition
1600;++bs.ass.currAss.cashEquiv.cash;P;Kassenbestand, Bundesbankguthaben, Guthaben bei Kreditinstituten und Schecks; Guthaben bei Kreditinstituten;Bank Bank 1 Bank 2 Bank 3 Bank 4 Bank 5 Finanzmittelanlagen im Rahmen der kurzfristigen Finanzdisposition (nicht im Finanzmittelfonds enthalten)
1800;++bs.ass.currAss.cashEquiv.bank;P;Kassenbestand, Bundesbankguthaben, Guthaben bei Kreditinstituten und Schecks; Guthaben bei Kreditinstituten;Bank Bank 1 Bank 2 Bank 3 Bank 4 Bank 5 Finanzmittelanlagen im Rahmen der kurzfristigen Finanzdisposition (nicht im Finanzmittelfonds enthalten)
1801;+1800+bs.ass.currAss.cashEquiv.bank;P;Kassenbestand, Bundesbankguthaben, Guthaben bei Kreditinstituten und Schecks; Guthaben bei Kreditinstituten;Bank Bank 1 Bank 2 Bank 3 Bank 4 Bank 5 Finanzmittelanlagen im Rahmen der kurzfristigen Finanzdisposition (nicht im Finanzmittelfonds enthalten)
1802;+1800+bs.ass.currAss.cashEquiv.bank;P;Kassenbestand, Bundesbankguthaben, Guthaben bei Kreditinstituten und Schecks; Guthaben bei Kreditinstituten;Bank Bank 1 Bank 2 Bank 3 Bank 4 Bank 5 Finanzmittelanlagen im Rahmen der kurzfristigen Finanzdisposition (nicht im Finanzmittelfonds enthalten)
1803;+1800+bs.ass.currAss.cashEquiv.bank;P;Kassenbestand, Bundesbankguthaben, Guthaben bei Kreditinstituten und Schecks; Guthaben bei Kreditinstituten;Bank Bank 1 Bank 2 Bank 3 Bank 4 Bank 5 Finanzmittelanlagen im Rahmen der kurzfristigen Finanzdisposition (nicht im Finanzmittelfonds enthalten)
1804;+1800+bs.ass.currAss.cashEquiv.bank;P;Kassenbestand, Bundesbankguthaben, Guthaben bei Kreditinstituten und Schecks; Guthaben bei Kreditinstituten;Bank Bank 1 Bank 2 Bank 3 Bank 4 Bank 5 Finanzmittelanlagen im Rahmen der kurzfristigen Finanzdisposition (nicht im Finanzmittelfonds enthalten)
1805;+1800+bs.ass.currAss.cashEquiv.bank;P;Kassenbestand, Bundesbankguthaben, Guthaben bei Kreditinstituten und Schecks; Guthaben bei Kreditinstituten;Bank Bank 1 Bank 2 Bank 3 Bank 4 Bank 5 Finanzmittelanlagen im Rahmen der kurzfristigen Finanzdisposition (nicht im Finanzmittelfonds enthalten)
1806;+1800+bs.ass.currAss.cashEquiv.bank;P;Kassenbestand, Bundesbankguthaben, Guthaben bei Kreditinstituten und Schecks; Guthaben bei Kreditinstituten;Bank Bank 1 Bank 2 Bank 3 Bank 4 Bank 5 Finanzmittelanlagen im Rahmen der kurzfristigen Finanzdisposition (nicht im Finanzmittelfonds enthalten)
1807;+1800+bs.ass.currAss.cashEquiv.bank;P;Kassenbestand, Bundesbankguthaben, Guthaben bei Kreditinstituten und Schecks; Guthaben bei Kreditinstituten;Bank Bank 1 Bank 2 Bank 3 Bank 4 Bank 5 Finanzmittelanlagen im Rahmen der kurzfristigen Finanzdisposition (nicht im Finanzmittelfonds enthalten)
1808;+1800+bs.ass.currAss.cashEquiv.bank;P;Kassenbestand, Bundesbankguthaben, Guthaben bei Kreditinstituten und Schecks; Guthaben bei Kreditinstituten;Bank Bank 1 Bank 2 Bank 3 Bank 4 Bank 5 Finanzmittelanlagen im Rahmen der kurzfristigen Finanzdisposition (nicht im Finanzmittelfonds enthalten)
1890;++bs.ass.currAss.cashEquiv.other;P;Kassenbestand, Bundesbankguthaben, Guthaben bei Kreditinstituten und Schecks; Guthaben bei Kreditinstituten;Bank Bank 1 Bank 2 Bank 3 Bank 4 Bank 5 Finanzmittelanlagen im Rahmen der kurzfristigen Finanzdisposition (nicht im Finanzmittelfonds enthalten)
1550; Schecks;P;Kassenbestand, Bundesbankguthaben, Guthaben bei Kreditinstituten und Schecks; Schecks;Schecks
1600; Kasse;P;Kassenbestand, Bundesbankguthaben, Guthaben bei Kreditinstituten und Schecks; Kasse;Kasse
1700; Guthaben bei Kreditinstituten;P;Kassenbestand, Bundesbankguthaben, Guthaben bei Kreditinstituten und Schecks; Guthaben bei Kreditinstituten;Bank (Postbank) Bank (Postbank 1) Bank (Postbank 2) Bank (Postbank 3)
1780; Bundesbankguthaben;P;Kassenbestand, Bundesbankguthaben, Guthaben bei Kreditinstituten und Schecks; Bundesbankguthaben;LZB-Guthaben Bundesbankguthaben
1800; Guthaben bei Kreditinstituten;P;Kassenbestand, Bundesbankguthaben, Guthaben bei Kreditinstituten und Schecks; Guthaben bei Kreditinstituten;Bank Bank 1 Bank 2 Bank 3 Bank 4 Bank 5 Finanzmittelanlagen im Rahmen der kurzfristigen Finanzdisposition (nicht im Finanzmittelfonds enthalten)
1895;bs.eqLiab.liab.bank.other;P;Verbindlichkeiten gegenüber Kreditinstituten, übrige;Verbindlichkeiten gegenüber Kreditinstituten (nicht im Finanzmittelfonds enthalten)
1900;bs.ass.prepaidExp;P;Aktive Rechnungsabgrenzungsposten;Aktive Rechnungsabgrenzung Als Aufwand berücksichtigte Zölle und Verbrauchsteuern auf Vorräte Als Aufwand berücksichtigte Umsatzsteuer auf Anzahlungen Damnum/Disagio
1950;bs.ass.defTax;P;Aktive latente Steuern;Aktive latente Steuern
2900;bs.eqLiab.equity.subscribed.corp;P;Gezeichnetes Kapital / Kapitalkonto / Kapitalanteile, gezeichnetes Kapital (Kapitalgesellschaften);Gezeichnetes Kapital17) Kapitalerhöhung aus Gesellschaftsmitteln17)
2909;bs.eqLiab.equity.subscribed.ownSharesdeducted;P;Gezeichnetes Kapital / Kapitalkonto/ Kapitalanteile, Eigene Anteile offen vom Gezeichneten Kapital abgesetzt;Erworbene eigene Anteile17)
2910;bs.eqLiab.equity.subscribed.unpaidCap;P;Gezeichnetes Kapital / Kapitalkonto/ Kapitalanteile, nicht eingeforderte ausstehende Einlagen (offen passivisch abgesetzt);Ausstehende Einlagen auf das gezeichnete Kapital, nicht eingefordert (Passivausweis, vom gezeichneten Kapital offen abgesetzt; eingeforderte ausstehende Einlagen s. Konto 1298)
2920;bs.eqLiab.equity.capRes;P;Kapitalrücklage;Kapitalrücklage17) Kapitalrücklage durch Ausgabe von Anteilen über Nennbetrag17) Kapitalrücklage durch Ausgabe von Schuldverschreibungen für Wandlungsrechte und Optionsrechte zum Erwerb von Anteilen17) Kapitalrücklage durch Zuzahlungen gegen Gewährung eines Vorzugs für Anteile17) Kapitalrücklage durch Zuzahlungen in das Eigenkapital17) Nachschusskapital (Gegenkonto 1299)17)
2930;bs.eqLiab.equity.revenueRes.legal;P;gesetzliche Rücklage;Gesetzliche Rücklage17)
2935;---xxx---;P;Rücklage für Anteile an einem herrn schenden oder mehrheitlich beteiligten Unternehmen;Rücklage für Anteile an einem herrschenden oder mehrheitlich beteiligten Unternehmen
2950;bs.eqLiab.equity.revenueRes.statutory;P;satzungsmäßige Rücklagen;Satzungsmäßige Rücklagen17)
2960;bs.eqLiab.equity.revenueRes.other;P;andere Gewinnrücklagen;Andere Gewinnrücklagen17) Andere Gewinnrücklagen aus dem Erwerb eigener Anteile17) Eigenkapitalanteil von Wertaufholungen17) Gewinnrücklagen aus den Übergangsvorschriften BilMoG17) Gewinnrücklagen aus den Übergangsvorschriften BilMoG (Zuschreibung Sachanlagevermögen)17) Gewinnrücklagen aus den Übergangsvorschriften BilMoG (Zuschreibung Finanzanlagevermögen)17) Gewinnrücklagen aus den Übergangsvorschriften BilMoG (Auflösung der Sonderposten mit Rücklageanteil)17) Latente Steuern (Gewinnrücklage Haben) aus erfolgsneutralen Verrechnungen17) Latente Steuern (Gewinnrücklage Soll) aus erfolgsneutralen Verrechnungen17) Rechnungsabgrenzungsposten (Gewinnrücklage Soll) aus erfolgsneutralen Verrechnungen17)
2970;bs.eqLiab.equity.retainedEarnings;P;Eigenkapital, Gewinn-/Verlustvortrag bei Kapitalgesellschaften;Gewinnvortrag vor Verwendung 17) Verlustvortrag vor Verwendung 17)
2978;+2970+bs.eqLiab.equity.retainedEarnings;P;Eigenkapital, Gewinn-/Verlustvortrag bei Kapitalgesellschaften;Gewinnvortrag vor Verwendung 17) Verlustvortrag vor Verwendung 17)
2980;bs.eqLiab.otherSpecRes.other.other;P;Sonstige Sonderposten, andere Sonderposten, übrige andere Sonderposten;Übrige andere Sonderposten
2981;bs.eqLiab.otherSpecRes.other.EStG6b;P;Sonstige Sonderposten, andere Sonderposten, Rücklage für Veräußerungsgewinne nach § 6b EStG;Steuerfreie Rücklagen nach § 6b EStG
2982;bs.eqLiab.otherSpecRes.other.replacement;P;Sonstige Sonderposten, andere Sonderposten, Rücklage für Ersatzbeschaffung;Rücklage für Ersatzbeschaffung
2988;bs.eqLiab.otherSpecRes.other.subsidies;P;Sonstige Sonderposten, andere Sonderposten, Rücklage für Zuschüsse;Rücklage für Zuschüsse
2990;bs.eqLiab.pretaxRes.specAmort;P;Sonderposten mit Rücklageanteil, steuerrechtliche Sonderabschreibungen;Sonderposten mit Rücklageanteil, Sonderabschreibungen6)
2995;bs.eqLiab.otherSpecRes.other.releaseWithdrawalEStG4g;P;Sonstige Sonderposten, andere Sonderposten, Ausgleichsposten bei Entnahmen § 4g EStG;Ausgleichsposten bei Entnahmen § 4g EStG
2997;bs.eqLiab.pretaxRes.specAmort;P;Sonderposten mit Rücklageanteil, steuerrechtliche Sonderabschreibungen;Sonderposten mit Rücklageanteil nach § 7g Abs. 5 EStG
2998;bs.eqLiab.otherSpecRes.subsidies;P;Sonstige Sonderposten, Sonderposten für Investitionszulagen und für Zuschüsse Dritter;Sonderposten für Zuschüsse Dritter Sonderposten für Investitionszulagen
3000;bs.eqLiab.accruals.pensions.direct;P;Rückstellungen für Pensionen und ähnliche Verpflichtungen, Rückstellung für Direktzusagen;Rückstellungen für Pensionen und ähnliche Verpflichtungen
3005;bs.eqLiab.accruals.pensions.shareholder;P;Rückstellungen für Pensionen und ähnliche Verpflichtungen, gegenüber Gesellschaftern oder nahestehenden Personen;Rückstellungen für Pensionen und ähnliche Verpflichtungen gegenüber Gesellschaftern oder nahe stehenden Personen (10% Beteiligung am Kapital)
3009;bs.eqLiab.accruals.pensions.direct;P;Rückstellungen für Pensionen und ähnliche Verpflichtungen, Rückstellung für Direktzusagen;Rückstellungen für Pensionen und ähnliche Verpflichtungen zur Saldierung mit Vermögensgegenständen zum langfristigen Verbleib nach § 246 Abs. 2 HGB Rückstellungen für Direktzusagen
3011;bs.eqLiab.accruals.pensions.externalFunds;P;Rückstellungen für Pensionen und ähnliche Verpflichtungen, Rückstellungen für Zuschussverpflichtungen für Pensionskassen und Lebensversicherungen (bei Unterdeckung oder Aufstockung);Rückstellungen für Zuschussverpflichtungen für Pensionskassen und Lebensversicherungen
3015;bs.eqLiab.accruals.pensions.direct;P;Rückstellungen für Pensionen und ähnliche Verpflichtungen, Rückstellung für Direktzusagen;Rückstellungen für pensionsähnliche Verpflichtungen
3020;bs.eqLiab.accruals.tax.misc;A;Steuerrückstellungen, nicht zuordenbar;Steuerrückstellungen
3035;bs.eqLiab.accruals.tax.gewst;P;Steuerrückstellungen, Gewerbesteuerrückstellung;Gewerbesteuerrückstellung nach § 4 Abs. 5b EStG
3040;bs.eqLiab.accruals.tax.kst;P;Steuerrückstellungen, Körperschaftsteuerrückstellung;Körperschaftsteuerrückstellung
3050;bs.eqLiab.accruals.tax.other;P;Steuerrückstellungen, Rückstellung für sonstige Steuern (außer für latente Steuern);Steuerrückstellung für Steuerstundung (BStBK)
3060;bs.eqLiab.accruals.tax.defTax;P;Steuerrückstellungen, Rückstellungen für latente Steuern;Rückstellungen für latente Steuern
3065;bs.eqLiab.defTax;P;Passive latente Steuern;Passive latente Steuern
3070;---xxx---;P;sonstige Rückstellungen der Aktiver r Vermö-;Sonstige Rückstellungen Rückstellungen für Personalkosten Rückstellungen für unterlassene Aufwendungen für Instandhaltung, Nachholung in den ersten drei Monaten Rückstellungen für mit der Altersversorgung vergleichbare langfristige Verpflichtungen zum langfristigen Verbleib Rückstellungen für mit der Altersversorgung vergleichbare langfristige Verpflichtungen zur Saldierung mit Vermögensgegenständen zum langfristigen Verbleib nach § 246 Abs. 2 HGB Urlaubsrückstellungen Rückstellungen für Abraumund Abfallbeseitigung Rückstellungen für Gewährleistungen (Gegenkonto 6790) Rückstellungen für drohende Verluste aus schwebenden Geschäften Rückstellungen für Abschlussund Prüfungskosten Rückstellungen zur Erfüllung der Aufbewahrungspflichten Aufwandsrückstellungen nach § 249 Abs. 2 HGB a. F. Rückstellungen für Umweltschutz
3100;bs.eqLiab.liab.securities;P;Anleihen;Anleihen, nicht konvertibel Anleihen, nicht konvertibel Restlaufzeit bis 1 Jahr Anleihen, nicht konvertibel Restlaufzeit 1 bis 5 Jahre Anleihen, nicht konvertibel Restlaufzeit größer 5 Jahre Anleihen, konvertibel
3150;bs.eqLiab.liab.bank.other;P;Verbindlichkeiten gegenüber Kreditinstituten, übrige;Verbindlichkeiten gegenüber Kreditinstituten Verbindlichkeiten gegenüber Kreditinstituten Restlaufzeit bis 1 Jahr Verbindlichkeiten gegenüber Kreditinstituten Restlaufzeit 1 bis 5 Jahre Verbindlichkeiten gegenüber Kreditinstituten Restlaufzeit größer 5 Jahre Verbindlichkeiten gegenüber Kreditinstituten aus Teilzahlungsverträgen Verbindlichkeiten gegenüber Kreditinstituten aus Teilzahlungsverträgen Restlaufzeit bis 1 Jahr Verbindlichkeiten gegenüber Kreditinstituten aus Teilzahlungsverträgen Restlaufzeit 1 bis 5 Jahre Verbindlichkeiten gegenüber Kreditinstituten aus Teilzahlungsverträgen Restlaufzeit größer 5 Jahre Verbindlichkeiten gegenüber Kreditinstituten, vor Restlaufzeitdifferenzierung Gegenkonto 3150-3209 bei Aufteilung der Konten 3210-3248
3250;bs.eqLiab.liab.advPaym;P;erhaltene Anzahlungen auf Bestellungen;Erhaltene Anzahlungen auf Bestellungen (Verbindlichkeiten) Erhaltene, versteuerte Anzahlungen 7 % USt (Verbindlichkeiten) Erhaltene, versteuerte Anzahlungen 5 % USt (Verbindlichkeiten) Erhaltene, versteuerte Anzahlungen 0 % USt (Verbindlichkeiten)1) Erhaltene, versteuerte Anzahlungen 16 % USt (Verbindlichkeiten) Erhaltene, versteuerte Anzahlungen 19 % USt (Verbindlichkeiten) Erhaltene Anzahlungen Nachsteuer Erhaltene Anzahlungen Restlaufzeit bis 1 Jahr Erhaltene Anzahlungen Restlaufzeit 1 bis 5 Jahre Erhaltene Anzahlungen Restlaufzeit größer 5 Jahre
3300;bs.eqLiab.liab.trade.genOther;P;Verbindlichkeiten aus Lieferungen und Leistungen, übrige Verbindlichkeiten;Verbindlichkeiten aus Lieferungen und Leistungen Verbindlichkeiten aus Lieferungen und Leistungen ohne Kontokorrent Verbindlichkeiten aus Lieferungen und Leistungen ohne Kontokorrent Restlaufzeit bis 1 Jahr
3340;bs.eqLiab.liab.shareholders.misc;A;Verbindlichkeiten, Verbindlichkeiten gegenüber Gesellschaftern, nicht nach Rechtsform zuordenbar;Verbindlichkeiten aus Lieferungen und Leistungen gegenüber Gesellschaftern Verbindlichkeiten aus Lieferungen und Leistungen gegenüber Gesellschaftern Restlaufzeit bis 1 Jahr Verbindlichkeiten aus Lieferungen und Leistungen gegenüber Gesellschaftern Restlaufzeit 1 bis 5 Jahre Verbindlichkeiten aus Lieferungen und Leistungen gegenüber Gesellschaftern Restlaufzeit größer 5 Jahre
3349;bs.eqLiab.liab.trade.genOther;P;Verbindlichkeiten aus Lieferungen und Leistungen, übrige Verbindlichkeiten;Gegenkonto 3335-3348, 34203449, 3470-3499 bei Aufteilung Kreditorenkonto
3350;bs.eqLiab.liab.notes;P;Verbindlichkeiten aus der Annahme gezogener Wechsel und der Ausstellung eigener Wechsel;Wechselverbindlichkeiten Wechselverbindlichkeiten Restlaufzeit bis 1 Jahr Wechselverbindlichkeiten Restlaufzeit 1 bis 5 Jahre Wechselverbindlichkeiten Restlaufzeit größer 5 Jahre
3400;bs.eqLiab.liab.assocComp.other;P;Verbindlichkeiten gegenüber verbundenen Unternehmen, übrige;Verbindlichkeiten gegenüber verbundenen Unternehmen Verbindlichkeiten gegenüber verbundenen Unternehmen Restlaufzeit bis 1 Jahr Verbindlichkeiten gegenüber verbundenen Unternehmen Restlaufzeit 1 bis 5 Jahre Verbindlichkeiten gegenüber verbundenen Unternehmen Restlaufzeit größer 5 Jahre Verbindlichkeiten aus Lieferungen und Leistungen gegenüber verbundenen Unternehmen Verbindlichkeiten aus Lieferungen und Leistungen gegenüber verbundenen Unternehmen Restlaufzeit bis 1 Jahr Verbindlichkeiten aus Lieferungen und Leistungen gegenüber verbundenen Unternehmen Restlaufzeit 1 bis 5 Jahre Verbindlichkeiten aus Lieferungen und Leistungen gegenüber verbundenen Unternehmen Restlaufzeit größer 5 Jahre
3450;bs.eqLiab.liab.particip.other;P;Verbindlichkeiten gegenüber Unternehmen, mit denen ein Beteiligungsverhältnis besteht, übrige;Verbindlichkeiten gegenüber Unternehmen, mit denen ein Beteiligungsverhältnis besteht Verbindlichkeiten gegenüber Unternehmen, mit denen ein Beteiligungsverhältnis besteht Restlaufzeit bis 1 Jahr Verbindlichkeiten gegenüber Unternehmen, mit denen ein Beteiligungsverhältnis besteht Restlaufzeit 1 bis 5 Jahre
3500;bs.eqLiab.liab.other.other;P;sonstige Verbindlichkeiten, übrige sonstige Verbindlichkeiten;Sonstige Verbindlichkeiten Sonstige Verbindlichkeiten Restlaufzeit bis 1 Jahr Sonstige Verbindlichkeiten Restlaufzeit 1 bis 5 Jahre Sonstige Verbindlichkeiten Restlaufzeit größer 5 Jahre
3510;bs.eqLiab.liab.shareholders.misc;A;Verbindlichkeiten, Verbindlichkeiten gegenüber Gesellschaftern, nicht nach Rechtsform zuordenbar;Verbindlichkeiten gegenüber Gesellschaftern Verbindlichkeiten gegenüber Gesellschaftern Restlaufzeit bis 1 Jahr Verbindlichkeiten gegenüber Gesellschaftern Restlaufzeit 1 bis 5 Jahre Verbindlichkeiten gegenüber Gesellschaftern Restlaufzeit größer 5 Jahre Verbindlichkeiten gegenüber Gesellschaftern für offene Ausschüttungen
3520;---xxx---;P;sonstige Verbindlichkeiten, gegenüber stillen Gesellschaftern Aufzulösender Auffangposten;Verbindlichkeiten gegenüber typisch stillen Gesellschaftern Verbindlichkeiten gegenüber typisch stillen Gesellschaftern Restlaufzeit bis 1 Jahr Verbindlichkeiten gegenüber typisch stillen Gesellschaftern Restlaufzeit 1 bis 5 Jahre Verbindlichkeiten gegenüber typisch stillen Gesellschaftern Restlaufzeit größer 5 Jahre Verbindlichkeiten gegenüber atypisch stillen Gesellschaftern Verbindlichkeiten gegenüber atypisch stillen Gesellschaftern Restlaufzeit bis 1 Jahr Verbindlichkeiten gegenüber atypisch stillen Gesellschaftern Restlaufzeit 1 bis 5 Jahre Verbindlichkeiten gegenüber atypisch stillen Gesellschaftern Restlaufzeit größer 5 Jahre
3540;bs.eqLiab.liab.other.profitPartLoans;P;sonstige Verbindlichkeiten, sonstige Verbindlichkeiten aus partiarischen Darlehen;Partiarische Darlehen Partiarische Darlehen Restlaufzeit bis 1 Jahr
3550;---xxx---;P;sonstige Verbindlichkeiten, übrige sonstige Verbindlichkeiten onstige Verbindlichkeiten oder Sonsige Vermögensgegenstände onstige Verbindlichkeiten;Erhaltene Kautionen Erhaltene Kautionen Restlaufzeit bis 1 Jahr Erhaltene Kautionen Restlaufzeit 1 bis 5 Jahre Erhaltene Kautionen Restlaufzeit größer 5 Jahre Darlehen Darlehen Restlaufzeit bis 1 Jahr Darlehen Restlaufzeit 1 bis 5 Jahre Darlehen Restlaufzeit größer 5 Jahre Sonstige Verbindlichkeiten, vor Restlaufzeitdifferenzierung (nur Bilanzierer) Gegenkonto 3500-3569 und 36403658 bei Aufteilung der Konten 3570-3598 Agenturwarenabrechnung Kreditkartenabrechnung
3611;bs.eqLiab.liab.other.jointVent;P;sonstige Verbindlichkeiten, sonstige Verbindlichkeiten gegenüber Arbeitsgemeinschaften;Verbindlichkeiten gegenüber Arbeitsgemeinschaften
3620;bs.eqLiab.liab.other.silentPartner;P;sonstige Verbindlichkeiten, gegenüber stillen Gesellschaftern;Gewinnverfügungskonto stille Gesellschafter sonstige Verbindlichkeiten8)
3630;bs.eqLiab.liab.other.other;P;sonstige Verbindlichkeiten, übrige sonstige Verbindlichkeiten;Sonstige Verrechnungskonten (Interimskonto) Verbindlichkeiten gegenüber Gesellschaft/Gesamthand28)
3640;bs.eqLiab.liab.shareholders.gmbhSilent;P;Verbindlichkeiten, Verbindlichkeiten gegenüber Gesellschaftern, Verbindlichkeiten gegenüber GmbH-Gesellschaftern;Verbindlichkeiten gegenüber GmbH-Gesellschaftern Verbindlichkeiten gegenüber GmbH-Gesellschaftern Restlaufzeit bis 1 Jahr Verbindlichkeiten gegenüber GmbH-Gesellschaftern Restlaufzeit 1 bis 5 Jahre Verbindlichkeiten gegenüber GmbH-Gesellschaftern Restlaufzeit größer 5 Jahre
3655;bs.eqLiab.liab.other.silentPartner;P;sonstige Verbindlichkeiten, gegenüber stillen Gesellschaftern;Verbindlichkeiten gegenüber stillen Gesellschaftern Verbindlichkeiten gegenüber stillen Gesellschaftern Restlaufzeit bis 1 Jahr Verbindlichkeiten gegenüber stillen Gesellschaftern Restlaufzeit 1 bis 5 Jahre Verbindlichkeiten gegenüber stillen Gesellschaftern Restlaufzeit größer 5 Jahre
3695;bs.ass.currAss.receiv.other.other;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, übrige sonstige Vermögensgegenstände;Verrechnungskonto geleistete Anzahlungen bei Buchung über Kreditorenkonto
3700;bs.eqLiab.liab.other.theroffTax;P;sonstige Verbindlichkeiten, aus Steuern;Verbindlichkeiten aus Steuern und Abgaben Verbindlichkeiten aus Steuern und Abgaben Restlaufzeit bis 1 Jahr Verbindlichkeiten aus Steuern und Abgaben Restlaufzeit 1 bis 5 Jahre
3708;+3700+bs.eqLiab.liab.other.theroffTax;P;sonstige Verbindlichkeiten, aus Steuern;Verbindlichkeiten aus Steuern und Abgaben Verbindlichkeiten aus Steuern und Abgaben Restlaufzeit bis 1 Jahr Verbindlichkeiten aus Steuern und Abgaben Restlaufzeit 1 bis 5 Jahre
3720;bs.eqLiab.liab.other.employees;P;sonstige Verbindlichkeiten, sonstige Verbindlichkeiten gegenüber Mitarbeitern;Verbindlichkeiten aus Lohn und Gehalt Verbindlichkeiten für Einbehaltungen von Arbeitnehmern
3726;bs.eqLiab.liab.other.theroffTax;P;sonstige Verbindlichkeiten, aus Steuern;Verbindlichkeiten an das Finanzamt aus abzuführendem Bauabzugsbetrag Verbindlichkeiten aus Lohnund Kirchensteuer
3740;bs.eqLiab.liab.other.thereoffSocSec;P;sonstige Verbindlichkeiten, im Rahmen der sozialen Sicherheit;Verbindlichkeiten im Rahmen der sozialen Sicherheit Verbindlichkeiten im Rahmen der sozialen Sicherheit Restlaufzeit bis 1 Jahr Verbindlichkeiten im Rahmen der sozialen Sicherheit Restlaufzeit 1 bis 5 Jahre Verbindlichkeiten im Rahmen der sozialen Sicherheit Restlaufzeit größer 5 Jahre Voraussichtliche Beitragsschuld gegenüber den Sozialversicherungsträgern
3759;+3740+bs.eqLiab.liab.other.thereoffSocSec;P;sonstige Verbindlichkeiten, im Rahmen der sozialen Sicherheit;Verbindlichkeiten im Rahmen der sozialen Sicherheit Verbindlichkeiten im Rahmen der sozialen Sicherheit Restlaufzeit bis 1 Jahr Verbindlichkeiten im Rahmen der sozialen Sicherheit Restlaufzeit 1 bis 5 Jahre Verbindlichkeiten im Rahmen der sozialen Sicherheit Restlaufzeit größer 5 Jahre Voraussichtliche Beitragsschuld gegenüber den Sozialversicherungsträgern
3760;bs.eqLiab.liab.other.theroffTax;P;sonstige Verbindlichkeiten, aus Steuern;Verbindlichkeiten aus Einbehaltungen (KapESt und SolZ, KiSt auf KapESt) für offene Ausschüttungen Verbindlichkeiten für Verbrauchsteuern
3770;---xxx---;P;sonstige Verbindlichkeiten, im Rahmen der sozialen Sicherheit onstige Verbindlichkeiten;Verbindlichkeiten aus Vermögensbildung Verbindlichkeiten aus Vermögensbildung Restlaufzeit bis 1 Jahr Verbindlichkeiten aus Vermögensbildung Restlaufzeit 1 bis 5 Jahre Verbindlichkeiten aus Vermögensbildung Restlaufzeit größer 5 Jahre
3786;---xxx---;P;sonstige Verbindlichkeiten, übrige sonstige Verbindlichkeiten onstige Verbindlichkeiten oder Sonsige Vermögensgegenstände;Ausgegebene Geschenkgutscheine Lohnund Gehaltsverrechnungskonto
3798;---xxx---;P;sonstige Verbindlichkeiten, aus Steuern der Sons-;Umsatzsteuer aus im anderen EULand steuerpflichtigen elektronischen Dienstleistungen Steuerzahlungen aus im anderen EU-Land steuerpflichtigen Leistungen8) Umsatzsteuer Umsatzsteuer 7 % Umsatzsteuer aus innergemeinschaftlichem Erwerb Umsatzsteuer 5 %11) Umsatzsteuer aus innergemeinschaftlichem Erwerb 19 % Umsatzsteuer 16 %11) Umsatzsteuer 19 % Umsatzsteuer aus im Inland steuerpflichtigen EU-Lieferungen Umsatzsteuer aus im Inland steuerpflichtigen EU-Lieferungen 19 % Umsatzsteuer aus innergemeinschaftlichem Erwerb ohne Vorsteuerabzug
3810;bs.eqLiab.accruals.tax.other;P;Steuerrückstellungen, Rückstellung für sonstige Steuern (außer für latente Steuern);Umsatzsteuer nicht fällig Umsatzsteuer nicht fällig 7 %
3817;---xxx---;P;sonstige Verbindlichkeiten, aus Steuern der Sonsder Sonsder Sonsder Sons-;Umsatzsteuer aus im anderen EULand steuerpflichtigen Lieferungen Umsatzsteuer aus im anderen EULand steuerpflichtigen sonstigen Leistungen/Werklieferungen Umsatzsteuer aus Erwerb als letzter Abnehmer innerhalb eines Dreiecksgeschäfts Umsatzsteuer-Vorauszahlungen Umsatzsteuer-Vorauszahlungen 1/11 Umsatzsteuer aus im Inland steuerpflichtigen EU-Lieferungen, nur OSS Nachsteuer, UStVA Kz. 65 Umsatzsteuer aus innergemeinschaftlichem Erwerb von Neufahrzeugen von Lieferanten ohne Umsatzsteuer-Identifikationsnummer Umsatzsteuer nach § 13b UStG Umsatzsteuer nach § 13b UStG 19 % Umsatzsteuer nach § 13b UStG 16 %11) Umsatzsteuer aus der Auslagerung von Gegenständen aus einem Umsatzsteuerlager Umsatzsteuer laufendes Jahr Umsatzsteuer Vorjahr Umsatzsteuer frühere Jahre Einfuhrumsatzsteuer aufgeschoben bis... In Rechnung unrichtig oder unberechtigt ausgewiesene Steuerbeträge, UStVA Kz. 69 Steuerzahlungen an andere Länder Verbindlichkeiten aus Umsatzsteuer-Vorauszahlungen Umsatzsteuer in Folgeperiode fällig (§§ 13 Abs. 1 Nr. 6 und 13b Abs. 2 UStG)
3900;bs.eqLiab.defIncome;P;Passive Rechnungsabgrenzungsposten;Passive Rechnungsabgrenzung Abgrenzung unterjährig pauschal gebuchter Abschreibungen für BWA
4000;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.unknownVAT;A;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, ohne Zuordnung nach Umsatzsteuertatbeständen;Umsatzerlöse (Zur freien Verfügung)
4100;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.taxExemptUStG4_8.other;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, steuerfreie Umsätze nach § 4 Nr. 8 ff UStG, übrige nach § 4 Nr. 8 ff UStG steuerfreie Umsätze;Steuerfreie Umsätze § 4 Nr. 8 ff. UStG
4105;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.taxExemptUStG4_8.UStG4_12;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, steuerfreie Umsätze nach § 4 Nr. 8 ff UStG, steuerfreie Umsätze aus Vermietung und Verpachtung § 4 Nr. 12 UStG;Steuerfreie Umsätze nach § 4 Nr. 12 UStG (Vermietung und Verpachtung)
4110;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.taxExemptOther;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, sonstige umsatzsteuerfreie Umsätze;Sonstige steuerfreie Umsätze Inland
4120;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.taxExemptUStG4_1a;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, steuerfreie Umsätze nach § 4 Nr. 1 a) UStG (Ausfuhr Drittland);Steuerfreie Umsätze nach § 4 Nr. 1a UStG
4125;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.taxExemptUStG4_1b;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, steuerfreie innergemeinschaftliche Lieferungen nach § 4 Nr. 1 b) UStG;Steuerfreie Innergemeinschaftliche Lieferungen nach § 4 Nr. 1b UStG
4130;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.triangularTransactionUStG25b_2_4;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, innergemeinschaftliche Dreiecksgeschäfte nach § 25b Abs. 2, 4 UStG;Lieferungen des ersten Abnehmers bei innergemeinschaftlichen Dreiecksgeschäften § 25b Abs. 2 UStG
4135;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.taxExemptUStG4_1b;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, steuerfreie innergemeinschaftliche Lieferungen nach § 4 Nr. 1 b) UStG;Steuerfreie innergemeinschaftliche Lieferungen von Neufahrzeugen an Abnehmer ohne UmsatzsteuerIdentifikationsnummer
4136;---xxx---;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, Umsatzerlöse nach § 25 und § 25a UStG Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, Regelsteuersatz;Umsatzerlöse nach §§ 25 und 25a UStG 19 % USt
4138;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.UStG25_25a;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, Umsatzerlöse nach § 25 und § 25a UStG;Umsatzerlöse nach §§ 25 und 25a UStG ohne USt Umsatzerlöse aus Reiseleistungen § 25 Abs. 2 UStG, steuerfrei
4140;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.taxExemptOther;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, sonstige umsatzsteuerfreie Umsätze;Steuerfreie Umsätze Offshore etc.
4150;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.taxExemptUStG4_2til7;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, steuerfreie Umsätze nach § 4 Nr. 2-7 UStG;Sonstige steuerfreie Umsätze (z. B. § 4 Nr. 2 bis 7 UStG)
4160;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.taxExemptOther;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, sonstige umsatzsteuerfreie Umsätze;Steuerfreie Umsätze ohne Vorsteuerabzug zum Gesamtumsatz gehörend, § 4 UStG Steuerfreie Umsätze ohne Vorsteuerabzug zum Gesamtumsatz gehörend
4180;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.otherRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, sonstige Umsatzsteuersätze;Erlöse, die mit den Durchschnittssätzen des § 24 UStG versteuert werden
4185;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.taxExemptOther;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, sonstige umsatzsteuerfreie Umsätze;Erlöse als Kleinunternehmer nach § 19 Abs. 1 UStG
4186;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.generalRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, Regelsteuersatz;Erlöse aus Geldspielautomaten 19 % USt
4200;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.unknownVAT;A;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, ohne Zuordnung nach Umsatzsteuertatbeständen;Erlöse
4290;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.otherRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, sonstige Umsatzsteuersätze;Erlöse 0 % USt1)
4300;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.reducedRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, ermäßigter Steuersatz;Erlöse 7 % USt Erlöse aus im Inland steuerpflichtigen EU-Lieferungen 7 % USt
4315;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.generalRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, Regelsteuersatz;Erlöse aus im Inland steuerpflichtigen EU-Lieferungen 19 % USt
4320;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.untaxable;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, nicht steuerbare Umsatzerlöse;Erlöse aus im anderen EU-Land steuerpflichtigen Lieferungen, im Inland nicht steuerbar3) Erlöse aus im anderen EU-Land steuerpflichtigen elektronischen Dienstleistungen5)
4333;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.otherRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, sonstige Umsatzsteuersätze;Erlöse 5 % USt11)
4334;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.reducedRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, ermäßigter Steuersatz;Erlöse 7 % USt
4335;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.UStG13b;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, Erlöse aus Leistungen nach § 13b UStG;Erlöse aus Lieferungen von Mobilfunkgeräten,Tablet-Computern, Spielekonsolen und integrierten Schaltkreisen, für die der Leistungsempfänger die Umsatzsteuer nach § 13b UStG schuldet
4336;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.untaxable;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, nicht steuerbare Umsatzerlöse;Erlöse aus im anderen EU-Land steuerpflichtigen sonstigen Leistungen, für die der Leistungsempfänger die Umsatzsteuer schuldet
4337;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.UStG13b;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, Erlöse aus Leistungen nach § 13b UStG;Erlöse aus Leistungen, für die der Leistungsempfänger die Umsatzsteuer nach § 13b UStG schuldet
4338;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.untaxable;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, nicht steuerbare Umsatzerlöse;Erlöse aus im Drittland steuerbaren Leistungen, im Inland nicht steuerbare Umsätze Erlöse aus im anderen EU-Land steuerbaren Leistungen, im Inland nicht steuerbare Umsätze
4340;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.otherRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, sonstige Umsatzsteuersätze;Erlöse 16 % USt
4400;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.generalRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, Regelsteuersatz;Erlöse 19 % USt Erlöse 19 % USt Erlöse aus im Inland steuerpflichtigen elektronischen Dienstleistungen 19 % USt
4499;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.unknownVAT;A;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, ohne Zuordnung nach Umsatzsteuertatbeständen;Nebenerlöse (Bezug zu Materialaufwand) Sonderbetriebseinnahmen, Tätigkeitsvergütung28) Sonderbetriebseinnahmen, Miet/Pachteinnahmen28) Sonderbetriebseinnahmen, Zinseinnahmen28) Sonderbetriebseinnahmen, Haftungsvergütung28) Sonderbetriebseinnahmen, Pensionszahlungen28) Sonderbetriebseinnahmen, sonstige Sonderbetriebseinnahmen28)
4510;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.unknownVAT;A;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, ohne Zuordnung nach Umsatzsteuertatbeständen;Erlöse Abfallverwertung Erlöse Leergut Provisionsumsätze
4564;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.taxExemptUStG4_8.other;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, steuerfreie Umsätze nach § 4 Nr. 8 ff UStG, übrige nach § 4 Nr. 8 ff UStG steuerfreie Umsätze;Provisionsumsätze, steuerfrei § 4 Nr. 8 ff. UStG
4565;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.taxExemptUStG4_2til7;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, steuerfreie Umsätze nach § 4 Nr. 2-7 UStG;Provisionsumsätze, steuerfrei § 4 Nr. 5 UStG
4566;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.reducedRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, ermäßigter Steuersatz;Provisionsumsätze 7 % USt
4569;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.generalRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, Regelsteuersatz;Provisionsumsätze 19 % USt
4570;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.unknownVAT;A;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, ohne Zuordnung nach Umsatzsteuertatbeständen;Sonstige Erträge aus Provisionen, Lizenzen und Patenten
4574;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.taxExemptUStG4_8.other;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, steuerfreie Umsätze nach § 4 Nr. 8 ff UStG, übrige nach § 4 Nr. 8 ff UStG steuerfreie Umsätze;Sonstige Erträge aus Provisionen, Lizenzen und Patenten, steuerfrei § 4 Nr. 8 ff. UStG
4575;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.taxExemptUStG4_2til7;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, steuerfreie Umsätze nach § 4 Nr. 2-7 UStG;Sonstige Erträge aus Provisionen, Lizenzen und Patenten, steuerfrei § 4 Nr. 5 UStG
4576;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.reducedRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, ermäßigter Steuersatz;Sonstige Erträge aus Provisionen, Lizenzen und Patenten 7 % USt
4579;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.generalRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, Regelsteuersatz;Sonstige Erträge aus Provisionen, Lizenzen und Patenten 19 % USt
4600;is.netIncome.regular.operatingTC.otherOpRevenue.ownConsumption.otherWithdrawals;P;sonstige betriebliche Erträge (GKV), Erträge aus Eigenverbrauch und Sachbezügen, sonstige Sach-, Nutzungsund Leistungsentnahmen;Unentgeltliche Wertabgaben Unentgeltliche Erbringung einer sonstigen Leistung 7 % USt Unentgeltliche Erbringung einer sonstigen Leistung 7 % USt Unentgeltliche Erbringung einer sonstigen Leistung ohne USt Unentgeltliche Erbringung einer sonstigen Leistung 19 % USt Unentgeltliche Zuwendung von Waren 7 % USt Unentgeltliche Zuwendung von Waren 7 % USt Unentgeltliche Zuwendung von Waren ohne USt Unentgeltliche Zuwendung von Waren 19 % USt Unentgeltliche Zuwendung von Gegenständen 19 % USt Unentgeltliche Zuwendung von Gegenständen ohne USt
4690;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.untaxable;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, nicht steuerbare Umsatzerlöse;Nicht steuerbare Umsätze (Innenumsätze)
4695;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.otherRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, sonstige Umsatzsteuersätze;Umsatzsteuervergütungen, z.B. nach § 24 UStG
4699;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.taxFromGrossSales;P;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, sonstige direkt mit dem Umsatz verbundene Steuern;Direkt mit dem Umsatz verbundene Steuern
4700;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.unknownVAT;A;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, ohne Zuordnung nach Umsatzsteuertatbeständen;Erlösschmälerungen
4701;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.taxExemptUStG4_8;P;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, für steuerfreie Umsätze nach § 4 Nr. 8 ff. UStG;Erlösschmälerungen für steuerfreie Umsätze nach § 4 Nr. 8 ff. UStG
4702;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.taxExemptUStG4_2til7;P;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, für steuerfreie Umsätze nach § 4 Nr. 2-7 UStG;Erlösschmälerungen für steuerfreie Umsätze nach § 4 Nr. 2 bis 7 UStG
4703;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.taxExemptOther;P;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, für sonstige steuerfreie Umsätze;Erlösschmälerungen für sonstige steuerfreie Umsätze ohne Vorsteuerabzug Erlösschmälerungen für sonstige steuerfreie Umsätze mit Vorsteuerabzug
4705;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.taxExemptUStG4_1a;P;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, für steuerfreie Umsätze nach § 4 Nr. 1 a) UStG (Ausfuhr, Drittland);Erlösschmälerungen aus steuerfreien Umsätzen § 4 Nr. 1a UStG
4706;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.UStGs25_2_4;P;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, für steuerfreie innergemeinschaftliche Dreiecksgeschäfte nach § 25b Abs. 2, 4 UStG;Erlösschmälerungen für steuerfreie innergemeinschaftliche Dreiecksgeschäfte nach § 25b Abs. 2 und 4 UStG
4710;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.reducedRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, ermäßigter Steuersatz;Erlösschmälerungen 7 % USt
4719;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.otherRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, übrige Steuersätze;Erlösschmälerungen 0 % USt1)
4720;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.generalRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, Regelsteuersatz;Erlösschmälerungen 19 % USt
4724;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.taxExemptUStG4_1b;P;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, für steuerfreie innergemeinschaftliche Lieferungen nach § 4 Nr. 1 b) UStG;Erlösschmälerungen aus steuerfreien innergemeinschaftlichen Lieferungen
4725;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.reducedRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, ermäßigter Steuersatz;Erlösschmälerungen aus im Inland steuerpflichtigen EU-Lieferungen 7 % USt
4726;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.generalRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, Regelsteuersatz;Erlösschmälerungen aus im Inland steuerpflichtigen EU-Lieferungen 19 % USt
4727;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.untaxable;P;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, sonstige Umsatzerlöse nicht steuerbar;Erlösschmälerungen aus im anderen EU-Land steuerpflichtigen Lieferungen3)
4730;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.unknownVAT;A;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, ohne Zuordnung nach Umsatzsteuertatbeständen;Gewährte Skonti
4731;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.reducedRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, ermäßigter Steuersatz;Gewährte Skonti 7 % USt
4732;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.otherRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, übrige Steuersätze;Gewährte Skonti 5 % USt11) Gewährte Skonti 0 % USt1) Gewährte Skonti 16 % USt11)
4736;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.generalRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, Regelsteuersatz;Gewährte Skonti 19 % USt
4738;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.untaxed;P;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, aus Leistungen nach § 13b UStG;Gewährte Skonti a. Lieferungen v. Mobilfunkgeräten etc., für die der Leistungsempfänger die Umsatzst. nach § 13b Abs. 2 Nr. 10 UStG schuldet Gewährte Skonti aus Leistungen, für die der Leistungsempfänger die Umsatzsteuer nach § 13b UStG schuldet
4742;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.untaxable;P;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, sonstige Umsatzerlöse nicht steuerbar;Gewährte Skonti aus Erlöse aus im anderen EU-Land steuerpflichtigen sonstigen Leistungen, für die der Leistungsempfänger die Umsatzsteuer schuldet
4743;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.taxExemptUStG4_1b;P;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, für steuerfreie innergemeinschaftliche Lieferungen nach § 4 Nr. 1 b) UStG;Gewährte Skonti aus steuerfreien innergemeinschaftlichen Lieferungen § 4 Nr. 1b UStG
4745;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.unknownVAT;A;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, ohne Zuordnung nach Umsatzsteuertatbeständen;Gewährte Skonti aus im Inland steuerpflichtigen EU-Lieferungen
4746;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.reducedRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, ermäßigter Steuersatz;Gewährte Skonti aus im Inland steuerpflichtigen EU-Lieferungen 7 % USt
4747;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.otherRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, übrige Steuersätze;Gewährte Skonti aus im Inland steuerpflichtigen EU-Lieferungen 5 % USt11)
4748;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.generalRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, Regelsteuersatz;Gewährte Skonti aus im Inland steuerpflichtigen EU-Lieferungen 19 % USt
4749;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.otherRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, übrige Steuersätze;Gewährte Skonti aus im Inland steuerpflichtigen EU-Lieferungen 16 % USt11)
4750;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.reducedRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, ermäßigter Steuersatz;Gewährte Boni 7 % USt
4760;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.generalRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, Regelsteuersatz;Gewährte Boni 19 % USt
4769;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.unknownVAT;A;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, ohne Zuordnung nach Umsatzsteuertatbeständen;Gewährte Boni Gewährte Rabatte
4780;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.reducedRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, ermäßigter Steuersatz;Gewährte Rabatte 7 % USt
4790;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.generalRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse verrechnete Erlösschmälerungen und sonstige direkt mit dem Umsatz verbundene Steuern, Regelsteuersatz;Gewährte Rabatte 19 % USt
4800;---xxx---;P;Erhöhung oder Verminderung des Berstandes an fertigen und unfertigen Erzeugnissen (GKV) uge;Bestandsveränderungen fertige Erzeugnisse Bestandsveränderungen unfertige Erzeugnisse Bestandsveränderungen unfertige Leistungen Bestandsveränderungen in Ausführung befindlicher Bauaufträge Bestandsveränderungen in Arbeit befindlicher Aufträge
4820;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.ownWork;P;andere aktivierte Eigenleistungen (GKV);Andere aktivierte Eigenleistungen Aktivierte Eigenleistungen (den Herstellungskosten zurechenbare Fremdkapitalzinsen) Aktivierte Eigenleistungen zur Erstellung von selbst geschaffenen immateriellen Vermögensgegenständen
4830;is.netIncome.regular.operatingTC.otherOpRevenue.miscellaneous;P;sonstige betriebliche Erträge (GKV), andere sonstige betriebliche Erträge;Sonstige betriebliche Erträge Sonstige betriebliche Erträge von verbundenen Unternehmen
4833;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.unknownVAT;A;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, ohne Zuordnung nach Umsatzsteuertatbeständen;Andere Nebenerlöse
4834;is.netIncome.regular.operatingTC.otherOpRevenue.miscellaneous;P;sonstige betriebliche Erträge (GKV), andere sonstige betriebliche Erträge;Sonstige Erträge betrieblich und regelmäßig 16 % USt Sonstige Erträge betrieblich und regelmäßig Sonstige Erträge betrieblich und regelmäßig 19 % USt Sonstige Erträge betriebsfremd und regelmäßig Erstattete Vorsteuer anderer Länder
4840;is.netIncome.regular.operatingTC.otherOpRevenue.currGains;P;sonstige betriebliche Erträge (GKV), Kurs-/Währungsgewinne;Erträge aus der Währungsumrechnung
4841;is.netIncome.regular.operatingTC.otherOpRevenue.miscellaneous;P;sonstige betriebliche Erträge (GKV), andere sonstige betriebliche Erträge;Sonstige Erträge betrieblich und regelmäßig, steuerfrei § 4 Nr. 8 ff. UStG Sonstige betriebliche Erträge, steuerfrei z. B. § 4 Nr. 2 bis 7 UStG
4843;is.netIncome.regular.operatingTC.otherOpRevenue.currGains;P;sonstige betriebliche Erträge (GKV), Kurs-/Währungsgewinne;Erträge aus Bewertung Finanzmittelfonds
4844;is.netIncome.regular.operatingTC.otherOpRevenue.disposFixAss.sale.tan;P;sonstige betriebliche Erträge (GKV), Erträge aus Abgängen des Anlagevermögens, Erlöse aus Verkäufen des Anlagevermögens, Erlöse aus Verkäufen von Sachanlagen;Erlöse aus Verkäufen Sachanlagevermögen steuerfrei § 4 Nr. 1a UStG (bei Buchgewinn) Erlöse aus Verkäufen Sachanlagevermögen 19 % USt (bei Buchgewinn)
4847;is.netIncome.regular.operatingTC.otherOpRevenue.currGains;P;sonstige betriebliche Erträge (GKV), Kurs-/Währungsgewinne;Erträge aus der Währungsumrechnung (nicht § 256a HGB)
4848;is.netIncome.regular.operatingTC.otherOpRevenue.disposFixAss.sale.tan;P;sonstige betriebliche Erträge (GKV), Erträge aus Abgängen des Anlagevermögens, Erlöse aus Verkäufen des Anlagevermögens, Erlöse aus Verkäufen von Sachanlagen;Erlöse aus Verkäufen Sachanlagevermögen steuerfrei § 4 Nr. 1b UStG (bei Buchgewinn) Erlöse aus Verkäufen Sachanlagevermögen (bei Buchgewinn)
4850;is.netIncome.regular.operatingTC.otherOpRevenue.disposFixAss.sale.intan;P;sonstige betriebliche Erträge (GKV), Erträge aus Abgängen des Anlagevermögens, Erlöse aus Verkäufen des Anlagevermögens, Erlöse aus Verkäufen von immateriellen Vermögensgegenständen;Erlöse aus Verkäufen immaterieller Vermögensgegenstände (bei Buchgewinn)
4851;is.netIncome.regular.operatingTC.otherOpRevenue.disposFixAss.sale.fin;P;sonstige betriebliche Erträge (GKV), Erträge aus Abgängen des Anlagevermögens, Erlöse aus Verkäufen des Anlagevermögens, Erlöse aus Verkäufen von Finanzanlagen;Erlöse aus Verkäufen Finanzanlagen (bei Buchgewinn) Erlöse aus Verkäufen Finanzanlagen § 3 Nr. 40 EStG bzw. § 8b Abs. 2 KStG (bei Buchgewinn)9)
4855;is.netIncome.regular.operatingTC.otherOpRevenue.disposFixAss.bookValue.tan;P;sonstige betriebliche Erträge (GKV), Erträge aus Abgängen des Anlagevermögens, Anlagenabgänge Anlagevermögen, Anlagenabgänge Sachanlagen;Anlagenabgänge Sachanlagen (Restbuchwert bei Buchgewinn)
4856;is.netIncome.regular.operatingTC.otherOpRevenue.disposFixAss.bookValue.intan;P;sonstige betriebliche Erträge (GKV), Erträge aus Abgängen des Anlagevermögens, Anlagenabgänge Anlagevermögen, Anlagenabgänge immaterielle Vermögensgegenstände;Anlagenabgänge immaterielle Vermögensgegenstände (Restbuchwert bei Buchgewinn)
4857;is.netIncome.regular.operatingTC.otherOpRevenue.disposFixAss.bookValue.fin;P;sonstige betriebliche Erträge (GKV), Erträge aus Abgängen des Anlagevermögens, Anlagenabgänge Anlagevermögen, Anlagenabgänge Finanzanlagen;Anlagenabgänge Finanzanlagen (Restbuchwert bei Buchgewinn) Anlagenabgänge Finanzanlagen § 3 Nr. 40 EStG bzw. § 8b Abs. 2 KStG (Restbuchwert bei Buchgewinn)9)
4860;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.unknownVAT;A;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, ohne Zuordnung nach Umsatzsteuertatbeständen;Grundstückserträge
4861;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.taxExemptUStG4_8.UStG4_12;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, steuerfreie Umsätze nach § 4 Nr. 8 ff UStG, steuerfreie Umsätze aus Vermietung und Verpachtung § 4 Nr. 12 UStG;Erlöse aus Vermietung und Verpachtung, umsatzsteuerfrei § 4 Nr. 12 UStG
4862;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.generalRateVAT;P;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, Regelsteuersatz;Erlöse aus Vermietung und Verpachtung 19 % USt
4900;is.netIncome.regular.operatingTC.otherOpRevenue.disposFixAss.sale.tan;P;sonstige betriebliche Erträge (GKV), Erträge aus Abgängen des Anlagevermögens, Erlöse aus Verkäufen des Anlagevermögens, Erlöse aus Verkäufen von Sachanlagen;Erträge aus dem Abgang von Gegenständen des Anlagevermögens12)
4901;is.netIncome.regular.operatingTC.otherOpRevenue.disposFixAss.sale.fin;P;sonstige betriebliche Erträge (GKV), Erträge aus Abgängen des Anlagevermögens, Erlöse aus Verkäufen des Anlagevermögens, Erlöse aus Verkäufen von Finanzanlagen;Erträge aus der Veräußerung von Anteilen an Kapitalgesellschaften (Finanzanlagevermögen) § 3 Nr. 40 EStG bzw. § 8b Abs. 2 KStG9)
4905;is.netIncome.regular.operatingTC.otherOpRevenue.disposCurrAss;P;sonstige betriebliche Erträge (GKV), Erträge aus Abgängen des Umlaufvermögens (außer Produkte);Erträge aus dem Abgang von Gegenständen des Umlaufvermögens (außer Vorräte) Erträge aus dem Abgang von Gegenständen des Umlaufvermögens (außer Vorräte) § 3 Nr. 40 EStG bzw. § 8b Abs. 2 KStG9)
4910;is.netIncome.regular.operatingTC.otherOpRevenue.revalFixAss;P;sonstige betriebliche Erträge (GKV), Erträge aus Zuschreibungen des Anlagevermögens;Erträge aus Zuschreibungen des Sachanlagevermögens Erträge aus Zuschreibungen des immateriellen Anlagevermögens Erträge aus Zuschreibungen des Finanzanlagevermögens Erträge aus Zuschreibungen des Finanzanlagevermögens § 3 Nr. 40 EStG bzw. § 8b Abs. 3 S. 8 KStG9) Erträge aus Zuschreibungen § 3 Nr. 40 EStG bzw. § 8b Abs. 2 KStG9)
4915;is.netIncome.regular.operatingTC.otherOpRevenue.revalCurrAss;P;sonstige betriebliche Erträge (GKV), Erträge aus Zuschreibungen des Umlaufvermögens;Erträge aus Zuschreibungen des Umlaufvermögens (außer Vorräte) Erträge aus Zuschreibungen des Umlaufvermögens § 3 Nr. 40 EStG bzw. § 8b Abs. 3 S. 8 KStG9)
4920;is.netIncome.regular.operatingTC.otherOpRevenue.releaseLossProv.globalValuation;P;sonstige betriebliche Erträge (GKV), Erträge aus der Herabsetzung / Auflösung von Einzelund Pauschalwertberichtigungen, Pauschalwertberichtigungen;Erträge aus der Herabsetzung der Pauschalwertberichtigung auf Forderungen
4923;is.netIncome.regular.operatingTC.otherOpRevenue.releaseLossProv.specificValuation;P;sonstige betriebliche Erträge (GKV), Erträge aus der Herabsetzung / Auflösung von Einzelund Pauschalwertberichtigungen, Einzelwertberichtigungen;Erträge aus der Herabsetzung der Einzelwertberichtigung auf Forderungen
4925;is.netIncome.regular.operatingTC.otherOpRevenue.recoveryWriteoffs;P;sonstige betriebliche Erträge (GKV), Zahlungseingänge auf in früheren Perioden abgeschriebene Forderungen;Erträge aus abgeschriebenen Forderungen
4927;is.netIncome.regular.operatingTC.otherOpRevenue.releasePreTaxRes.EStG6b_3;P;sonstige betriebliche Erträge (GKV), Erträge aus Auflösung des Sonderpostens mit Rücklageanteil und anderer Sonderposten, § 6b Abs. 3 EStG;Erträge aus der Auflösung einer steuerlichen Rücklage nach § 6b Abs. 3 EStG
4929;is.netIncome.regular.operatingTC.otherOpRevenue.releasePreTaxRes.substEStR6_6;P;sonstige betriebliche Erträge (GKV), Erträge aus Auflösung des Sonderpostens mit Rücklageanteil und anderer Sonderposten, Rücklage für Ersatzbeschaffung, R 6.6 EStR;Erträge aus der Auflösung der Rücklage für Ersatzbeschaffung, R 6.6 EStR
4930;is.netIncome.regular.operatingTC.otherOpRevenue.releaseProv;P;sonstige betriebliche Erträge (GKV), Erträge aus der Auflösung von Rückstellungen;Erträge aus der Auflösung von Rückstellungen
4932;is.netIncome.regular.operatingTC.otherOpRevenue.releasLiab;P;sonstige betriebliche Erträge (GKV), Erträge aus der Herabsetzung von Verbindlichkeiten;Erträge aus der Herabsetzung von Verbindlichkeiten
4935;is.netIncome.regular.operatingTC.otherOpRevenue.releasePreTaxRes.other;P;sonstige betriebliche Erträge (GKV), Erträge aus Auflösung des Sonderpostens mit Rücklageanteil und anderer Sonderposten, sonstige Erträge aus Auflösung eines Sonderpostens mit Rücklageanteil und anderer Sonderposten;Erträge aus der Auflösung sonstiger steuerlicher Rücklagen Erträge aus der Auflösung steuerrechtlicher Sonderabschreibungen
4938;is.netIncome.regular.operatingTC.otherOpRevenue.releasePreTaxRes.EStG4g;P;sonstige betriebliche Erträge (GKV), Erträge aus Auflösung des Sonderpostens mit Rücklageanteil und anderer Sonderposten, § 4g EStG;Erträge aus der Auflösung einer steuerlichen Rücklage nach § 4g EStG
4940;is.netIncome.regular.operatingTC.otherOpRevenue.ownConsumption.nonCashBenefitsOther;P;sonstige betriebliche Erträge (GKV), Erträge aus Eigenverbrauch und Sachbezügen, sonstige Sachbezüge;Verrechnete sonstige Sachbezüge (keine Waren) Sachbezüge 7 % USt (Waren) Sachbezüge 19 % USt (Waren) Verrechnete sonstige Sachbezüge
4947;is.netIncome.regular.operatingTC.otherOpRevenue.ownConsumption.nonCashBenefitsCompCar;P;sonstige betriebliche Erträge (GKV), Erträge aus Eigenverbrauch und Sachbezügen, Sachbezüge Kfz;Verrechnete sonstige Sachbezüge aus Fahrzeug-Gestellung 19 % USt8)
4948;is.netIncome.regular.operatingTC.otherOpRevenue.ownConsumption.nonCashBenefitsOther;P;sonstige betriebliche Erträge (GKV), Erträge aus Eigenverbrauch und Sachbezügen, sonstige Sachbezüge;Verrechnete sonstige Sachbezüge 19 % USt Verrechnete sonstige Sachbezüge ohne Umsatzsteuer
4960;is.netIncome.regular.operatingTC.otherOpRevenue.miscellaneous;P;sonstige betriebliche Erträge (GKV), andere sonstige betriebliche Erträge;Periodenfremde Erträge
4970;is.netIncome.regular.operatingTC.otherOpRevenue.insuranceRefunds;P;sonstige betriebliche Erträge (GKV), Versicherungsentschädigungen und Schadensersatzleistungen;Versicherungsentschädigungen und Schadenersatzleistungen Erstattungen Aufwendungsausgleichsgesetz
4975;is.netIncome.regular.operatingTC.otherOpRevenue.subsidies;P;sonstige betriebliche Erträge (GKV), Zuschüsse und Zulagen;Investitionszuschüsse (steuerpflichtig) Investitionszulagen (steuerfrei)
4981;is.netIncome.regular.operatingTC.otherOpRevenue.releasePreTaxRes.misc;A;sonstige betriebliche Erträge (GKV), Erträge aus Auflösung des Sonderpostens mit Rücklageanteil und anderer Sonderposten, nicht zuordenbar;Steuerfreie Erträge aus der Auflösung von steuerlichen Rücklagen
4982;is.netIncome.regular.operatingTC.otherOpRevenue.miscellaneous;P;sonstige betriebliche Erträge (GKV), andere sonstige betriebliche Erträge;Sonstige steuerfreie Betriebseinnahmen
4987;is.netIncome.regular.operatingTC.otherOpRevenue.acqudFreeOfCharge;P;sonstige betriebliche Erträge (GKV), Erträge aus der Aktivierung unentgeltlich erworbener Vermögensgegenstände;Erträge aus der Aktivierung unentgeltlich erworbener Vermögensgegenstände
4989;is.netIncome.regular.operatingTC.otherOpRevenue.miscellaneous;P;sonstige betriebliche Erträge (GKV), andere sonstige betriebliche Erträge;Kostenerstattungen, Rückvergütungen und Gutschriften für frühere Jahre
4992;is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.unknownVAT;A;Umsatzerlöse (GKV), in Umsatzerlöse enthaltener Bruttowert, ohne Zuordnung nach Umsatzsteuertatbeständen;Erträge aus Verwaltungskostenumlagen
5000;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.unknownVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, übriger Wareneinkauf ohne Zuordnung nach Umsatzsteuertatbeständen;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren
5100;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.unknownVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, übrige Roh-, Hilfsund Betriebsstoffe ohne Zuordnung nach Umsatzsteuertatbeständen;Einkauf Roh-, Hilfsund Betriebsstoffe
5110;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.reducedRateVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, ermäßigter Steuersatz;Einkauf Roh-, Hilfsund Betriebsstoffe 7 % Vorsteuer
5129;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.noDeductVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, ohne Vorsteuerabzug;Einkauf Roh-, Hilfsund Betriebsstoffe ohne Vorsteuerabzug
5130;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.generalRateVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, Regelsteuersatz;Einkauf Roh-, Hilfsund Betriebsstoffe 19 % Vorsteuer
5160;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.intraEU;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, innergemeinschaftliche Erwerbe;Einkauf Roh-, Hilfsund Betriebsstoffe, innergemeinschaftlicher Erwerb 7 % Vorsteuer und 7 % Umsatzsteuer Einkauf Roh-, Hilfsund Betriebsstoffe, innergemeinschaftlicher Erwerb 19 % Vorsteuer und 19 % Umsatzsteuer Einkauf Roh-, Hilfsund Betriebsstoffe, innergemeinschaftlicher Erwerb ohne Vorsteuer und 7 % Umsatzsteuer Einkauf Roh-, Hilfsund Betriebsstoffe, innergemeinschaftlicher Erwerb ohne Vorsteuer und 19 % Umsatzsteuer
5170;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.unknownVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, übrige Roh-, Hilfsund Betriebsstoffe ohne Zuordnung nach Umsatzsteuertatbeständen;Einkauf Roh-, Hilfsund Betriebsstoffe 5,5 % Vorsteuer Einkauf Roh-, Hilfsund Betriebsstoffe 9,5 % / 9,0 % Vorsteuer8)
5175;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.reducedRateVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, ermäßigter Steuersatz;Einkauf Roh-, Hilfsund Betriebsstoffe aus einem USt-Lager § 13a UStG 7 % Vorsteuer und 7 % Umsatzsteuer
5176;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.generalRateVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, Regelsteuersatz;Einkauf Roh-, Hilfsund Betriebsstoffe aus einem USt-Lager § 13a UStG 19 % Vorsteuer und 19 % Umsatzsteuer
5189;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.intraEU;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, innergemeinschaftliche Erwerbe;Erwerb Roh-, Hilfsund Betriebsstoffe als letzter Abnehmer innerhalb Dreiecksgeschäft 19 % Vorsteuer und 19 % Umsatzsteuer
5190;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.unknownVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, übrige Roh-, Hilfsund Betriebsstoffe ohne Zuordnung nach Umsatzsteuertatbeständen;Energiestoffe (Fertigung)
5191;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.reducedRateVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, ermäßigter Steuersatz;Energiestoffe (Fertigung) 7 % Vorsteuer
5192;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.generalRateVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, Regelsteuersatz;Energiestoffe (Fertigung) 19 % Vorsteuer
5200;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.unknownVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, übriger Wareneinkauf ohne Zuordnung nach Umsatzsteuertatbeständen;Wareneingang
5300;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.reducedRateVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, Wareneinkauf zum ermäßigten Steuersatz;Wareneingang 7 % Vorsteuer Wareneingang 7 % Vorsteuer
5348;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.unknownVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, übriger Wareneinkauf ohne Zuordnung nach Umsatzsteuertatbeständen;Wareneingang 5 % Vorsteuer11)
5349;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.withoutVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, Wareneinkauf ohne Vorsteuerabzug;Wareneingang ohne Vorsteuerabzug
5400;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.generalRateVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, Wareneinkauf zum Regelsteuersatz;Wareneingang 19 % Vorsteuer Wareneingang 19 % Vorsteuer
5419;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.unknownVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, übriger Wareneinkauf ohne Zuordnung nach Umsatzsteuertatbeständen;Wareneingang 16 % Vorsteuer 11)
5420;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.intraEU;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, Innergemeinschaftliche Erwerbe;Innergemeinschaftlicher Erwerb 7 % Vorsteuer und 7 % Umsatzsteuer Innergemeinschaftlicher Erwerb 19 % Vorsteuer und 19 % Umsatzsteuer Innergemeinschaftlicher Erwerb ohne Vorsteuer und 7 % Umsatzsteuer
5505;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.unknownVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, übriger Wareneinkauf ohne Zuordnung nach Umsatzsteuertatbeständen;Wareneingang 5,5 % Vorsteuer Wareneingang zum Durchschnittssatz nach § 24 UStG 9,5 % / 9,0 % Vorsteuer8)
5550;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.intraEU;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, Innergemeinschaftliche Erwerbe;Steuerfreier innergemeinschaftlicher Erwerb
5551;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.unknownVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, übriger Wareneinkauf ohne Zuordnung nach Umsatzsteuertatbeständen;Wareneingang im Drittland steuerbar
5552;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.intraEU;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, Innergemeinschaftliche Erwerbe;Erwerb 1. Abnehmer innerhalb eines Dreieckgeschäftes Erwerb Waren als letzter Abnehmer innerhalb Dreiecksgeschäft 19 % Vorsteuer und 19 % Umsatzsteuer
5558;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.unknownVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, übriger Wareneinkauf ohne Zuordnung nach Umsatzsteuertatbeständen;Wareneingang im anderen EULand steuerbar Steuerfreie Einfuhren
5560;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.reducedRateVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, Wareneinkauf zum ermäßigten Steuersatz;Waren aus einem Umsatzsteuerlager, § 13a UStG 7 % Vorsteuer und 7 % Umsatzsteuer
5565;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.generalRateVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, Wareneinkauf zum Regelsteuersatz;Waren aus einem Umsatzsteuerlager, § 13a UStG 19 % Vorsteuer und 19 % Umsatzsteuer
5600;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.unknownVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, übriger Wareneinkauf ohne Zuordnung nach Umsatzsteuertatbeständen;Nicht abziehbare Vorsteuer Nicht abziehbare Vorsteuer 7 %
5701;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.unknownVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, übrige Roh-, Hilfsund Betriebsstoffe ohne Zuordnung nach Umsatzsteuertatbeständen;Nachlässe aus Einkauf Roh-, Hilfsund Betriebsstoffe
5710;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.reducedRateVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, Wareneinkauf zum ermäßigten Steuersatz;Nachlässe 7 % Vorsteuer
5714;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.reducedRateVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, ermäßigter Steuersatz;Nachlässe aus Einkauf Roh-, Hilfsund Betriebsstoffe 7 % Vorsteuer
5715;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.generalRateVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, Regelsteuersatz;Nachlässe aus Einkauf Roh-, Hilfsund Betriebsstoffe 19 % Vorsteuer
5717;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.intraEU;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, innergemeinschaftliche Erwerbe;Nachlässe aus Einkauf Roh-, Hilfsund Betriebsstoffe, innergemeinschaftlicher Erwerb 7 % Vorsteuer und 7 % Umsatzsteuer Nachlässe aus Einkauf Roh-, Hilfsund Betriebsstoffe, innergemeinschaftlicher Erwerb 19 % Vorsteuer und 19 % Umsatzsteuer
5720;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.generalRateVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, Wareneinkauf zum Regelsteuersatz;Nachlässe 19 % Vorsteuer
5724;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.intraEU;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, Innergemeinschaftliche Erwerbe;Nachlässe aus innergemeinschaftlichem Erwerb 7 % Vorsteuer und 7 % Umsatzsteuer Nachlässe aus innergemeinschaftlichem Erwerb 19 % Vorsteuer und 19 % Umsatzsteuer
5730;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.unknownVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, übriger Wareneinkauf ohne Zuordnung nach Umsatzsteuertatbeständen;Erhaltene Skonti
5731;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.reducedRateVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, Wareneinkauf zum ermäßigten Steuersatz;Erhaltene Skonti 7 % Vorsteuer
5732;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.unknownVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, übriger Wareneinkauf ohne Zuordnung nach Umsatzsteuertatbeständen;Erhaltene Skonti 5 % Vorsteuer11)
5733;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.unknownVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, übrige Roh-, Hilfsund Betriebsstoffe ohne Zuordnung nach Umsatzsteuertatbeständen;Erhaltene Skonti aus Einkauf Roh-, Hilfsund Betriebsstoffe
5734;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.reducedRateVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, ermäßigter Steuersatz;Erhaltene Skonti aus Einkauf Roh-, Hilfsund Betriebsstoffe 7 % Vorsteuer
5735;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.unknownVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, übrige Roh-, Hilfsund Betriebsstoffe ohne Zuordnung nach Umsatzsteuertatbeständen;Erhaltene Skonti aus Einkauf Roh-, Hilfsund Betriebsstoffe 5 % Vorsteuer 11)
5736;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.generalRateVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, Wareneinkauf zum Regelsteuersatz;Erhaltene Skonti 19 % Vorsteuer
5737;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.unknownVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, übriger Wareneinkauf ohne Zuordnung nach Umsatzsteuertatbeständen;Erhaltene Skonti 16 % Vorsteuer11)
5738;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.generalRateVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, Regelsteuersatz;Erhaltene Skonti aus Einkauf Roh-, Hilfsund Betriebsstoffe 19 % Vorsteuer
5739;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.unknownVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, übrige Roh-, Hilfsund Betriebsstoffe ohne Zuordnung nach Umsatzsteuertatbeständen;Erhaltene Skonti aus Einkauf Roh-, Hilfsund Betriebsstoffe 16 % Vorsteuer 11)
5740;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.intraEU;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, innergemeinschaftliche Erwerbe;Erhaltene Skonti aus Einkauf Roh-, Hilfsund Betriebsstoffe aus steuerpflichtigem innergemeinschaftlichem Erwerb 16 % Vorsteuer und 16 % Umsatzsteuer11) Erhaltene Skonti aus Einkauf Roh-, Hilfsund Betriebsstoffe aus steuerpflichtigem innergemeinschaftlichem Erwerb 19 % Vorsteuer und 19 % Umsatzsteuer Erhaltene Skonti aus Einkauf Roh-, Hilfsund Betriebsstoffe aus steuerpflichtigem innergemeinschaftlichem Erwerb 5 % Vorsteuer und 5 % Umsatzsteuer11) Erhaltene Skonti aus Einkauf Roh-, Hilfsund Betriebsstoffe aus steuerpflichtigem innergemeinschaftlichem Erwerb 7 % Vorsteuer und 7 % Umsatzsteuer Erhaltene Skonti aus Einkauf Roh-, Hilfsund Betriebsstoffe aus steuerpflichtigem innergemeinschaftlichem Erwerb
5745;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.intraEU;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, Innergemeinschaftliche Erwerbe;Erhaltene Skonti aus steuerpflichtigem innergemeinschaftlichem Erwerb Erhaltene Skonti aus steuerpflichtigem innergemeinschaftlichem Erwerb 7 % Vorsteuer und 7 % Umsatzsteuer
5750;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.reducedRateVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, Wareneinkauf zum ermäßigten Steuersatz;Erhaltene Boni 7 % Vorsteuer
5753;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.unknownVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, übrige Roh-, Hilfsund Betriebsstoffe ohne Zuordnung nach Umsatzsteuertatbeständen;Erhaltene Boni aus Einkauf Roh-, Hilfsund Betriebsstoffe
5754;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.reducedRateVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, ermäßigter Steuersatz;Erhaltene Boni aus Einkauf Roh-, Hilfsund Betriebsstoffe 7 % Vorsteuer
5755;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.generalRateVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, Regelsteuersatz;Erhaltene Boni aus Einkauf Roh-, Hilfsund Betriebsstoffe 19 % Vorsteuer
5760;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.generalRateVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, Wareneinkauf zum Regelsteuersatz;Erhaltene Boni 19 % Vorsteuer
5769;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.unknownVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, übriger Wareneinkauf ohne Zuordnung nach Umsatzsteuertatbeständen;Erhaltene Boni Erhaltene Rabatte
5780;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.reducedRateVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, Wareneinkauf zum ermäßigten Steuersatz;Erhaltene Rabatte 7 % Vorsteuer
5783;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.unknownVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, übrige Roh-, Hilfsund Betriebsstoffe ohne Zuordnung nach Umsatzsteuertatbeständen;Erhaltene Rabatte aus Einkauf Roh, Hilfsund Betriebsstoffe
5784;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.reducedRateVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, ermäßigter Steuersatz;Erhaltene Rabatte aus Einkauf Roh, Hilfsund Betriebsstoffe 7 % Vorsteuer
5785;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.generalRateVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, Regelsteuersatz;Erhaltene Rabatte aus Einkauf Roh, Hilfsund Betriebsstoffe 19 % Vorsteuer
5787;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.unknownVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, übrige Roh-, Hilfsund Betriebsstoffe ohne Zuordnung nach Umsatzsteuertatbeständen;Erhaltene Skonti aus Einkauf Roh-, Hilfsund Betriebsstoffe 9,0 % Vorsteuer 1) Erhaltene Skonti aus Einkauf Roh-, Hilfsund Betriebsstoffe 10,7 % Vorsteuer11) Erhaltene Skonti aus Einkauf Roh-, Hilfsund Betriebsstoffe 9,5 % Vorsteuer
5790;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.generalRateVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, Wareneinkauf zum Regelsteuersatz;Erhaltene Rabatte 19 % Vorsteuer
5792;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.intraEU;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, innergemeinschaftliche Erwerbe;Erhaltene Skonti aus Erwerb Roh-, Hilfsund Betriebsstoffe als letzter Abnehmer innerhalb Dreiecksgeschäft 19 % Vorsteuer und 19 % Umsatzsteuer
5793;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.intraEU;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, Innergemeinschaftliche Erwerbe;Erhaltene Skonti aus Erwerb Waren als letzter Abnehmer innerhalb Dreiecksgeschäft 19 % Vorsteuer und 19 % Umsatzsteuer
5794;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.unknownVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, übriger Wareneinkauf ohne Zuordnung nach Umsatzsteuertatbeständen;Erhaltene Skonti 5,5 % Vorsteuer Erhaltene Skonti 9,0 % Vorsteuer1) Erhaltene Skonti 10,7 % Vorsteuer 11) Erhaltene Skonti 9,5 % Vorsteuer
5798;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.unknownVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, übrige Roh-, Hilfsund Betriebsstoffe ohne Zuordnung nach Umsatzsteuertatbeständen;Erhaltene Skonti aus Einkauf Roh-, Hilfsund Betriebsstoffe 5,5 % Vorsteuer
5800;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.unknownVAT;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, übriger Wareneinkauf ohne Zuordnung nach Umsatzsteuertatbeständen;Bezugsnebenkosten Leergut Zölle und Einfuhrabgaben Verrechnete Stoffkosten (Gegenkonto zu 5000-99)
5880;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.inventoryChange;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für bezogene Waren, Bestandsveränderungen;Bestandsveränderungen Roh-, Hilfsund Betriebsstoffe sowie bezogene Waren Bestandsveränderungen Waren
5885;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.inventoryChange;P;Aufwendungen für Roh-, Hilfsund Betriebsstoffe und für bezogene Waren (GKV), Aufwendungen für Roh-, Hilfsund Betriebsstoffe, Bestandsveränderungen;Bestandsveränderungen Roh-, Hilfsund Betriebsstoffe
5900;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.services.unknownVAT;A;Aufwendungen für bezogene Leistungen (GKV), Übrige Leistungen ohne Zuordnung nach Umsatzsteuertatbeständen;Fremdleistungen
5906;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.services.OtherDedInputTax;P;Aufwendungen für bezogene Leistungen (GKV), Übrige Leistungen mit Vorsteuerabzug;Fremdleistungen 19 % Vorsteuer Fremdleistungen 7 % Vorsteuer
5909;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.services.OtherNonDedInputTax;P;Aufwendungen für bezogene Leistungen (GKV), Übrige Leistungen ohne Vorsteuerabzug;Fremdleistungen ohne Vorsteuer
5910;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.services.UStG13bDedInputTax;P;Aufwendungen für bezogene Leistungen (GKV), Leistungen nach § 13b UStG mit Vorsteuerabzug;Bauleistungen eines im Inland ansässigen Unternehmers 7 % Vorsteuer und 7 % Umsatzsteuer Sonstige Leistungen eines im anderen EU-Land ansässigen Unternehmers 7 % Vorsteuer und 7 % Umsatzsteuer Leistungen eines im Ausland ansässigen Unternehmers 7 % Vorsteuer und 7 % Umsatzsteuer Bauleistungen eines im Inland ansässigen Unternehmers 19 % Vorsteuer und 19 % Umsatzsteuer Sonstige Leistungen eines im anderen EU-Land ansässigen Unternehmers 19 % Vorsteuer und 19 % Umsatzsteuer Leistungen eines im Ausland ansässigen Unternehmers 19 % Vorsteuer und 19 % Umsatzsteuer
5930;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.services.UStG13bNonDedInputTax;P;Aufwendungen für bezogene Leistungen (GKV), Leistungen nach § 13b UStG ohne Vorsteuerabzug;Bauleistungen eines im Inland ansässigen Unternehmers ohne Vorsteuer und 7 % Umsatzsteuer Sonstige Leistungen eines im anderen EU-Land ansässigen Unternehmers ohne Vorsteuer und 7 % Umsatzsteuer Leistungen eines im Ausland ansässigen Unternehmers ohne Vorsteuer und 7 % Umsatzsteuer Bauleistungen eines im Inland ansässigen Unternehmers ohne Vorsteuer und 19 % Umsatzsteuer Sonstige Leistungen eines im anderen EU-Land ansässigen Unternehmers ohne Vorsteuer und 19 % Umsatzsteuer Leistungen eines im Ausland ansässigen Unternehmers ohne Vorsteuer und 19 % Umsatzsteuer
5950;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.services.UStG13bDedInputTax;P;Aufwendungen für bezogene Leistungen (GKV), Leistungen nach § 13b UStG mit Vorsteuerabzug;Erhaltene Skonti aus Leistungen, für die als Leistungsempfänger die Steuer nach § 13b UStG geschuldet wird Erhaltene Skonti aus Leistungen, für die als Leistungsempfänger die Steuer nach § 13b UStG geschuldet wird 19 % Vorsteuer und 19 % Umsatzsteuer
5953;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.services.UStG13bNonDedInputTax;P;Aufwendungen für bezogene Leistungen (GKV), Leistungen nach § 13b UStG ohne Vorsteuerabzug;Erhaltene Skonti aus Leistungen, für die als Leistungsempfänger die Steuer nach § 13b UStG geschuldet wird ohne Vorsteuer aber mit Umsatzsteuer Erhaltene Skonti aus Leistungen, für die als Leistungsempfänger die Steuer nach § 13b UStG geschuldet wird ohne Vorsteuer, mit 19 % Umsatzsteuer Erhaltene Skonti aus Leistungen, für die als Leistungsempfänger die Steuer nach § 13b UStG geschuldet wird ohne Vorsteuer, mit 16 % Umsatzsteuer11)
5960;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.services.UStG13bDedInputTax;P;Aufwendungen für bezogene Leistungen (GKV), Leistungen nach § 13b UStG mit Vorsteuerabzug;Leistungen nach § 13b UStG mit Vorsteuerabzug21)
5965;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.services.UStG13bNonDedInputTax;P;Aufwendungen für bezogene Leistungen (GKV), Leistungen nach § 13b UStG ohne Vorsteuerabzug;Leistungen nach § 13b UStG ohne Vorsteuerabzug21)
5970;is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.services.unknownVAT;A;Aufwendungen für bezogene Leistungen (GKV), Übrige Leistungen ohne Zuordnung nach Umsatzsteuertatbeständen;Fremdleistungen (Mietund Pachtzinsen bewegliche Wirtschaftsgüter) Fremdleistungen (Mietund Pachtzinsen unbewegliche Wirtschaftsgüter) Fremdleistungen (Entgelte für Rechte und Lizenzen)
6000;is.netIncome.regular.operatingTC.staff.salaries.misc;P;Löhne und Gehälter (GKV), übrige Löhne und Gehälter;Löhne und Gehälter Löhne Gehälter
6010;+6000+is.netIncome.regular.operatingTC.staff.salaries.misc;P;Löhne und Gehälter (GKV), übrige Löhne und Gehälter;Löhne und Gehälter Löhne Gehälter
6020;+6010+is.netIncome.regular.operatingTC.staff.salaries.misc;P;Löhne und Gehälter (GKV), übrige Löhne und Gehälter;Löhne und Gehälter Löhne Gehälter
6024;is.netIncome.regular.operatingTC.staff.salaries.managerPartner;P;Löhne und Gehälter (GKV), Vergütungen an Gesellschafter-Geschäftsführer;Geschäftsführergehälter der GmbH-Gesellschafter Tantiemen Gesellschafter-Geschäftsführer
6027;is.netIncome.regular.operatingTC.staff.salaries.misc;P;Löhne und Gehälter (GKV), übrige Löhne und Gehälter;Geschäftsführergehälter Tantiemen Arbeitnehmer Aushilfslöhne
6035;is.netIncome.regular.operatingTC.staff.salaries.minijobs;P;Löhne und Gehälter (GKV), Löhne für Minijobs;Löhne für Minijobs Pauschale Steuer für Minijobber
6037;is.netIncome.regular.operatingTC.staff.salaries.managerPartner;P;Löhne und Gehälter (GKV), Vergütungen an Gesellschafter-Geschäftsführer;Pauschale Steuer für Gesellschafter-Geschäftsführer
6039;is.netIncome.regular.operatingTC.staff.salaries.misc;P;Löhne und Gehälter (GKV), übrige Löhne und Gehälter;Pauschale Steuer für Arbeitnehmer Pauschale Steuer für Aushilfen Bedienungsgelder
6060;is.netIncome.regular.operatingTC.staff.salaries.voluntayBenefits;P;Löhne und Gehälter (GKV), freiwillige Zuwendungen;Freiwillige soziale Aufwendungen, lohnsteuerpflichtig
6066;is.netIncome.regular.operatingTC.staff.salaries.minijobs;P;Löhne und Gehälter (GKV), Löhne für Minijobs;Freiwillige Zuwendungen an Minijobber
6067;is.netIncome.regular.operatingTC.staff.salaries.managerPartner;P;Löhne und Gehälter (GKV), Vergütungen an Gesellschafter-Geschäftsführer;Freiwillige Zuwendungen an Gesellschafter-Geschäftsführer
6069;is.netIncome.regular.operatingTC.staff.salaries.voluntayBenefits;P;Löhne und Gehälter (GKV), freiwillige Zuwendungen;Pauschale Steuer auf sonstige Bezüge (z. B. Fahrtkostenzuschüsse) Krankengeldzuschüsse
6071;is.netIncome.regular.operatingTC.staff.salaries.minijobs;P;Löhne und Gehälter (GKV), Löhne für Minijobs;Sachzuwendungen und Dienstleistungen an Minijobber
6072;is.netIncome.regular.operatingTC.staff.salaries.inKind;P;Löhne und Gehälter (GKV), Sachbezüge;Sachzuwendungen und Dienstleistungen an Arbeitnehmer
6073;is.netIncome.regular.operatingTC.staff.salaries.managerPartner;P;Löhne und Gehälter (GKV), Vergütungen an Gesellschafter-Geschäftsführer;Sachzuwendungen und Dienstleistungen an Gesellschafter-Geschäftsführer
6075;is.netIncome.regular.operatingTC.staff.salaries.misc;P;Löhne und Gehälter (GKV), übrige Löhne und Gehälter;Zuschüsse der Agenturen für Arbeit (Haben) Aufwendungen aus der Veränderung von Urlaubsrückstellungen
6077;is.netIncome.regular.operatingTC.staff.salaries.managerPartner;P;Löhne und Gehälter (GKV), Vergütungen an Gesellschafter-Geschäftsführer;Aufwendungen aus der Veränderung von Urlaubsrückstellungen für Gesellschafter-Geschäftsführer
6079;is.netIncome.regular.operatingTC.staff.salaries.minijobs;P;Löhne und Gehälter (GKV), Löhne für Minijobs;Aufwendungen aus der Veränderung von Urlaubsrückstellungen für Minijobber
6080;is.netIncome.regular.operatingTC.staff.salaries.misc;P;Löhne und Gehälter (GKV), übrige Löhne und Gehälter;Vermögenswirksame Leistungen
6090;is.netIncome.regular.operatingTC.staff.salaries.voluntayBenefits;P;Löhne und Gehälter (GKV), freiwillige Zuwendungen;Fahrtkostenerstattung Wohnung/Arbeitsstätte
6100;---xxx---;A;soziale Abgaben und Aufwendungen stütfür Altersversorgung und für Unterstützung (GKV), nicht zuordenbar;Soziale Abgaben und Aufwendungen für Altersversorgung und für Unterstützung
6110;is.netIncome.regular.operatingTC.staff.social.socExp.other;P;soziale Abgaben und Aufwendungen für Altersversorgung und für Unterstützung (GKV), soziale Abgaben, für übrige Arbeitnehmer;Gesetzliche soziale Aufwendungen Beiträge zur Berufsgenossenschaft Freiwillige soziale Aufwendungen, lohnsteuerfrei
6140;is.netIncome.regular.operatingTC.staff.social.pensions.other;P;soziale Abgaben und Aufwendungen für Altersversorgung und für Unterstützung (GKV), Aufwendungen für Altersversorgung, für übrige Arbeitnehmer;Aufwendungen für Altersversorgung Pauschale Steuer auf sonstige Bezüge (z. B. Direktversicherungen)
6149;is.netIncome.regular.operatingTC.staff.social.pensions.shareholderManager;P;soziale Abgaben und Aufwendungen für Altersversorgung und für Unterstützung (GKV), Aufwendungen für Altersversorgung, für Gesellschafter-Geschäftsführer;Aufwendungen für Altersversorgung für Gesellschafter-Geschäftsführer
6150;is.netIncome.regular.operatingTC.staff.social.pensions.other;P;soziale Abgaben und Aufwendungen für Altersversorgung und für Unterstützung (GKV), Aufwendungen für Altersversorgung, für übrige Arbeitnehmer;Versorgungskassen
6160;is.netIncome.regular.operatingTC.staff.social.welfare;P;soziale Abgaben und Aufwendungen für Altersversorgung und für Unterstützung (GKV), Aufwendungen für Unterstützung;Aufwendungen für Unterstützung
6170;is.netIncome.regular.operatingTC.staff.social.socExp.other;P;soziale Abgaben und Aufwendungen für Altersversorgung und für Unterstützung (GKV), soziale Abgaben, für übrige Arbeitnehmer;Sonstige soziale Abgaben Soziale Abgaben für Minijobber
6200;is.netIncome.regular.operatingTC.deprAmort.fixAss.otherIntan;P;Abschreibungen (GKV) auf immaterielle Vermögensgegenstände des Anlagevermögens und Sachanlagen, auf andere immaterielle Vermögensgegenstände;Abschreibungen auf immaterielle Vermögensgegenstände Abschreibungen auf selbst geschaffene immaterielle Vermögensgegenstände
6205;is.netIncome.regular.operatingTC.deprAmort.fixAss.goodwill;P;Abschreibungen (GKV) auf immaterielle Vermögensgegenstände des Anlagevermögens und Sachanlagen, auf Geschäfts-, Firmenoder Praxiswert;Abschreibungen auf den Geschäftsoder Firmenwert
6209;is.netIncome.regular.operatingTC.deprAmort.fixAss.specific.except.goodwill;P;Abschreibungen (GKV) auf immaterielle Vermögensgegenstände des Anlagevermögens und Sachanlagen, außerplanmäßige und Sonderabschreibungen und sonstige Abzüge, außerplanmäßige Abschreibungen, auf Geschäfts-, Firmenoder Praxiswert;Außerplanmäßige Abschreibungen auf den Geschäftsoder Firmenwert
6210;is.netIncome.regular.operatingTC.deprAmort.fixAss.specific.except.otherIntan;P;Abschreibungen (GKV) auf immaterielle Vermögensgegenstände des Anlagevermögens und Sachanlagen, außerplanmäßige und Sonderabschreibungen und sonstige Abzüge, außerplanmäßige Abschreibungen, auf andere immaterielle Vermögensgegenstände;Außerplanmäßige Abschreibungen auf immaterielle Vermögensgegenstände Außerplanmäßige Abschreibungen auf selbst geschaffene immaterielle Vermögensgegenstände
6220;is.netIncome.regular.operatingTC.deprAmort.fixAss.tan.otherMisc;A;Abschreibungen (GKV) auf immaterielle Vermögensgegenstände des Anlagevermögens und Sachanlagen, auf Sachanlagen, nicht zuordenbare Abschreibungen auf Sachanlagen;Abschreibungen auf Sachanlagen (ohne AfA auf Fahrzeuge und Gebäude)8)
6221;is.netIncome.regular.operatingTC.deprAmort.fixAss.tan.buildings;P;Abschreibungen (GKV) auf immaterielle Vermögensgegenstände des Anlagevermögens und Sachanlagen, auf Sachanlagen, Abschreibungen auf Gebäude;Abschreibungen auf Gebäude
6222;is.netIncome.regular.operatingTC.deprAmort.fixAss.tan.other;P;Abschreibungen (GKV) auf immaterielle Vermögensgegenstände des Anlagevermögens und Sachanlagen, auf Sachanlagen, übrige Abschreibungen auf Sachanlagen;Abschreibungen auf Fahrzeuge8)
6230;is.netIncome.regular.operatingTC.deprAmort.fixAss.specific.except.tan;P;Abschreibungen (GKV) auf immaterielle Vermögensgegenstände des Anlagevermögens und Sachanlagen, außerplanmäßige und Sonderabschreibungen und sonstige Abzüge, außerplanmäßige Abschreibungen, auf Sachanlagen;Außerplanmäßige Abschreibungen auf Sachanlagen Absetzung für außergewöhnliche technische und wirtschaftliche Abnutzung der Gebäude Absetzung für außergewöhnliche technische und wirtschaftliche Abnutzung der Fahrzeuge8) Absetzung für außergewöhnliche technische und wirtschaftliche Abnutzung sonstiger Wirtschaftsgüter
6240;is.netIncome.regular.operatingTC.deprAmort.fixAss.specific.impairment;P;Abschreibungen (GKV) auf immaterielle Vermögensgegenstände des Anlagevermögens und Sachanlagen, außerplanmäßige und Sonderabschreibungen und sonstige Abzüge, Sonderabschreibungen;Abschreibungen auf Sachanlagen auf Grund steuerlicher Sondervorschriften Sonderabschreibungen nach § 7g Abs. 5 EStG (ohne Fahrzeuge)8) Sonderabschreibungen nach § 7g Abs. 5 EStG (für Fahrzeuge)8)
6243;is.netIncome.regular.operatingTC.otherCost.deductValueEStG7g_2;P;Abschreibungen (GKV) auf immaterielle Vermögensgegenstände des Anlagevermögens und Sachanlagen, außerplanmäßige und Sonderabschreibungen und sonstige Abzüge, Herabsetzungsbetrag nach § 7g Abs. 2 EStG;Kürzung der Anschaffungsoder Herstellungskosten nach § 7g Abs. 2 EStG (ohne Fahrzeuge)8) Kürzung der Anschaffungsoder Herstellungskosten nach § 7g Abs. 2 EStG (für Fahrzeuge)8)
6245;is.netIncome.regular.operatingTC.deprAmort.fixAss.specific.impairment;P;Abschreibungen (GKV) auf immaterielle Vermögensgegenstände des Anlagevermögens und Sachanlagen, außerplanmäßige und Sonderabschreibungen und sonstige Abzüge, Sonderabschreibungen;Sonderabschreibungen nach § 7b EStG (Mietwohnungsneubau)
6249;is.netIncome.regular.operatingTC.deprAmort.fixAss.specific.EStG6b_3;P;Abschreibungen (GKV) auf immaterielle Vermögensgegenstände des Anlagevermögens und Sachanlagen, außerplanmäßige und Sonderabschreibungen und sonstige Abzüge, Abzugsbetrag nach § 6b EStG;Abzugsbetrag nach § 6b EStG
6250;is.netIncome.regular.operatingTC.deprAmort.fixAss.tan.other;P;Abschreibungen (GKV) auf immaterielle Vermögensgegenstände des Anlagevermögens und Sachanlagen, auf Sachanlagen, übrige Abschreibungen auf Sachanlagen;Kaufleasing
6260;is.netIncome.regular.operatingTC.deprAmort.fixAss.tan.lowValueAs;P;Abschreibungen (GKV) auf immaterielle Vermögensgegenstände des Anlagevermögens und Sachanlagen, auf Sachanlagen, Sofortabschreibung GWG;Sofortabschreibung geringwertiger Wirtschaftsgüter
6262;is.netIncome.regular.operatingTC.deprAmort.fixAss.tan.other;P;Abschreibungen (GKV) auf immaterielle Vermögensgegenstände des Anlagevermögens und Sachanlagen, auf Sachanlagen, übrige Abschreibungen auf Sachanlagen;Abschreibungen auf aktivierte, geringwertige Wirtschaftsgüter
6264;is.netIncome.regular.operatingTC.deprAmort.fixAss.tan.lowValueAsCollItem;P;Abschreibungen (GKV) auf immaterielle Vermögensgegenstände des Anlagevermögens und Sachanlagen, auf Sachanlagen, Auflösung GWG-Sammelposten;Abschreibungen auf den Sammelposten Wirtschaftsgüter
6266;is.netIncome.regular.operatingTC.deprAmort.fixAss.specific.except.tan;P;Abschreibungen (GKV) auf immaterielle Vermögensgegenstände des Anlagevermögens und Sachanlagen, außerplanmäßige und Sonderabschreibungen und sonstige Abzüge, außerplanmäßige Abschreibungen, auf Sachanlagen;Außerplanmäßige Abschreibungen auf aktivierte geringwertige Wirtschaftsgüter
6270;---xxx---;P;Abschreibungen (GKV), auf Vermögensgegenstände des Umlaufvermöft übgens, soweit diese die in der Kapitalgen sellschaft üblichen Abschreibungen überschreiten, Abschreibungen auf Forderungen und sonstige Vermögensgegenstände, übrige Abschreibungen auf Forderungen und sonstige Vermögensgegenstände;Abschreibungen auf sonstige Vermögensgegenstände des Umlaufvermögens (soweit unüblich hoch)
6272;is.netIncome.regular.operatingTC.deprAmort.currAss.misc;A;Abschreibungen (GKV), auf Vermögensgegenstände des Umlaufvermögens, soweit diese die in der Kapitalgesellschaft üblichen Abschreibungen überschreiten, nicht zuordenbar;Abschreibungen auf Umlaufvermögen, steuerrechtlich bedingt (soweit unüblich hoch)
6278;is.netIncome.regular.operatingTC.deprAmort.currAss.inventory;P;Abschreibungen (GKV), auf Vermögensgegenstände des Umlaufvermögens, soweit diese die in der Kapitalgesellschaft üblichen Abschreibungen überschreiten, Abschreibungen auf Vorräte;Abschreibungen auf Roh-, Hilfsund Betriebsstoffe/Waren (soweit unüblich hoch) Abschreibungen auf fertige und unfertige Erzeugnisse (soweit unüblich hoch)
6280;is.netIncome.regular.operatingTC.deprAmort.currAss.receiv.other;P;Abschreibungen (GKV), auf Vermögensgegenstände des Umlaufvermögens, soweit diese die in der Kapitalgesellschaft üblichen Abschreibungen überschreiten, Abschreibungen auf Forderungen und sonstige Vermögensgegenstände, übrige Abschreibungen auf Forderungen und sonstige Vermögensgegenstände;Forderungsverluste (soweit unüblich hoch) Forderungsverluste 7 % USt (soweit unüblich hoch) Forderungsverluste 19 % USt (soweit unüblich hoch)
6290;is.netIncome.regular.operatingTC.deprAmort.currAss.receiv.againstCorpParticip;P;Abschreibungen (GKV), auf Vermögensgegenstände des Umlaufvermögens, soweit diese die in der Kapitalgesellschaft üblichen Abschreibungen überschreiten, Abschreibungen auf Forderungen und sonstige Vermögensgegenstände, Abschreibungen auf Forderungen gegenüber Kapitalgesellschaften, an denen eine Beteiligung besteht;Abschreibungen auf Forderungen gegenüber Kapitalgesellschaften, an denen eine Beteiligung besteht (soweit unüblich hoch), § 3c EStG bzw. § 8b Abs. 3 KStG
6291;is.netIncome.regular.operatingTC.deprAmort.currAss.receiv.sharehRelPart;P;Abschreibungen (GKV), auf Vermögensgegenstände des Umlaufvermögens, soweit diese die in der Kapitalgesellschaft üblichen Abschreibungen überschreiten, Abschreibungen auf Forderungen und sonstige Vermögensgegenstände, Abschreibungen auf Forderungen gegenüber Gesellschaftern und nahe stehenden Personen;Abschreibungen auf Forderungen gegenüber Gesellschaftern und nahe stehenden Personen (soweit unüblich hoch), § 8b Abs. 3 KStG
6300;is.netIncome.regular.operatingTC.otherCost.miscellaneous;P;sonstige betriebliche Aufwendungen (GKV), andere sonstige betriebliche Aufwendungen;Sonstige betriebliche Aufwendungen
6302;is.netIncome.regular.operatingTC.otherCost.otherOrdinary;P;sonstige betriebliche Aufwendungen (GKV), andere ordentliche sonstige betriebliche Aufwendungen;Interimskonto für Aufwendungen in einem anderen Land, bei denen eine Vorsteuervergütung möglich ist Fremdleistungen/Fremdarbeiten
6304;is.netIncome.regular.operatingTC.otherCost.miscellaneous;P;sonstige betriebliche Aufwendungen (GKV), andere sonstige betriebliche Aufwendungen;Sonstige Aufwendungen betrieblich und regelmäßig
6305;is.netIncome.regular.operatingTC.otherCost.otherOrdinary;P;sonstige betriebliche Aufwendungen (GKV), andere ordentliche sonstige betriebliche Aufwendungen;Raumkosten
6310;is.netIncome.regular.operatingTC.otherCost.leaseFix.other;P;sonstige betriebliche Aufwendungen (GKV), Mietund Pachtaufwendungen für unbewegliche Wirtschaftsgüter, übrige Miete und Pacht für unbewegliche Wirtschaftsgüter;Miete (unbewegliche Wirtschaftsgüter)
6313;is.netIncome.regular.operatingTC.otherCost.leaseFix.shareholders;P;sonstige betriebliche Aufwendungen (GKV), Mietund Pachtaufwendungen für unbewegliche Wirtschaftsgüter, an Gesellschafter;Vergütungen an Gesellschafter für die mietoder pachtweise Überlassung ihrer unbeweglichen Wirtschaftsgüter
6315;is.netIncome.regular.operatingTC.otherCost.leaseFix.other;P;sonstige betriebliche Aufwendungen (GKV), Mietund Pachtaufwendungen für unbewegliche Wirtschaftsgüter, übrige Miete und Pacht für unbewegliche Wirtschaftsgüter;Pacht (unbewegliche Wirtschaftsgüter)
6316;is.netIncome.regular.operatingTC.otherCost.leasingAll.immovable;P;sonstige betriebliche Aufwendungen (GKV), Aufwendungen für Leasing, Leasing für unbewegliche Wirtschaftsgüter;Leasing (unbewegliche Wirtschaftsgüter)
6317;is.netIncome.regular.operatingTC.otherCost.leaseFix.other;P;sonstige betriebliche Aufwendungen (GKV), Mietund Pachtaufwendungen für unbewegliche Wirtschaftsgüter, übrige Miete und Pacht für unbewegliche Wirtschaftsgüter;Aufwendungen für gemietete oder gepachtete unbewegliche Wirtschaftsgüter, die gewerbesteuerlich hinzuzurechnen sind Mietund Pachtnebenkosten, die gewerbesteuerlich nicht hinzuzurechnen sind
6320;is.netIncome.regular.operatingTC.otherCost.energyCost;P;sonstige betriebliche Aufwendungen (GKV), Aufwendungen für Energie;Heizung Gas, Strom, Wasser
6325;+6320+is.netIncome.regular.operatingTC.otherCost.energyCost;P;sonstige betriebliche Aufwendungen (GKV), Aufwendungen für Energie;Heizung Gas, Strom, Wasser
6330;is.netIncome.regular.operatingTC.otherCost.otherOrdinary;P;sonstige betriebliche Aufwendungen (GKV), andere ordentliche sonstige betriebliche Aufwendungen;Reinigung
6335;is.netIncome.regular.operatingTC.otherCost.fixingLandBuildings;P;sonstige betriebliche Aufwendungen (GKV), Aufwand für Fremdreparaturen und Instandhaltung für Grundstücke und Gebäude;Instandhaltung betrieblicher Räume
6340;is.netIncome.regular.operatingTC.otherCost.otherOrdinary;P;sonstige betriebliche Aufwendungen (GKV), andere ordentliche sonstige betriebliche Aufwendungen;Abgaben für betrieblich genutzten Grundbesitz Sonstige Raumkosten Grundstücksaufwendungen betrieblich Sonstige Grundstücksaufwendungen (neutral)
6390;is.netIncome.regular.operatingTC.otherCost.limitedDeductible.other;P;sonstige betriebliche Aufwendungen (GKV), beschränkt abziehbare Betriebsausgaben, sonstige beschränkt abziehbare Betriebsausgaben;Zuwendungen, Spenden, steuerlich nicht abziehbar Zuwendungen, Spenden für wissenschaftliche und kulturelle Zwecke Zuwendungen, Spenden für mildtätige Zwecke Zuwendungen, Spenden für kirchliche, religiöse und gemeinnützige Zwecke Zuwendungen, Spenden an politische Parteien Zuwendungen, Spenden in das zu erhaltende Vermögen (Vermögensstock) einer Stiftung für gemeinnützige Zwecke Zuwendungen, Spenden in das zu erhaltende Vermögen (Vermögensstock) einer Stiftung für kirchliche, religiöse und gemeinnützige Zwecke Zuwendungen, Spenden an Stiftungen in das zu erhaltende Vermögen (Vermögensstock) für wissenschaftliche, mildtätige, kulturelle Zwecke
6400;is.netIncome.regular.operatingTC.otherCost.insurance;P;sonstige betriebliche Aufwendungen (GKV), Versicherungsprämien, Gebühren und Beiträge;Versicherungen Versicherungen für Gebäude Netto-Prämie für Rückdeckung künftiger Versorgungsleistungen Beiträge Sonstige Abgaben
6420;+6400+is.netIncome.regular.operatingTC.otherCost.insurance;P;sonstige betriebliche Aufwendungen (GKV), Versicherungsprämien, Gebühren und Beiträge;Versicherungen Versicherungen für Gebäude Netto-Prämie für Rückdeckung künftiger Versorgungsleistungen Beiträge Sonstige Abgaben
6430;+6400+is.netIncome.regular.operatingTC.otherCost.insurance;P;sonstige betriebliche Aufwendungen (GKV), Versicherungsprämien, Gebühren und Beiträge;Versicherungen Versicherungen für Gebäude Netto-Prämie für Rückdeckung künftiger Versorgungsleistungen Beiträge Sonstige Abgaben
6436;is.netIncome.regular.operatingTC.otherCost.limitedDeductible.other;P;sonstige betriebliche Aufwendungen (GKV), beschränkt abziehbare Betriebsausgaben, sonstige beschränkt abziehbare Betriebsausgaben;Steuerlich abzugsfähige Verspätungszuschläge und Zwangsgelder Steuerlich nicht abzugsfähige Verspätungszuschläge und Zwangsgelder
6440;is.netIncome.regular.operatingTC.otherCost.insurance;P;sonstige betriebliche Aufwendungen (GKV), Versicherungsprämien, Gebühren und Beiträge;Ausgleichsabgabe nach dem Schwerbehindertengesetz
6450;is.netIncome.regular.operatingTC.otherCost.fixingLandBuildings;P;sonstige betriebliche Aufwendungen (GKV), Aufwand für Fremdreparaturen und Instandhaltung für Grundstücke und Gebäude;Reparaturen und Instandhaltung von Bauten
6460;is.netIncome.regular.operatingTC.otherCost.fixing;P;sonstige betriebliche Aufwendungen (GKV), Aufwand für Fremdreparaturen und Instandhaltung (ohne Grundstücke);Reparaturen und Instandhaltung von technischen Anlagen und Maschinen Reparaturen und Instandhaltungen von anderen Anlagen und Betriebsund Geschäftsausstattung
6475;is.netIncome.regular.operatingTC.otherCost.provisions;P;sonstige betriebliche Aufwendungen (GKV), Zuführungen zu Aufwandsrückstellungen;Zuführung zu Aufwandsrückstellungen
6485;is.netIncome.regular.operatingTC.otherCost.fixing;P;sonstige betriebliche Aufwendungen (GKV), Aufwand für Fremdreparaturen und Instandhaltung (ohne Grundstücke);Reparaturen und Instandhaltung von anderen Anlagen Sonstige Reparaturen und Instandhaltungen Wartungskosten für Hardund Software
6490;+6485+is.netIncome.regular.operatingTC.otherCost.fixing;P;sonstige betriebliche Aufwendungen (GKV), Aufwand für Fremdreparaturen und Instandhaltung (ohne Grundstücke);Reparaturen und Instandhaltung von anderen Anlagen Sonstige Reparaturen und Instandhaltungen Wartungskosten für Hardund Software
6498;is.netIncome.regular.operatingTC.otherCost.leasingAll.moveable;P;sonstige betriebliche Aufwendungen (GKV), Aufwendungen für Leasing, Leasing für bewegliche Wirtschaftsgüter;Mietleasing bewegliche Wirtschaftsgüter für technische Anlagen und Maschinen
6520;+6500+is.netIncome.regular.operatingTC.otherCost.vehicles;P;sonstige betriebliche Aufwendungen (GKV), Aufwendungen für den Fuhrpark;Fahrzeugkosten18) Fahrzeug-Versicherungen8) Laufende Fahrzeug-Betriebskosten8) Fahrzeug-Reparaturen8) Garagenmiete
6530;+6500+is.netIncome.regular.operatingTC.otherCost.vehicles;P;sonstige betriebliche Aufwendungen (GKV), Aufwendungen für den Fuhrpark;Fahrzeugkosten18) Fahrzeug-Versicherungen8) Laufende Fahrzeug-Betriebskosten8) Fahrzeug-Reparaturen8) Garagenmiete
6540;+6500+is.netIncome.regular.operatingTC.otherCost.vehicles;P;sonstige betriebliche Aufwendungen (GKV), Aufwendungen für den Fuhrpark;Fahrzeugkosten18) Fahrzeug-Versicherungen8) Laufende Fahrzeug-Betriebskosten8) Fahrzeug-Reparaturen8) Garagenmiete
6500;is.netIncome.regular.operatingTC.otherCost.vehicles;P;sonstige betriebliche Aufwendungen (GKV), Aufwendungen für den Fuhrpark;Fahrzeugkosten18) Fahrzeug-Versicherungen8) Laufende Fahrzeug-Betriebskosten8) Fahrzeug-Reparaturen8) Garagenmiete
6560;is.netIncome.regular.operatingTC.otherCost.leasingAll.moveable;P;sonstige betriebliche Aufwendungen (GKV), Aufwendungen für Leasing, Leasing für bewegliche Wirtschaftsgüter;Mietleasing Kfz Mietleasingaufwendungen für Elektrofahrzeuge und Fahrräder, die gewerbesteuerlich hinzuzurechnen sind8)
6570;is.netIncome.regular.operatingTC.otherCost.vehicles;P;sonstige betriebliche Aufwendungen (GKV), Aufwendungen für den Fuhrpark;Sonstige Fahrzeugkosten8) Mautgebühren Fremdfahrzeugkosten
6600;is.netIncome.regular.operatingTC.otherCost.marketing;P;sonstige betriebliche Aufwendungen (GKV), Werbeaufwand;Werbekosten Streuartikel
6610;is.netIncome.regular.operatingTC.otherCost.limitedDeductible.gifts.deductible;P;sonstige betriebliche Aufwendungen (GKV), beschränkt abziehbare Betriebsausgaben, Aufwendungen für Geschenke, abziehbare Aufwendungen für Geschenke;Geschenke abzugsfähig ohne § 37b EStG Geschenke abzugsfähig mit § 37b EStG Pauschale Steuer für Geschenke und Zuwendungen abzugsfähig
6620;is.netIncome.regular.operatingTC.otherCost.limitedDeductible.gifts.nondeductible;P;sonstige betriebliche Aufwendungen (GKV), beschränkt abziehbare Betriebsausgaben, Aufwendungen für Geschenke, nicht abziehbare Aufwendungen für Geschenke;Geschenke nicht abzugsfähig ohne § 37b EStG Geschenke nicht abzugsfähig mit § 37b EStG Pauschale Steuer für Geschenke und Zuwendungen nicht abzugsfähig
6625;is.netIncome.regular.operatingTC.otherCost.limitedDeductible.gifts.deductible;P;sonstige betriebliche Aufwendungen (GKV), beschränkt abziehbare Betriebsausgaben, Aufwendungen für Geschenke, abziehbare Aufwendungen für Geschenke;Geschenke ausschließlich betrieblich genutzt
6629;is.netIncome.regular.operatingTC.otherCost.marketing;P;sonstige betriebliche Aufwendungen (GKV), Werbeaufwand;Zugaben mit § 37b EStG
6630;is.netIncome.regular.operatingTC.otherCost.otherOrdinary;P;sonstige betriebliche Aufwendungen (GKV), andere ordentliche sonstige betriebliche Aufwendungen;Repräsentationskosten
6640;is.netIncome.regular.operatingTC.otherCost.limitedDeductible.entertainment.deductible;P;sonstige betriebliche Aufwendungen (GKV), beschränkt abziehbare Betriebsausgaben, Bewirtungsaufwendungen, abziehbar;Bewirtungskosten
6641;is.netIncome.regular.operatingTC.otherCost.limitedDeductible.other;P;sonstige betriebliche Aufwendungen (GKV), beschränkt abziehbare Betriebsausgaben, sonstige beschränkt abziehbare Betriebsausgaben;Sonstige eingeschränkt abziehbare Betriebsausgaben (abziehbarer Anteil) Sonstige eingeschränkt abziehbare Betriebsausgaben (nicht abziehbarer Anteil)
6643;is.netIncome.regular.operatingTC.otherCost.marketing;P;sonstige betriebliche Aufwendungen (GKV), Werbeaufwand;Aufmerksamkeiten
6644;is.netIncome.regular.operatingTC.otherCost.limitedDeductible.entertainment.nonDeductible;P;sonstige betriebliche Aufwendungen (GKV), beschränkt abziehbare Betriebsausgaben, Bewirtungsaufwendungen, nicht abziehbar;Nicht abzugsfähige Bewirtungskosten
6645;is.netIncome.regular.operatingTC.otherCost.limitedDeductible.other;P;sonstige betriebliche Aufwendungen (GKV), beschränkt abziehbare Betriebsausgaben, sonstige beschränkt abziehbare Betriebsausgaben;Nicht abzugsfähige Betriebsausgaben aus Werbeund Repräsentationskosten
6650;is.netIncome.regular.operatingTC.otherCost.employee;P;sonstige betriebliche Aufwendungen (GKV), Reisekosten Arbeitnehmer;Reisekosten Arbeitnehmer Reisekosten Arbeitnehmer Übernachtungsaufwand Reisekosten Arbeitnehmer Fahrtkosten Reisekosten Arbeitnehmer Verpflegungsmehraufwand Kilometergelderstattung Arbeitnehmer
6660;+6650+is.netIncome.regular.operatingTC.otherCost.employee;P;sonstige betriebliche Aufwendungen (GKV), Reisekosten Arbeitnehmer;Reisekosten Arbeitnehmer Reisekosten Arbeitnehmer Übernachtungsaufwand Reisekosten Arbeitnehmer Fahrtkosten Reisekosten Arbeitnehmer Verpflegungsmehraufwand Kilometergelderstattung Arbeitnehmer
6663;+6650+is.netIncome.regular.operatingTC.otherCost.employee;P;sonstige betriebliche Aufwendungen (GKV), Reisekosten Arbeitnehmer;Reisekosten Arbeitnehmer Reisekosten Arbeitnehmer Übernachtungsaufwand Reisekosten Arbeitnehmer Fahrtkosten Reisekosten Arbeitnehmer Verpflegungsmehraufwand Kilometergelderstattung Arbeitnehmer
6700;is.netIncome.regular.operatingTC.otherCost.freight;P;sonstige betriebliche Aufwendungen (GKV), Frachten / Verpackung;Kosten der Warenabgabe Verpackungsmaterial Ausgangsfrachten Transportversicherungen
6770;is.netIncome.regular.operatingTC.otherCost.fees;P;sonstige betriebliche Aufwendungen (GKV), Provisionen;Verkaufsprovisionen
6780;is.netIncome.regular.operatingTC.otherCost.otherOrdinary;P;sonstige betriebliche Aufwendungen (GKV), andere ordentliche sonstige betriebliche Aufwendungen;Fremdarbeiten (Vertrieb) Aufwand für Gewährleistungen
6800;is.netIncome.regular.operatingTC.otherCost.communication;P;sonstige betriebliche Aufwendungen (GKV), Aufwendungen für Kommunikation;Porto Telefon Telefax und Internetkosten
6805;+6800+is.netIncome.regular.operatingTC.otherCost.communication;P;sonstige betriebliche Aufwendungen (GKV), Aufwendungen für Kommunikation;Porto Telefon Telefax und Internetkosten
6815;is.netIncome.regular.operatingTC.otherCost.otherOrdinary;P;sonstige betriebliche Aufwendungen (GKV), andere ordentliche sonstige betriebliche Aufwendungen;Bürobedarf
6820;is.netIncome.regular.operatingTC.otherCost.training;P;sonstige betriebliche Aufwendungen (GKV), Fortbildungskosten;Zeitschriften, Bücher (Fachliteratur) Fortbildungskosten
6821;+6820+is.netIncome.regular.operatingTC.otherCost.training;P;sonstige betriebliche Aufwendungen (GKV), Fortbildungskosten;Zeitschriften, Bücher (Fachliteratur) Fortbildungskosten
6822;is.netIncome.regular.operatingTC.otherCost.staffRelated;P;sonstige betriebliche Aufwendungen (GKV), sonstige Aufwendungen für Personal;Freiwillige Sozialleistungen
6825;is.netIncome.regular.operatingTC.otherCost.legalConsulting;P;sonstige betriebliche Aufwendungen (GKV), Rechtsund Beratungskosten;Rechtsund Beratungskosten Abschlussund Prüfungskosten Buchführungskosten
6826;+6825+is.netIncome.regular.operatingTC.otherCost.legalConsulting;P;sonstige betriebliche Aufwendungen (GKV), Rechtsund Beratungskosten;Rechtsund Beratungskosten Abschlussund Prüfungskosten Buchführungskosten
6833;is.netIncome.regular.operatingTC.otherCost.leaseMoveable.shareholders;P;sonstige betriebliche Aufwendungen (GKV), Mietund Pachtaufwendungen für bewegliche Wirtschaftsgüter, an Gesellschafter;Vergütungen an Gesellschafter für die mietoder pachtweise Überlassung ihrer beweglichen Wirtschaftsgüter
6835;is.netIncome.regular.operatingTC.otherCost.leaseMoveable.other;P;sonstige betriebliche Aufwendungen (GKV), Mietund Pachtaufwendungen für bewegliche Wirtschaftsgüter, übrige Miete und Pacht für bewegliche Wirtschaftsgüter;Mieten für Einrichtungen (bewegliche Wirtschaftsgüter) Pacht (bewegliche Wirtschaftsgüter)
6837;is.netIncome.regular.operatingTC.otherCost.concessLicenses;P;sonstige betriebliche Aufwendungen (GKV), Aufwendungen für Konzessionen und Lizenzen;Aufwendungen für die zeitlich befristete Überlassung von Rechten (Lizenzen, Konzessionen)
6838;is.netIncome.regular.operatingTC.otherCost.leaseMoveable.other;P;sonstige betriebliche Aufwendungen (GKV), Mietund Pachtaufwendungen für bewegliche Wirtschaftsgüter, übrige Miete und Pacht für bewegliche Wirtschaftsgüter;Aufwendungen für gemietete oder gepachtete bewegliche Wirtschaftsgüter, die gewerbesteuerlich hinzuzurechnen sind
6840;is.netIncome.regular.operatingTC.otherCost.leasingAll.moveable;P;sonstige betriebliche Aufwendungen (GKV), Aufwendungen für Leasing, Leasing für bewegliche Wirtschaftsgüter;Mietleasing bewegliche Wirtschaftsgüter für Betriebsund Geschäftsausstattung
6845;is.netIncome.regular.operatingTC.otherCost.otherOrdinary;P;sonstige betriebliche Aufwendungen (GKV), andere ordentliche sonstige betriebliche Aufwendungen;Werkzeuge und Kleingeräte Sonstiger Betriebsbedarf Nebenkosten des Geldverkehrs Aufwendungen aus Anteilen an Kapitalgesellschaften §§ 3 Nr. 40 und 3c EStG bzw. § 8b Abs. 1 und 4 KStG9), 16)
6850;+6845+is.netIncome.regular.operatingTC.otherCost.otherOrdinary;P;sonstige betriebliche Aufwendungen (GKV), andere ordentliche sonstige betriebliche Aufwendungen;Werkzeuge und Kleingeräte Sonstiger Betriebsbedarf Nebenkosten des Geldverkehrs Aufwendungen aus Anteilen an Kapitalgesellschaften §§ 3 Nr. 40 und 3c EStG bzw. § 8b Abs. 1 und 4 KStG9), 16)
6855;+6845+is.netIncome.regular.operatingTC.otherCost.otherOrdinary;P;sonstige betriebliche Aufwendungen (GKV), andere ordentliche sonstige betriebliche Aufwendungen;Werkzeuge und Kleingeräte Sonstiger Betriebsbedarf Nebenkosten des Geldverkehrs Aufwendungen aus Anteilen an Kapitalgesellschaften §§ 3 Nr. 40 und 3c EStG bzw. § 8b Abs. 1 und 4 KStG9), 16)
6857;is.netIncome.regular.operatingTC.otherCost.disposalCorp;P;sonstige betriebliche Aufwendungen (GKV), Veräußerungskosten bei Anteilen an Kapitalgesellschaften;Veräußerungskosten § 3 Nr. 40 EStG bzw. § 8b Abs. 2 KStG (bei Veräußerungsgewinn) Veräußerungskosten § 3 Nr. 40 EStG bzw. § 8b Abs. 3 KStG (bei Veräußerungsverlust)
6859;is.netIncome.regular.operatingTC.otherCost.otherOrdinary;P;sonstige betriebliche Aufwendungen (GKV), andere ordentliche sonstige betriebliche Aufwendungen;Aufwendungen für Abraumund Abfallbeseitigung
6860;is.netIncome.regular.operatingTC.otherCost.otherTaxes;P;sonstige betriebliche Aufwendungen (GKV), sonstige Steuern, soweit in den sonstigen Aufwendungen ausgewiesen;Nicht abziehbare Vorsteuer Nicht abziehbare Vorsteuer 7 % Nicht abziehbare Vorsteuer 19 %
6875;is.netIncome.regular.operatingTC.otherCost.limitedDeductible.other;P;sonstige betriebliche Aufwendungen (GKV), beschränkt abziehbare Betriebsausgaben, sonstige beschränkt abziehbare Betriebsausgaben;Nicht abziehbare Hälfte der Aufsichtsratsvergütungen Abziehbare Aufsichtsratsvergütungen
6879;is.netIncome.regular.operatingTC.otherCost.custodyFee;P;sonstige betriebliche Aufwendungen (GKV), Verwahrentgelte;Verwahrentgelt
6880;is.netIncome.regular.operatingTC.otherCost.currLoss;P;sonstige betriebliche Aufwendungen (GKV), Kurs/ Währungsverluste;Aufwendungen aus der Währungsumrechnung Aufwendungen aus der Währungsumrechnung (nicht § 256a HGB) Aufwendungen aus Bewertung Finanzmittelfonds
6884;is.netIncome.regular.operatingTC.otherCost.disposFixAss.sale.tan;P;sonstige betriebliche Aufwendungen (GKV), Verluste aus dem Abgang von Vermögensgegenständen des Anlagevermögens, Erlöse aus Verkäufen des Anlagevermögens, Erlöse aus Verkäufen von Sachanlagen;Erlöse aus Verkäufen Sachanlagevermögen steuerfrei § 4 Nr. 1a UStG (bei Buchverlust) Erlöse aus Verkäufen Sachanlagevermögen 19 % USt (bei Buchverlust) Erlöse aus Verkäufen Sachanlagevermögen steuerfrei § 4 Nr. 1b UStG (bei Buchverlust) Erlöse aus Verkäufen Sachanlagevermögen (bei Buchverlust)
6890;is.netIncome.regular.operatingTC.otherCost.disposFixAss.sale.intan;P;sonstige betriebliche Aufwendungen (GKV), Verluste aus dem Abgang von Vermögensgegenständen des Anlagevermögens, Erlöse aus Verkäufen des Anlagevermögens, Erlöse aus Verkäufen von immateriellen Vermögensgegenständen;Erlöse aus Verkäufen immaterieller Vermögensgegenstände (bei Buchverlust)
6891;is.netIncome.regular.operatingTC.otherCost.disposFixAss.sale.fin;P;sonstige betriebliche Aufwendungen (GKV), Verluste aus dem Abgang von Vermögensgegenständen des Anlagevermögens, Erlöse aus Verkäufen des Anlagevermögens, Erlöse aus Verkäufen von Finanzanlagen;Erlöse aus Verkäufen Finanzanlagen (bei Buchverlust) Erlöse aus Verkäufen Finanzanlagen § 3 Nr. 40 EStG bzw. § 8b Abs. 3 KStG (bei Buchverlust)9)
6895;is.netIncome.regular.operatingTC.otherCost.disposFixAss.bookValue.tan;P;sonstige betriebliche Aufwendungen (GKV), Verluste aus dem Abgang von Vermögensgegenständen des Anlagevermögens, Anlagenabgänge Anlagevermögen, Anlagenabgänge Sachanlagen;Anlagenabgänge Sachanlagen (Restbuchwert bei Buchverlust)
6896;is.netIncome.regular.operatingTC.otherCost.disposFixAss.bookValue.intan;P;sonstige betriebliche Aufwendungen (GKV), Verluste aus dem Abgang von Vermögensgegenständen des Anlagevermögens, Anlagenabgänge Anlagevermögen, Anlagenabgänge immaterielle Vermögensgegenstände;Anlagenabgänge immaterielle Vermögensgegenstände (Restbuchwert bei Buchverlust)
6897;is.netIncome.regular.operatingTC.otherCost.disposFixAss.bookValue.fin;P;sonstige betriebliche Aufwendungen (GKV), Verluste aus dem Abgang von Vermögensgegenständen des Anlagevermögens, Anlagenabgänge Anlagevermögen, Anlagenabgänge Finanzanlagen;Anlagenabgänge Finanzanlagen (Restbuchwert bei Buchverlust) Anlagenabgänge Finanzanlagen § 3 Nr. 40 EStG bzw. § 8b Abs. 3 KStG (Restbuchwert bei Buchverlust)9)
6900;is.netIncome.regular.operatingTC.otherCost.disposFixAss.sale.tan;P;sonstige betriebliche Aufwendungen (GKV), Verluste aus dem Abgang von Vermögensgegenständen des Anlagevermögens, Erlöse aus Verkäufen des Anlagevermögens, Erlöse aus Verkäufen von Sachanlagen;Verluste aus dem Abgang von Gegenständen des Anlagevermögens12)
6903;is.netIncome.regular.operatingTC.otherCost.disposFixAss.sale.fin;P;sonstige betriebliche Aufwendungen (GKV), Verluste aus dem Abgang von Vermögensgegenständen des Anlagevermögens, Erlöse aus Verkäufen des Anlagevermögens, Erlöse aus Verkäufen von Finanzanlagen;Verluste aus der Veräußerung von Anteilen an Kapitalgesellschaften (Finanzanlagevermögen) § 3 Nr. 40 EStG bzw. § 8b Abs. 3 KStG9)
6905;is.netIncome.regular.operatingTC.otherCost.disposCurrAss;P;sonstige betriebliche Aufwendungen (GKV), Verluste aus dem Abgang von Vermögensgegenständen des Umlaufvermögens;Verluste aus dem Abgang von Gegenständen des Umlaufvermögens (außer Vorräte) Verluste aus dem Abgang von Gegenständen des Umlaufvermögens (außer Vorräte) § 3 Nr. 40 EStG bzw. § 8b Abs. 3 KStG9)
6910;is.netIncome.regular.operatingTC.otherCost.regAllowance;P;sonstige betriebliche Aufwendungen (GKV), übliche Abschreibungen auf Forderungen;Abschreibungen auf Umlaufvermögen außer Vorräte und Wertpapiere des Umlaufvermögens (übliche Höhe) Abschreibungen auf Umlaufvermögen außer Vorräte und Wertpapiere des Umlaufvermögens, steuerrechtlich bedingt (übliche Höhe)
6918;is.netIncome.regular.operatingTC.otherCost.otherOrdinary;P;sonstige betriebliche Aufwendungen (GKV), andere ordentliche sonstige betriebliche Aufwendungen;Aufwendungen aus dem Erwerb eigener Anteile
6920;is.netIncome.regular.operatingTC.otherCost.transferValuatonPresentYear.global;P;sonstige betriebliche Aufwendungen (GKV), Aufwand aus Wertberichtigungen des lfd. Jahres, Pauschalwertberichtigungen des lfd. Jahres;Einstellung in die Pauschalwertberichtigung auf Forderungen
6922;is.netIncome.regular.operatingTC.otherCost.addPreTaxRes.EStG6b_3;P;sonstige betriebliche Aufwendungen (GKV), Einstellung in steuerliche Rücklagen, § 6b Abs. 3 EStG;Einstellungen in die steuerliche Rücklage nach § 6b Abs. 3 EStG
6923;is.netIncome.regular.operatingTC.otherCost.transferValuatonPresentYear.specific;P;sonstige betriebliche Aufwendungen (GKV), Aufwand aus Wertberichtigungen des lfd. Jahres, Einzelwertberichtigungen des lfd. Jahres;Einstellung in die Einzelwertberichtigung auf Forderungen
6927;is.netIncome.regular.operatingTC.otherCost.addPreTaxRes.other;P;sonstige betriebliche Aufwendungen (GKV), Einstellung in steuerliche Rücklagen, übrige Einstellung in steuerliche Rücklagen;Einstellungen in sonstige steuerliche Rücklagen
6928;is.netIncome.regular.operatingTC.otherCost.addPreTaxRes.substEStR6_6;P;sonstige betriebliche Aufwendungen (GKV), Einstellung in steuerliche Rücklagen, Rücklage für Ersatzbeschaffung, R 6.6 EStR;Einstellungen in die Rücklage für Ersatzbeschaffung nach R 6.6 EStR
6929;is.netIncome.regular.operatingTC.otherCost.addPreTaxRes.EStG4g;P;sonstige betriebliche Aufwendungen (GKV), Einstellung in steuerliche Rücklagen, § 4g EStG;Einstellungen in die steuerliche Rücklage nach § 4g EStG
6930;is.netIncome.regular.operatingTC.otherCost.regAllowance;P;sonstige betriebliche Aufwendungen (GKV), übliche Abschreibungen auf Forderungen;Forderungsverluste (übliche Höhe) Forderungsverluste 7 % USt (übliche Höhe) Forderungsverluste aus steuerfreien EU-Lieferungen (übliche Höhe) Forderungsverluste aus im Inland steuerpflichtigen EU-Lieferungen 7 % USt (übliche Höhe) Forderungsverluste 19 % USt (übliche Höhe) Forderungsverluste aus im Inland steuerpflichtigen EU-Lieferungen 19 % USt (übliche Höhe)
6960;is.netIncome.regular.operatingTC.otherCost.otherOrdinary;P;sonstige betriebliche Aufwendungen (GKV), andere ordentliche sonstige betriebliche Aufwendungen;Periodenfremde Aufwendungen
6967;is.netIncome.regular.operatingTC.otherCost.miscellaneous;P;sonstige betriebliche Aufwendungen (GKV), andere sonstige betriebliche Aufwendungen;Sonstige Aufwendungen betriebsfremd und regelmäßig
6968;is.netIncome.regular.operatingTC.otherCost.otherOrdinary;P;sonstige betriebliche Aufwendungen (GKV), andere ordentliche sonstige betriebliche Aufwendungen;Sonstige nicht abziehbare Aufwendungen
6969;is.netIncome.regular.operatingTC.otherCost.miscellaneous;P;sonstige betriebliche Aufwendungen (GKV), andere sonstige betriebliche Aufwendungen;Sonstige Aufwendungen unregelmäßig
6970;is.netIncome.regular.operatingTC.otherCost.otherOrdinary;P;sonstige betriebliche Aufwendungen (GKV), andere ordentliche sonstige betriebliche Aufwendungen;Kalkulatorischer Unternehmerlohn Kalkulatorische Miete und Pacht Kalkulatorische Zinsen Kalkulatorische Abschreibungen Kalkulatorische Wagnisse Kalkulatorischer Lohn für unentgeltliche Mitarbeiter Verrechneter kalkulatorischer Unternehmerlohn Verrechnete kalkulatorische Miete/Pacht Verrechnete kalkulatorische Zinsen Verrechnete kalkulatorische Abschreibungen Verrechnete kalkulatorische Wagnisse Verrechneter kalkulatorischer Lohn für unentgeltliche Mitarbeiter
6990;is.netIncome.regular.operatingTC.otherCost.misc;A;sonstige betriebliche Aufwendungen (GKV), nicht zuordenbar;Herstellungskosten Verwaltungskosten
7000;is.netIncome.regular.fin.netParticipation.earnings.other;A;Erträge aus Beteiligungen, nach Rechtsform der Beteiligung nicht zuordenbar;Erträge aus Beteiligungen
7002;is.netIncome.regular.fin.netParticipation.earnings.silentPart;P;Erträge aus Beteiligungen, Erträge aus stillen Beteiligungen;Erträge aus typisch stillen Beteiligungen
7003;is.netIncome.regular.fin.commPart;P;Gewinnanteil aus Beteiligungen an Mitunternehmerschaften;Erträge aus atypisch stillen Beteiligungen23) Erträge aus Beteiligungen an Personengesellschaften (verbundene Unternehmen), § 9 GewStG bzw. § 18 EStG23)
7005;is.netIncome.regular.fin.netParticipation.earnings.corporations;P;Erträge aus Beteiligungen, an Kapitalgesellschaften;Erträge aus Anteilen an Kapitalgesellschaften (Beteiligung) § 3 Nr. 40 EStG bzw. § 8b Abs. 1 KStG9) Erträge aus Anteilen an Kapitalgesellschaften (verbundene Unternehmen) § 3 Nr. 40 EStG bzw. § 8b Abs. 1 KStG9)
7008;is.netIncome.regular.fin.commPart;P;Gewinnanteil aus Beteiligungen an Mitunternehmerschaften;Gewinnanteile aus gewerblichen und selbständigen Mitunternehmerschaften, § 9 GewStG bzw. § 18 EStG23)
7009;is.netIncome.regular.fin.netParticipation.earnings.other;A;Erträge aus Beteiligungen, nach Rechtsform der Beteiligung nicht zuordenbar;Erträge aus Beteiligungen an verbundenen Unternehmen
7011;+7009+is.netIncome.regular.fin.netParticipation.earnings.other;A;Erträge aus Beteiligungen, nach Rechtsform der Beteiligung nicht zuordenbar;Erträge aus Beteiligungen an verbundenen Unternehmen
7010;is.netIncome.regular.fin.netParticipation.earningSecurities.shareholder;P;Erträge aus anderen Wertpapieren und Ausleihungen des Finanzanlagevermögens, Erträge aus Ausleihungen an Gesellschaften und Gesellschafter [KapG / Mitunternehmer (PersG)];Erträge aus anderen Wertpapieren und Ausleihungen des Finanzanlagevermögens Erträge aus Ausleihungen des Finanzanlagevermögens Erträge aus Ausleihungen des Finanzanlagevermögens an verbundenen Unternehmen
7013;is.netIncome.regular.fin.netParticipation.earningSecurities.partnerships;P;Erträge aus anderen Wertpapieren und Ausleihungen des Finanzanlagevermögens, Erträge aus Beteiligungen an Personengesellschaften;Erträge aus Anteilen an Personengesellschaften (Finanzanlagevermögen)
7014;is.netIncome.regular.fin.netParticipation.earningSecurities.corporations;P;Erträge aus anderen Wertpapieren und Ausleihungen des Finanzanlagevermögens, Erträge aus Beteiligungen an Kapitalgesellschaften;Erträge aus Anteilen an Kapitalgesellschaften (Finanzanlagevermögen) § 3 Nr. 40 EStG bzw. § 8b Abs. 1 und 4 KStG9) Erträge aus Anteilen an Kapitalgesellschaften (verbundene Unternehmen) § 3 Nr. 40 EStG bzw. § 8b Abs. 1 KStG9)
7016;is.netIncome.regular.fin.netParticipation.earningSecurities.partnerships;P;Erträge aus anderen Wertpapieren und Ausleihungen des Finanzanlagevermögens, Erträge aus Beteiligungen an Personengesellschaften;Erträge aus Anteilen an Personengesellschaften (verbundene Unternehmen)
7017;is.netIncome.regular.fin.netParticipation.earningSecurities.corporations;P;Erträge aus anderen Wertpapieren und Ausleihungen des Finanzanlagevermögens, Erträge aus Beteiligungen an Kapitalgesellschaften;Erträge aus anderen Wertpapieren des Finanzanlagevermögens an Kapitalgesellschaften (verbundene Unternehmen)
7018;is.netIncome.regular.fin.netParticipation.earningSecurities.partnerships;P;Erträge aus anderen Wertpapieren und Ausleihungen des Finanzanlagevermögens, Erträge aus Beteiligungen an Personengesellschaften;Erträge aus anderen Wertpapieren des Finanzanlagevermögens an Personengesellschaften (verbundene Unternehmen)
7019;is.netIncome.regular.fin.netParticipation.earningSecurities.shareholder;P;Erträge aus anderen Wertpapieren und Ausleihungen des Finanzanlagevermögens, Erträge aus Ausleihungen an Gesellschaften und Gesellschafter [KapG / Mitunternehmer (PersG)];Erträge aus anderen Wertpapieren und Ausleihungen des Finanzanlagevermögens aus verbundenen Unternehmen
7020;is.netIncome.regular.fin.netParticipation.earningSecurities.interestDividend.nonAllocable;A;Erträge aus anderen Wertpapieren und Ausleihungen des Finanzanlagevermögens, Zinsund Dividendenerträge, nicht zuordenbar;Zinsund Dividendenerträge
7030;is.netIncome.regular.fin.netParticipation.earningSecurities.minorInterestReceived;P;Erträge aus anderen Wertpapieren und Ausleihungen des Finanzanlagevermögens, erhaltene Ausgleichszahlungen (als außenstehender Aktionär);Erhaltene Ausgleichszahlungen (als außenstehender Aktionär)
7100;is.netIncome.regular.fin.netInterest.income.deposits.otherMisc;A;sonstige Zinsen und ähnliche Erträge, Zinsen auf Einlagen bei Kreditinstituten und auf Forderungen an Dritte, nicht zuordenbare Zinsen;Sonstige Zinsen und ähnliche Erträge
7103;is.netIncome.regular.fin.netInterest.income.securities.dividends;P;sonstige Zinsen und ähnliche Erträge, Zinsund Dividendenerträge aus Wertpapieren des Umlaufvermögens, Dividendenerträge;Erträge aus Anteilen an Kapitalgesellschaften (Umlaufvermögen) § 3 Nr. 40 EStG bzw. § 8b Abs. 1 und 4 KStG9) Erträge aus Anteilen an Kapitalgesellschaften (verbundene Unternehmen) § 3 Nr. 40 EStG bzw. § 8b Abs. 1 KStG9)
7105;is.netIncome.regular.fin.netInterest.income.deposits.AO233a;P;sonstige Zinsen und ähnliche Erträge, Zinsen auf Einlagen bei Kreditinstituten und auf Forderungen an Dritte, Zinsen nach § 233a AO;Zinserträge § 233a AO, steuerpflichtig Zinserträge § 233a AO, steuerfrei (Anlage GK KSt) Zinserträge § 233a AO und § 4 Abs. 5b EStG, steuerfrei
7109;is.netIncome.regular.fin.netInterest.income.deposits.otherMisc;A;sonstige Zinsen und ähnliche Erträge, Zinsen auf Einlagen bei Kreditinstituten und auf Forderungen an Dritte, nicht zuordenbare Zinsen;Sonstige Zinsen und ähnliche Erträge aus verbundenen Unternehmen Sonstige Zinserträge
7115;is.netIncome.regular.fin.netInterest.income.securities.interest;P;sonstige Zinsen und ähnliche Erträge, Zinsund Dividendenerträge aus Wertpapieren des Umlaufvermögens, Zinserträge;Erträge aus anderen Wertpapieren und Ausleihungen des Umlaufvermögens
7119;---xxx---;A;sonstige Zinsen und ähnliche Erträge, Zinsen auf Einlagen bei Kreditinstituten und auf Forderungen an Dritte, nicht zuordenbare Zinsen sonstige Zinsen und ähnliche Erträge, Erträge aus Abzinsung;Sonstige Zinserträge aus verbundenen Unternehmen Zinsähnliche Erträge
7129;is.netIncome.regular.fin.netInterest.income.deposits.otherMisc;A;sonstige Zinsen und ähnliche Erträge, Zinsen auf Einlagen bei Kreditinstituten und auf Forderungen an Dritte, nicht zuordenbare Zinsen;Zinsähnliche Erträge aus verbundenen Unternehmen
7130;is.netIncome.regular.fin.netInterest.income.discount;P;sonstige Zinsen und ähnliche Erträge, Diskonterträge;Diskonterträge Diskonterträge aus verbundenen Unternehmen
7140;is.netIncome.regular.fin.netInterest.income.valueDiscount;P;sonstige Zinsen und ähnliche Erträge, Erträge aus Abzinsung;Steuerfreie Zinserträge aus der Abzinsung von Rückstellungen Zinserträge aus der Abzinsung von Verbindlichkeiten Zinserträge aus der Abzinsung von Rückstellungen Zinserträge aus der Abzinsung von Pensionsrückstellungen und ähnlichen/vergleichbaren Verpflichtungen
7141;+7140+is.netIncome.regular.fin.netInterest.income.valueDiscount;P;sonstige Zinsen und ähnliche Erträge, Erträge aus Abzinsung;Steuerfreie Zinserträge aus der Abzinsung von Rückstellungen Zinserträge aus der Abzinsung von Verbindlichkeiten Zinserträge aus der Abzinsung von Rückstellungen Zinserträge aus der Abzinsung von Pensionsrückstellungen und ähnlichen/vergleichbaren Verpflichtungen
7144;is.netIncome.regular.fin.netInterest.income.offsetAssets;P;sonstige Zinsen und ähnliche Erträge, im Zusammenhang mit Vermögensverrechnung;Zinserträge aus der Abzinsung von Pensionsrückstellungen und ähnlichen/vergleichbaren Verpflichtungen zur Verrechnung nach § 246 Abs. 2 HGB Erträge aus Vermögensgegenständen zur Verrechnung nach § 246 Abs. 2 HGB
7190;is.netIncome.incomeSharing.loss;P;Verlustbzw. Gewinnabführung (Tochter), Erträge aus Verlustübernahme;Erträge aus Verlustübernahme
7192;is.netIncome.regular.fin.netParticipation.earningProfSharing;P;Aufgrund einer Gewinngemeinschaft, eines Gewinnabführungsoder Teilgewinnabführungsvertrags erhaltene Gewinne (Mutter);Erhaltene Gewinne auf Grund einer Gewinngemeinschaft Erhaltene Gewinne auf Grund eines Gewinnoder Teilgewinnabführungsvertrags
7200;is.netIncome.regular.fin.netParticipation.amortFinanc.financialsExcept.misc;A;Abschreibungen auf Finanzanlagen und auf Wertpapiere des Umlaufvermögens, außerplanmäßige Abschreibungen auf Finanzanlagen, nicht zuordenbar;Abschreibungen auf Finanzanlagen (dauerhaft) Abschreibungen auf Finanzanlagen (nicht dauerhaft) Abschreibungen auf Finanzanlagen § 3 Nr. 40 EStG bzw. § 8b Abs. 3 KStG (dauerhaft)9) Abschreibungen auf Finanzanlagen verbundene Unternehmen
7208;is.netIncome.regular.fin.lossCommPart;P;Verlustanteil aus Beteiligungen an Mitunternehmerschaften;Aufwendungen auf Grund von Verlustanteilen an gewerblichen und selbständigen Mitunternehmerschaften, § 8 GewStG bzw. § 18 EStG23)
7210;is.netIncome.regular.fin.netParticipation.amortFinanc.secCurrAss;P;Abschreibungen auf Finanzanlagen und auf Wertpapiere des Umlaufvermögens, übliche und unübliche Abschreibungen auf Wertpapiere des Umlaufvermögens;Abschreibungen auf Wertpapiere des Umlaufvermögens Abschreibungen auf Wertpapiere des Umlaufvermögens § 3 Nr. 40 EStG bzw. § 8b Abs. 3 KStG9) Abschreibungen auf Wertpapiere des Umlaufvermögens verbundene Unternehmen
7250;is.netIncome.regular.fin.netParticipation.amortFinanc.other;A;Abschreibungen auf Finanzanlagen und auf Wertpapiere des Umlaufvermögens, nicht zuordenbar;Abschreibungen auf Finanzanlagen auf Grund § 6b EStG-Rücklage Abschreibungen auf Finanzanlagen auf Grund § 6b EStG-Rücklage, § 3 Nr. 40 EStG bzw. § 8b Abs. 3 KStG9)
7300;is.netIncome.regular.fin.netInterest.expenses.regularInterest.other;P;Zinsen und ähnliche Aufwendungen, Zinsen, Übrige Zinsaufwendungen;Zinsen und ähnliche Aufwendungen
7302;is.netIncome.regular.fin.netInterest.expenses.regularInterest.relatedPayments;P;Zinsen und ähnliche Aufwendungen, Zinsen, andere Nebenleistungen zu Steuern;Steuerlich nicht abzugsfähige andere Nebenleistungen zu Steuern § 4 Abs. 5b EStG Steuerlich abzugsfähige andere Nebenleistungen zu Steuern Steuerlich nicht abzugsfähige andere Nebenleistungen zu Steuern
7303;+7302+is.netIncome.regular.fin.netInterest.expenses.regularInterest.relatedPayments;P;Zinsen und ähnliche Aufwendungen, Zinsen, andere Nebenleistungen zu Steuern;Steuerlich nicht abzugsfähige andere Nebenleistungen zu Steuern § 4 Abs. 5b EStG Steuerlich abzugsfähige andere Nebenleistungen zu Steuern Steuerlich nicht abzugsfähige andere Nebenleistungen zu Steuern
7305;is.netIncome.regular.fin.netInterest.expenses.regularInterest.AO233a;P;Zinsen und ähnliche Aufwendungen, Zinsen, Zinsen nach § 233a AO;Zinsaufwendungen § 233a AO abzugsfähig
7306;---xxx---;P;Zinsen und ähnliche Aufwendungen, Zinsen, Zinsen nach §§ 234 bis 237 AO Zinsen und ähnliche Aufwendungen, sonstige Zinsen und ähnliche Aufwendungen aus Abzinsung;Zinsaufwendungen §§ 234 bis 237 AO nicht abzugsfähig
7308;is.netIncome.regular.fin.netInterest.expenses.regularInterest.AO233a;P;Zinsen und ähnliche Aufwendungen, Zinsen, Zinsen nach § 233a AO;Zinsaufwendungen § 233a AO nicht abzugsfähig
7309;is.netIncome.regular.fin.netInterest.expenses.regularInterest.other;P;Zinsen und ähnliche Aufwendungen, Zinsen, Übrige Zinsaufwendungen;Zinsaufwendungen an verbundene Unternehmen Zinsaufwendungen für kurzfristige Verbindlichkeiten
7311;is.netIncome.regular.fin.netInterest.expenses.regularInterest.AO234to237;P;Zinsen und ähnliche Aufwendungen, Zinsen, Zinsen nach §§ 234 bis 237 AO;Zinsaufwendungen §§ 234 bis 237 AO abzugsfähig
7316;is.netIncome.regular.fin.netInterest.expenses.regularInterest.PartnersLoans.other;P;Zinsen und ähnliche Aufwendungen, Zinsen, Zinsen für Gesellschafterdarlehen, Übrige Zinsen für Gesellschafterdarlehen;Zinsen für Gesellschafterdarlehen
7317;is.netIncome.regular.fin.netInterest.expenses.regularInterest.PartnersLoans.participationOver25pt;P;Zinsen und ähnliche Aufwendungen, Zinsen, Zinsen für Gesellschafterdarlehen, Zinsen an Gesellschafter mit einer Beteiligung von mehr als 25 % bzw. diesen nahe stehenden Personen;Zinsen an Gesellschafter mit einer Beteiligung von mehr als 25 % bzw. diesen nahe stehende Personen
7318;is.netIncome.regular.fin.netInterest.expenses.regularInterest.other;P;Zinsen und ähnliche Aufwendungen, Zinsen, Übrige Zinsaufwendungen;Zinsen auf Kontokorrentkonten Zinsaufwendungen für kurzfristige Verbindlichkeiten an verbundene Unternehmen
7323;is.netIncome.regular.fin.netInterest.expenses.amortDiscount;P;Zinsen und ähnliche Aufwendungen, Abschreibungen auf ein Agio, Disagio oder Damnum;Abschreibungen auf ein Agio oder Disagio/Damnum zur Finanzierung Abschreibungen auf ein Agio oder Disagio/Damnum zur Finanzierung des Anlagevermögens
7325;is.netIncome.regular.fin.netInterest.expenses.regularInterest.misc;A;Zinsen und ähnliche Aufwendungen, Zinsen, nicht zuordenbare Zinsaufwendungen;Zinsaufwendungen für Gebäude, die zum Betriebsvermögen gehören Zinsen zur Finanzierung des Anlagevermögens
7327;is.netIncome.regular.fin.netInterest.expenses.annuities;P;Zinsen und ähnliche Aufwendungen, Renten und dauernde Lasten;Renten und dauernde Lasten
7329;is.netIncome.regular.fin.netInterest.expenses.regularInterest.other;P;Zinsen und ähnliche Aufwendungen, Zinsen, Übrige Zinsaufwendungen;Zinsaufwendungen für langfristige Verbindlichkeiten an verbundene Unternehmen
7330;is.netIncome.regular.fin.netInterest.expenses.misc;A;Zinsen und ähnliche Aufwendungen, nicht zuordenbar;Zinsähnliche Aufwendungen Zinsähnliche Aufwendungen an verbundene Unternehmen
7340;is.netIncome.regular.fin.netInterest.expenses.discount;P;Zinsen und ähnliche Aufwendungen, Diskontaufwendungen;Diskontaufwendungen Diskontaufwendungen an verbundene Unternehmen
7350;is.netIncome.regular.fin.netInterest.expenses.regularInterest.other;P;Zinsen und ähnliche Aufwendungen, Zinsen, Übrige Zinsaufwendungen;Zinsen und ähnliche Aufwendungen §§ 3 Nr. 40 und 3c EStG bzw. § 8b Abs. 1 und Abs. 4 KStG9), 16) Zinsen und ähnliche Aufwendungen an verbundene Unternehmen §§ 3 Nr. 40 und 3c EStG bzw. § 8b Abs. 1 KStG9), 16)
7355;is.netIncome.regular.fin.netInterest.expenses.loanFees;P;Zinsen und ähnliche Aufwendungen, Kreditprovisionen und Verwaltungskostenbeiträge;Kreditprovisionen und Verwaltungskostenbeiträge
7360;is.netIncome.regular.fin.netInterest.expenses.calcInterestOnPensProv;P;Zinsen und ähnliche Aufwendungen, Zinsanteil der Zuführungen zu Pensionsrückstellungen;Zinsanteil der Zuführungen zu Pensionsrückstellungen
7361;is.netIncome.regular.fin.netInterest.expenses.valueDiscount;P;Zinsen und ähnliche Aufwendungen, sonstige Zinsen und ähnliche Aufwendungen aus Abzinsung;Zinsaufwendungen aus der Abzinsung von Verbindlichkeiten Zinsaufwendungen aus der Abzinsung von Rückstellungen Zinsaufwendungen aus der Abzinsung von Pensionsrückstellungen und ähnlichen/vergleichbaren Verpflichtungen
7364;---xxx---;P;Zinsen und ähnliche Aufwendungen, Ersonstige Zinsen und ähnliche Aufwendungen im Zusammenhang mit der Vermögensverrechnung;Zinsaufwendungen aus der Abzinsung von Pensionsrückstellungen und ähnlichen/vergleichbaren Verpflichtungen zur Verrechnung nach § 246 Abs. 2 HGB Aufwendungen aus Vermögensgegenständen zur Verrechnung nach § 246 Abs. 2 HGB
7366;is.netIncome.regular.fin.netInterest.expenses.valueDiscount;P;Zinsen und ähnliche Aufwendungen, sonstige Zinsen und ähnliche Aufwendungen aus Abzinsung;Steuerlich nicht abzugsfähige Zinsaufwendungen aus der Abzinsung von Rückstellungen
7390;is.netIncome.regular.fin.netParticipation.loss;P;Aufwendungen aus Verlustübernahmen (Mutter);Aufwendungen aus Verlustübernahme
7392; aufgrund einer Gewinngemeinschaft, eines Gewinnabführungsoder Teilgewinnabführungsvertrags abgeführte Gewinne;P;Verlustbzw. Gewinnabführung (Tochter); aufgrund einer Gewinngemeinschaft, eines Gewinnabführungsoder Teilgewinnabführungsvertrags abgeführte Gewinne;Abgeführte Gewinne auf Grund einer Gewinngemeinschaft Abgeführte Gewinne auf Grund eines Gewinnoder Teilgewinnabführungsvertrags
7451;is.netIncome.extraord.income.merger;P;sonstige betriebliche Erträge (GKV), Erträge durch Verschmelzung und andere Umwandlungen;Erträge durch Verschmelzung und Umwandlung
7454;is.netIncome.regular.operatingTC.otherOpRevenue.nonAllocable;A;sonstige betriebliche Erträge (GKV), nicht zuordenbar;Gewinn aus der Veräußerung oder der Aufgabe von Geschäftsaktivitäten nach Steuern11)
7460;---xxx---;P;sonstige betriebliche Erträge (GKV), Erträge nach Art. 67 Abs. 1 und 2 EGHGB onstige betriebliche Aufwendungen sonstige betriebliche Aufwendungen (GKV), andere ordentliche sonstige betriebliche Aufwendungen;Erträge aus der Anwendung von Übergangsvorschriften Erträge aus der Anwendung von Übergangsvorschriften (latente Steuern)
7551;is.netIncome.regular.operatingTC.otherCost.merger;P;sonstige betriebliche Aufwendungen (GKV), Verluste durch Verschmelzung und andere Umwandlungen;Verluste durch Verschmelzung und Umwandlung
7552;is.netIncome.regular.operatingTC.otherCost.otherOrdinary;P;sonstige betriebliche Aufwendungen (GKV), andere ordentliche sonstige betriebliche Aufwendungen;Verluste durch außergewöhnliche Schadensfälle (nur Bilanzierer)11)
7553;is.netIncome.regular.operatingTC.otherCost.restructuring;P;sonstige betriebliche Aufwendungen (GKV), Aufwendungen für Restrukturierungsund Sanierungsmaßnahmen;Aufwendungen für Restrukturierungsund Sanierungsmaßnahmen
7554;is.netIncome.regular.operatingTC.otherCost.otherOrdinary;P;sonstige betriebliche Aufwendungen (GKV), andere ordentliche sonstige betriebliche Aufwendungen;Verluste aus der Veräußerung oder der Aufgabe von Geschäftsaktivitäten nach Steuern11)
7560;is.netIncome.regular.operatingTC.otherCost.EGHGB;P;sonstige betriebliche Aufwendungen (GKV), Aufwendungen nach Art. 67 Abs. 1 und 2 EGHGB;Aufwendungen aus der Anwendung von Übergangsvorschriften Aufwendungen aus der Anwendung von Übergangsvorschriften (Pensionsrückstellungen) Aufwendungen aus der Anwendung von Übergangsvorschriften (Latente Steuern)
7600;is.netIncome.tax.kst;P;Steuern vom Einkommen und vom Ertrag, Körperschaftsteuer;Körperschaftsteuer
7603;is.netIncome.tax.prevPeriodPaid;P;Steuern vom Einkommen und vom Ertrag, Steuernachzahlungen für Vorjahre;Körperschaftsteuer für Vorjahre
7604;is.netIncome.tax.prevPeriodReceived;P;Steuern vom Einkommen und vom Ertrag, Steuererstattungen für Vorjahre;Körperschaftsteuererstattungen für Vorjahre Solidaritätszuschlagerstattungen für Vorjahre
7608;is.netIncome.tax.soli;P;Steuern vom Einkommen und vom Ertrag, Solidaritätszuschlag;Solidaritätszuschlag
7609;is.netIncome.tax.prevPeriodPaid;P;Steuern vom Einkommen und vom Ertrag, Steuernachzahlungen für Vorjahre;Solidaritätszuschlag für Vorjahre
7610;is.netIncome.tax.gewst;P;Steuern vom Einkommen und vom Ertrag, Gewerbesteuer;Gewerbesteuer
7630;is.netIncome.tax.kest;P;Steuern vom Einkommen und vom Ertrag, Kapitalertragsteuer;Kapitalertragsteuer 25 %
7633;is.netIncome.tax.soli;P;Steuern vom Einkommen und vom Ertrag, Solidaritätszuschlag;Anrechenbarer Solidaritätszuschlag auf Kapitalertragsteuer 25 %
7638;is.netIncome.tax.nonDeductableForeignIncomeTaxes;P;Steuern vom Einkommen und vom Ertrag, nicht anrechenbare ausländische Steuern;Ausländische Steuer auf im Inland steuerfreie DBA-Einkünfte
7639;+7788+bs.eqLiab.equity.netIncome;P;Bilanzgewinn / Bilanzverlust (GuV); Jahresüberschuss/-fehlbetrag, Ergebnisverwendung;Änderung steuerlicher Ausgleichsposten (Körperschaften)8)
7639;-is.netIncome.tax.deductableForeignIncomeTaxes;P;Steuern vom Einkommen und vom Ertrag, anrechenbare ausländische Steuern;Anrechnung / Abzug ausländische Quellensteuer
7641;is.netIncome.tax.prevPeriodPaid;P;Steuern vom Einkommen und vom Ertrag, Steuernachzahlungen für Vorjahre;Gewerbesteuernachzahlungen und Gewerbesteuererstattungen für Vorjahre nach § 4 Abs. 5b EStG
7643;is.netIncome.tax.releaseTaxProv;P;Steuern vom Einkommen und vom Ertrag, Erträge aus der Auflösung von Steuerrückstellungen;Erträge aus der Auflösung von Gewerbesteuerrückstellungen nach § 4 Abs. 5b EStG
7645;is.netIncome.tax.deferred;P;Steuern vom Einkommen und vom Ertrag, bilanzierte latente Steuern;Aufwendungen aus der Zuführung und Auflösung von latenten Steuern
7646;is.netIncome.tax.otherIncomeTaxes;P;Steuern vom Einkommen und vom Ertrag, sonstige Steuern;Aufwendungen aus der Zuführung zu Steuerrückstellungen für Steuerstundung (BStBK)
7648;is.netIncome.tax.releaseTaxProv;P;Steuern vom Einkommen und vom Ertrag, Erträge aus der Auflösung von Steuerrückstellungen;Erträge aus der Auflösung von Steuerrückstellungen für Steuerstundung (BStBK)
7649;is.netIncome.tax.deferred;P;Steuern vom Einkommen und vom Ertrag, bilanzierte latente Steuern;Erträge aus der Zuführung und Auflösung von latenten Steuern
7650;is.netIncome.otherTaxes;P;sonstige Steuern;Sonstige Betriebssteuern Verbrauchsteuer (sonstige Steuern) Ökosteuer Grundsteuer Kfz-Steuer Steuernachzahlungen Vorjahre für sonstige Steuern Steuererstattungen Vorjahre für sonstige Steuern Erträge aus der Auflösung von Rückstellungen für sonstige Steuern
7700;incomeUse.gainLoss.retainedEarningsPrevYear;P;Bilanzgewinn / Bilanzverlust (GuV), Gewinnvortrag aus dem Vorjahr;Gewinnvortrag nach Verwendung Verlustvortrag nach Verwendung
7720;+7700+incomeUse.gainLoss.retainedEarningsPrevYear;P;Bilanzgewinn / Bilanzverlust (GuV), Gewinnvortrag aus dem Vorjahr;Gewinnvortrag nach Verwendung Verlustvortrag nach Verwendung
7730;incomeUse.gainLoss.releaseCapReserves;P;Bilanzgewinn / Bilanzverlust (GuV), Entnahmen aus der Kapitalrücklage;Entnahmen aus der Kapitalrücklage
7735;incomeUse.gainLoss.releaseRevenReserves.legalRes;P;Bilanzgewinn / Bilanzverlust (GuV), Entnahmen aus Gewinnrücklagen, Entnahmen aus der gesetzlichen Rücklage;Entnahmen aus der gesetzlichen Rücklage
7743;incomeUse.gainLoss.releaseRevenReserves.sharesParentCompRes;P;Bilanzgewinn / Bilanzverlust (GuV), Entnahmen aus Gewinnrücklagen, Entnahmen aus der Rücklage für Anteile an einem herrschenden oder mehrheitlich beteiligten Unternehmen;Entnahmen aus der Rücklage für Anteile an einem herrschenden oder mehrheitlich beteiligten Unternehmen
7745;incomeUse.gainLoss.releaseRevenReserves.statRes;P;Bilanzgewinn / Bilanzverlust (GuV), Entnahmen aus Gewinnrücklagen, Entnahmen aus satzungsmäßigen Rücklagen;Entnahmen aus satzungsmäßigen Rücklagen
7750;incomeUse.gainLoss.releaseOtherRes;P;Bilanzgewinn / Bilanzverlust (GuV), Entnahmen aus Gewinnrücklagen, Entnahmen aus anderen Gewinnrücklagen;Entnahmen aus anderen Gewinnrücklagen
7755;incomeUse.gainLoss.releaseCapital;P;Bilanzgewinn / Bilanzverlust (GuV), Erträge aus der Kapitalherabsetzung;Erträge aus Kapitalherabsetzung
7760;incomeUse.gainLoss.releaseCapitalReserve;P;Bilanzgewinn / Bilanzverlust (GuV), Einstellung in die Kapitalrücklage nach den Vorschriften über die vereinfachte Kapitalherabsetzung;Einstellungen in die Kapitalrücklage nach den Vorschriften über die vereinfachte Kapitalherabsetzung
7765;incomeUse.gainLoss.additionRevenReserves.legalRes;P;Bilanzgewinn / Bilanzverlust (GuV), Einstellungen in Gewinnrücklagen, Einstellungen in die gesetzliche Rücklage;Einstellungen in die gesetzliche Rücklage
7773;incomeUse.gainLoss.additionRevenReserves.sharesParentCompRes;P;Bilanzgewinn / Bilanzverlust (GuV), Einstellungen in Gewinnrücklagen, Einstellungen in die Rücklage für Anteile an einem herrschenden oder mehrheitlich beteiligten Unternehmen;Einstellungen in die Rücklage für Anteile an einem herrschenden oder mehrheitlich beteiligten Unternehmen
7775;incomeUse.gainLoss.additionRevenReserves.statRes;P;Bilanzgewinn / Bilanzverlust (GuV), Einstellungen in Gewinnrücklagen, Einstellungen in die satzungsmäßigen Rücklagen;Einstellungen in satzungsmäßige Rücklagen
7780;incomeUse.gainLoss.additionOtherRes;P;Bilanzgewinn / Bilanzverlust (GuV), Einstellungen in Gewinnrücklagen, Einstellungen in andere Gewinnrücklagen;Einstellungen in andere Gewinnrücklagen
7788;Jahresüberschuss/-fehlbetrag, Ergebnisverwendung;P;Bilanzgewinn / Bilanzverlust (GuV); Jahresüberschuss/-fehlbetrag, Ergebnisverwendung;Änderung steuerlicher Ausgleichsposten (Körperschaften)8)
7790;incomeUse.gainLoss.dividensPlanned;P;Bilanzgewinn / Bilanzverlust (GuV), Vorabausschüttung / beschlossene Ausschüttung für das Geschäftsjahr;Vorabausschüttung
7800;is.netIncome.regular.operatingTC.otherCost.miscellaneous;P;sonstige betriebliche Aufwendungen (GKV), andere sonstige betriebliche Aufwendungen;(zur freien Verfügung)
8000;is.netIncome.regular.operatingTC.otherCost.misc;A;sonstige betriebliche Aufwendungen (GKV), nicht zuordenbar;Zur freien Verfügung
9258; Jahresüberschuss/-fehlbetrag, Ergebnisverwendung;P;Bilanzgewinn / Bilanzverlust (GuV); Jahresüberschuss/-fehlbetrag, Ergebnisverwendung;Änderung steuerlicher Ausgleichsposten (ohne Ergebnisverwendung Körperschaften)11) Kurzfristige Rückstellungen Mittelfristige Rückstellungen Langfristige Rückstellungen, außer Pensionen Gegenkonto zu Konten 9260-9268 Gegenkonto zu Konten 9271-9279 (Soll-Buchung) Verbindlichkeiten aus der Begebung und Übertragung von Wechseln Verbindlichkeiten aus der Begebung und Übertragung von Wechseln gegenüber verbundenen/assoziierten Unternehmen Verbindlichkeiten aus Bürgschaften, Wechselund Scheckbürgschaften Verbindlichkeiten aus Bürgschaften, Wechselund Scheckbürgschaften gegenüber verbundenen/assoziierten Unternehmen Verbindlichkeiten aus Gewährleistungsverträgen Verbindlichkeiten aus Gewährleistungsverträgen gegenüber verbundenen/assoziierten Unternehmen Haftung aus der Bestellung von Sicherheiten für fremde Verbindlichkeiten Haftung aus der Bestellung von Sicherheiten für fremde Verbindlichkeiten gegenüber verbundenen/assoziierten Unternehmen Verpflichtungen aus Treuhandvermögen Gegenkonto zu 9281-9284 Verpflichtungen aus Mietund Leasingverträgen Verpflichtungen aus Mietund Leasingverträgen gegenüber verbundenen Unternehmen Andere Verpflichtungen nach § 285 Nr. 3a HGB Andere Verpflichtungen nach § 285 Nr. 3a HGB gegenüber verbundenen Unternehmen Unterschiedsbetrag aus der Abzinsung von Altersversorgungsverpflichtungen nach § 253 Abs. 6 HGB (Haben) Gegenkonto zu 9285
9292;bs.eqLiab.liab.trade.genOther;P;Verbindlichkeiten aus Lieferungen und Leistungen, übrige Verbindlichkeiten;Statistisches Konto Fremdgeld
9293;---xxx---;P;sonstige Verbindlichkeiten, übrige sonstige Verbindlichkeiten ter Aufzulösender Auffangposten;Gegenkonto zu 9292 Einlagen atypisch stiller Gesellschafter
9297;bs.eqLiab.equity.netIncome.taxBalanceGenerally.finalPrev;P;Eigenkapital, steuerlicher Ausgleichsposten, steuerlicher Ausgleichsposten des letzten Stichtags;Steuerlicher Ausgleichsposten (Körperschaften)17) Statistische Konten für den Kennziffernteil Bilanz/BWA7) Statistische Konten für den Kennziffernteil Bilanz/BWA7) Statistische Konten für den Kennziffernteil Bilanz/BWA7) Statistische Konten für den Kennziffernteil Bilanz/BWA7) Statistische Konten für den Kennziffernteil Bilanz/BWA7) Statistische Konten für den Kennziffernteil Bilanz/BWA7) Konto für Branchenlösungen (Werte 1), (Zur freien Verfügung)24) Konto für Branchenlösungen (Werte 2), (Zur freien Verfügung)24) Konto für Branchenlösungen (Werte 3), (Zur freien Verfügung)24) Konto für Branchenlösungen (Werte 4), (Zur freien Verfügung)24) Gegenkonto für Branchenlösungen (Werte), (Zur freien Verfügung)24) Konto für Branchenlösungen (Menge 1), (Zur freien Verfügung)7) Konto für Branchenlösungen (Menge 2), (Zur freien Verfügung)7) Konto für Branchenlösungen (Menge 3), (Zur freien Verfügung)7) Konto für Branchenlösungen (Menge 4), (Zur freien Verfügung)7) Gegenkonto für Branchenlösungen (Menge), (Zur freien Verfügung)7) Statistisches Konto für den Gewinnzuschlag nach §§ 6b und 6c EStG (Haben) Statistisches Konto für den Gewinnzuschlag nach §§ 6b und 6c EStG (Soll) Gegenkonto zu 9890 Hinzurechnung Investitionsabzugsbetrag § 7g Abs. 2 EStG aus dem 4. vorangegangenen Wirtschaftsjahr, außerbilanziell (Haben) Rückgängigmachung Investitionsabzugsbetrag § 7g Abs. 3 und 4 EStG im 4. vorangegangenen Wirtschaftsjahr Hinzurechnung Investitionsabzugsbetrag § 7g Abs. 2 EStG aus dem 2. vorangegangenen Wirtschaftsjahr, außerbilanziell (Haben) Hinzurechnung Investitionsabzugsbetrag § 7g Abs. 2 EStG aus dem 3. vorangegangenen Wirtschaftsjahr, außerbilanziell (Haben) Rückgängigmachung Investitionsabzugsbetrag § 7g Abs. 3 und 4 EStG im 2. vorangegangenen Wirtschaftsjahr
9960;bs.ass.currAss.receiv.trade.other;P;Forderungen aus Lieferungen und Leistungen, übrige Forderungen;Bewertungskorrektur zu Forderungen aus Lieferungen und Leistungen
9961;bs.eqLiab.liab.other.other;P;sonstige Verbindlichkeiten, übrige sonstige Verbindlichkeiten;Bewertungskorrektur zu sonstigen Verbindlichkeiten
9962; Guthaben bei Kreditinstituten;P;Kassenbestand, Bundesbankguthaben, Guthaben bei Kreditinstituten und Schecks; Guthaben bei Kreditinstituten;Bewertungskorrektur zu Guthaben bei Kreditinstituten
9963;bs.eqLiab.liab.bank.other;P;Verbindlichkeiten gegenüber Kreditinstituten, übrige;Bewertungskorrektur zu Verbindlichkeiten gegenüber Kreditinstituten
9964;bs.eqLiab.liab.trade.genOther;P;Verbindlichkeiten aus Lieferungen und Leistungen, übrige Verbindlichkeiten;Bewertungskorrektur zu Verbindlichkeiten aus Lieferungen und Leistungen
9965;bs.ass.currAss.receiv.other.other;P;Forderungen und sonstige Vermögensgegenstände, sonstige Vermögensgegenstände, übrige sonstige Vermögensgegenstände;Bewertungskorrektur zu sonstigen Vermögensgegenständen Hinzurechnung Investitionsabzugsbetrag § 7g Abs. 2 EStG aus dem 6. vorangegangenen Wirtschaftsjahr, außerbilanziell (Haben)1) Rückgängigmachung Investitionsabzugsbetrag § 7g Abs. 3 und 4 EStG im 6. vorangegangenen Wirtschaftsjahr1) Hinzurechnung Investitionsabzugsbetrag § 7g Abs. 2 EStG aus dem 5. vorangegangenen Wirtschaftsjahr, außerbilanziell (Haben) Rückgängigmachung Investitionsabzugsbetrag § 7g Abs. 3 und 4 EStG im 5. vorangegangenen Wirtschaftsjahr Investitionsabzugsbetrag § 7g Abs. 1 EStG, außerbilanziell (Soll) Investitionsabzugsbetrag § 7g Abs. 1 EStG, außerbilanziell (Haben) Gegenkonto zu 9970 Hinzurechnung Investitionsabzugsbetrag § 7g Abs. 2 EStG aus dem vorangegangenen Wirtschaftsjahr, außerbilanziell (Haben) Hinzurechnung Investitionsabzugsbetrag § 7g Abs. 2 EStG aus den vorangegangenen Wirtschaftsjahren, außerbilanziell (Soll) Gegenkonto zu 9972, 9914, 9916, 9917, 9968, 99668) Rückgängigmachung Investitionsabzugsbetrag § 7g Abs. 3 und 4 EStG im vorangegangenen Wirtschaftsjahr Rückgängigmachung Investitionsabzugsbetrag § 7g Abs. 3 und 4 EStG in den vorangegangenen Wirtschaftsjahren Gegenkonto zu 9974, 9915, 9918, 9919, 9969, 99678) Nicht abzugsfähige Zinsaufwendungen nach § 4h EStG (Haben) Nicht abzugsfähige Zinsaufwendungen nach § 4h EStG (Soll) Gegenkonto zu 9976 Abziehbare Zinsaufwendungen aus Vorjahren nach § 4h EStG (Soll) Abziehbare Zinsaufwendungen aus Vorjahren nach § 4h EStG (Haben) Gegenkonto zu 9978
2080;++bs.eqLiab.equity.revenueRes.unappropriated.otherMeansDueCourse.finalPrev;P;freie RÜcklage bis Vorjahr
2082;++bs.eqLiab.equity.revenueRes.unappropriated.otherMeansDueCourse.changePresentYear;P;freie RÜcklage Änderung lfd. Jahr


''')


#**********************************************************************************************

if __name__ == "__main__":

    Bilanz().base_bilanz(*(sys.argv[1:]))
    
