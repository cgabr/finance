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
            for file in glob.glob("*.ps") + glob.glob("*.ps~") + glob.glob("*.kto") + glob.glob("*.kto.html"):
                os.unlink(file);

            if jahr == jahr1:
                break
            jahr = "%02u" % (int(jahr)+1)


#*****************************************************************************************************

    def base_bilanz1 (self,name,bez,jahr,WITH_BWA): 

        kto  = Konto(self.ktotyp)

        self.ini_text = self.ebilanz_ini(jahr)

        text = "BILANZ " + name + ", Jahr 20" + jahr
        kto.read_saldo("10-:"+jahr)
        text_10 = kto.salden_text()
        text    = text + "\nXXAKTIVA   " + text_10

        kto.read_saldo("11-:"+jahr)
        text_11 = kto.salden_text()
        text1   = "\nXXPASSIVA  " + text_11
#        text1 = "\nXXPASSIVA  " + os.popen("grep -P '^(\S+|     ) +(\S+) *$' *kto").read()
        text1 = re.sub(r" (\-?\d+\.\d\d)","-\\1",text1,999999)  #  Minuszeichen
        text1 = re.sub(r" --","   ",text1,999999)
        text  = text + text1

        kto.read_saldo("12-."+jahr)
        text_12 = kto.salden_text()
#        text1 = "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\f\nXXERTRAG " + os.popen("grep -P '^(\S+|     ) +(\S+) *$' *kto").read()
        text1 = "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\f\nXXERTRAG " + text_12
        text1 = re.sub(r" (\-?\d+\.\d\d)","-\\1",text1,999999)  #  Minuszeichen
        text1 = re.sub(r" --","   ",text1,999999)
        text  = text + text1

        kto.read_saldo("13-."+jahr)
        text_13 = kto.salden_text()
#        text  = text + "\nXXAUFWAND" + re.sub(r"Do","Xo",os.popen("grep -P '^(\S+|     ) +(\S+) *$' *kto").read(),99999999)
        text  = text + "\nXXAUFWAND" + re.sub(r"Do","Xo",text_13,99999999)

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


# --- fuer anlagenspiegel: ------

        kto = Konto()
        kto.read_saldo("10-A11-:"+jahr)
        anlagen_current = kto.salden_text()
        kto.read_saldo("10-A11-:"+("%02u"%(int(jahr)-1)))
        anlagen_previous = kto.salden_text()
        
#        print(anlagen_current)
#        exit()

#---------------------------

        text = text + text_add

        text = re.sub(r"( .\d+\.\d\d)","                                                      \\1",text,99999999)
        text = re.sub(r"\nXX([A-Z]+)        ([^\n]+)","\n\n\n\\1\\2\n=======\n",text,9999)

        Konto(self.ktotyp).kto("^12-."+jahr)
        einnahmen = open((glob.glob("*kto")+glob.glob("*kto.html"))[0]).read()

        Konto(self.ktotyp).kto("^13-."+jahr)
        ausgaben = open((glob.glob("*kto")+glob.glob("*kto.html"))[0]).read()

        Konto(self.ktotyp).kto("^10-A11-."+jahr)
        anlagen = open((glob.glob("*kto")+glob.glob("*kto.html"))[0]).read()

        Konto(self.ktotyp).kto("^11-C13-3060-."+jahr)
        ust = open((glob.glob("*kto")+glob.glob("*kto.html"))[0]).read()

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
                                                                        "C02: Steuerliches Einlagenkonto               ",text,1)
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

        text = re.sub(r"D4a                                           ","\n"+
                                                                        "D4a: Gewinne Beteiligungen                     ",text,1)
        text = re.sub(r"D..-7001                                      ","  7001   Gewinn 12park                         ",text)



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

        text = re.sub(r"D8b                                           ","\n"+
                                                                        "D8b: Verlust Beteiligungen                   ",text,1)
        text = re.sub(r"D..-6291                                      ","  6291   Verlust 12park                        ",text)


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

        text_orig = text1
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

#             print(text6)
            
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
 
#-------------------------------------------

        file = jahr + "_bilanz_"+bez+"__20" + jahr
        open(file + ".md","w").write(text1)


        if os.path.isdir("kn"+jahr):   #  Kontennachweise:
        
            ktogruppe = 9
            for text2 in (text_10,text_11,text_12,text_13):
                ktogruppe = "%02u" % (int(ktogruppe)+1)
                for zeile in text1.split("\n"):
                    m = re.search(r"  (\d\d\d\d)  ",zeile)
                    if m:
                        ktoblatt = m.group(1)
                        m = re.search("\n([A-Z]\S\S\-"+ktoblatt+")  ",text2)
                        if m:
                            if ktogruppe in ("10","11"):
                                Konto().kto("^"+ktogruppe+"-"+m.group(1)+":"+jahr)
                            else:
                                Konto().kto("^"+ktogruppe+"-"+m.group(1)+"."+jahr)
                            ktofile1 = (glob.glob("*kto") + glob.glob("*kto.html"))[0]
                            os.system("mv " + ktofile1 + " kn" + jahr + "/" + ktoblatt + ".kto.html")
        
#--------------  E-BILANZ: ----------------

#        text2 = {}
        text4        = ""
        faktor       = 1.0
        thisyear     = 0.00
        gvvortrag    = 0.00
        difference   = 0.00
        stammkapital = 0.00
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
            elif "JAHRESERGEBNIS" in zeile:
                faktor = -1.0
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
                if m1.group(1) == "2080":
                    thisyear = float(m1.group(3))
                    continue
                if m1.group(1) == "2900":
                    stammkapital = float(m1.group(3))
                if m1.group(1) == "7639":
                    difference = float(m1.group(3))
                if m1.group(1) in ("2970","2971","2972","2978"):
                    gvvortrag  = gvvortrag + float(m1.group(3))
                text4 = text4 + m1.group(1) + ";" + ("%3.2f"%(faktor*float(m1.group(3)))) + ";\"" + m1.group(2).strip() + "\"\n"
                
        if int(jahr) > 17:
            text4 = text4 + "2085;" + ("%3.2f"%(-thisyear-stammkapital-gvvortrag+difference))  + ";\"Beginn Periode\"\n"
            text4 = text4 + "2087;" + ("%3.2f"%(-thisyear-stammkapital-gvvortrag)) + ";\"Ende Periode\"\n"
        text4 = text4 + "2082;" + ("%3.2f"%(-thisyear+difference)) + ";\"Kumulierte Erloese Beginn der Periode\"\n"

        open("j" + file + ".csv","w").write(text4)
        
        text2 = self.ini_text
        text2 = re.sub(r"---JAHR---",jahr,text2)
        text2 = re.sub(r"---JFILE---","j"+file+".csv",text2)
        if int(jahr) > 16:
            text2 = re.sub(r"---TAXO---",{"17":"6.1","18":"6.2","19":"6.3","20":"6.4","21":"6.5","22":"6.6","23":"6.6"}[jahr],text2)
            
   #  Anlagenspiegel:

        anl_data  = {}
        anl_arten = []
        i         = -1
        for anlagen in (anlagen_previous,anlagen_current):
            i = i + 1
            for zeile in anlagen.split("\n"):
                m = re.search(r"^(\d\d\d\d)\-(.*?)\-(AN|AS) +(\-?\d+\.\d\d)",zeile)
                if m:
                    item = m.group(1)+"-"+m.group(2)
                    nr   = m.group(1)
                    art  = m.group(3)
                    if not item in anl_data:
                        anl_data[item] = [0.00,0.00,0.00,0.00,nr]
                    anl_data[item][int(art=="AS")*2+i] = float(m.group(4))
                    m = re.search(item+"AN +(\-?\d+\.\d\d)",anlagen_current)

        anl_data1 = {}
        anl_arten = {}
        for item in anl_data:
            if anl_data[item][0] == anl_data[item][1] == -anl_data[item][2] == -anl_data[item][3]:
                continue
            print(item,anl_data[item])
            nr = anl_data[item][4]
            anl_arten[nr] = 1
            if not (nr+"I") in anl_data1:
                for pos in ("I","J","K","L"):
                    anl_data1[nr+pos] = 0.00
            anl_data1[nr+"I"] = anl_data1[nr+"I"] + anl_data[item][0]    #   anfangsbestand anfang periode (AN)
            anl_data1[nr+"J"] = anl_data1[nr+"J"] + anl_data[item][1]    #   anfangsbestand ende periode (AN)   
            anl_data1[nr+"K"] = anl_data1[nr+"K"] + anl_data[item][2]    #   abschreibung bis anfang periode  
            anl_data1[nr+"L"] = anl_data1[nr+"L"] + anl_data[item][3]    #   abschreibung bis ende periode
                    
        for nr in anl_arten:
            anl_data1[nr+"A"] =     anl_data1[nr+"I"] 
            anl_data1[nr+"B"] =     anl_data1[nr+"J"] - anl_data1[nr+"I"]   #  Differenz im Anfangsbestand (AN)
            anl_data1[nr+"C"] = -   anl_data1[nr+"K"]                       #  Abschreibungen bis Anfang Periode
            anl_data1[nr+"D"] = - ( anl_data1[nr+"L"] - anl_data1[nr+"K"])  #  Abschreibung laufende Periode
            anl_data1[nr+"E"] =     anl_data1[nr+"I"] + anl_data1[nr+"K"]   #  Endbestand Vorperiode, konsolidiert, AN minus AS
            
            
            for pos in ("A","B","C","D","E"):
                betr1 = "%3.2f" % anl_data1[nr+pos]
                if betr1 == "-0.00":
                    betr1 = "0.00"
                text2 = text2.replace("-"+nr+pos+"-",betr1)
        print(anl_data1)


        text2 = re.sub("\n\-?de-gaap-ci:.*?\!.*?\[\-.*?\-\].*?\n","\n",text2,9999)
        text2 = re.sub("\n\-?de-gaap-ci:.*?\!.*?\[\-.*?\-\].*?\n","\n",text2,9999)
        text2 = re.sub("\n\-?de-gaap-ci:.*?\!.*?\[\-.*?\-\].*?\n","\n",text2,9999)

        
        open("i" + file + ".ini","w").write(text2)
        
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


    def ebilanz_ini(self,jahr):

        erg = '''
[magic]
myebilanz=true
guid=88D4E913-584C-41AC-AB2E-7CC6CA01063C

[general]
Transferdatenlieferant=IfT GmbH;Nuernberger Str.;134;;;90762;Fuerth;Deutschland;(0911) 148781-11;finanz@ift-informatik.de
Nutzdatenlieferant=IfT GmbH;Nuernberger Str.;134;;;90762;Fuerth;Deutschland;(0911) 148781-11;finanz@ift-informatik.de

[cert]
file=/home/cgabriel/25_ift/37_steuern/elster/IfT_elster_2022.pfx
pin=IfT9372

[mysql]
server=127.0.0.1
port=4136
username=nurlesen
password=nurlesen%1
db=mand3
select=SELECT k.KtoNr, k.Saldo+k.SSaldo AS Saldo, k.KtoBezeichnung FROM sg_fib_konten k INNER JOIN sg_fib_wijahre w ON k.SG_FIB_WiJahre_FK=w.SG_FIB_WiJahre_PK WHERE LENGTH(k.KtoNr)=4 and w.WirtschaftsjahrBez='#JAHR#' HAVING Saldo<>0.00 ORDER BY KtoNr;

[csv]
filename=/home/cgabriel/25_ift/99_bilanz/---JFILE---
delimiter=;
fieldKto=1
fieldValue=2
fieldName=3
fieldValueDebit=0
fieldValueCredit=0
fieldXBRL=0

[period]
balSheetClosingDate=20---JAHR----12-31


[report]
reportType=JA
reportStatus=E
revisionStatus=E
reportElements=GuV,-GuVMicroBilG,B,-SGE,-KS,-STU,-EB,-EV,-SGEP,-KKE,BAL,BVV,-SA,-AV
statementType=E
statementTypeTax=-GHB
incomeStatementendswithBalProfit=false
accountingStandard=HAOE
specialAccountingStandard=K
incomeStatementFormat=GKV
consolidationRange=EA
taxonomy=---TAXO---
MicroBilG=0

[company]
name=IfT GmbH
legalStatus=GMBH
street=Nuernberger Str.
houseNo=134
zipCode=90762
city=Fuerth
country=Deutschland
ST13=9218012910296
STID=
BF4=9218
incomeClassification=trade
business=Beratung

[xbrloriginal]
de-gaap-ci:bs.ass.fixAss.intan.concessionBrands=100
de-gaap-ci:bs.ass.fixAss.tan.landBuildings.misc=200
de-gaap-ci:bs.ass.fixAss.tan.landBuildings.buildingsOnOwnLand.buildings=300
de-gaap-ci:bs.ass.fixAss.tan.machinery=400
de-gaap-ci:bs.ass.fixAss.tan.otherEquipm.other=500
de-gaap-ci:bs.ass.fixAss.tan.inConstrAdvPaym=700
de-gaap-ci:bs.ass.fixAss.fin.sharesInAffil.other=800
de-gaap-ci:bs.ass.fixAss.fin.securities=900
de-gaap-ci:bs.ass.currAss.inventory.material=1000
de-gaap-ci:bs.ass.currAss.inventory.finishedAndMerch=1100
de-gaap-ci:bs.ass.currAss.receiv.trade.other=1200
de-gaap-ci:bs.ass.currAss.receiv.other.misc=1300
de-gaap-ci:bs.ass.currAss.receiv.other.vat=1400
de-gaap-ci:bs.ass.currAss.securities.affil=1500
de-gaap-ci:bs.ass.currAss.cashEquiv.cash=1600
de-gaap-ci:bs.ass.currAss.cashEquiv.bank=1700,1800
de-gaap-ci:bs.ass.prepaidExp=1900
de-gaap-ci:bs.ass.defTax=2000,2100,2200,2300,2400,2500,2600,2700,2800
de-gaap-ci:bs.eqLiab.equity.subscribed.corp=2900
de-gaap-ci:bs.eqLiab.accruals.pensions.direct=3000
de-gaap-ci:bs.eqLiab.liab.securities=3100
de-gaap-ci:bs.eqLiab.liab.trade.genOther=3300
de-gaap-ci:bs.eqLiab.liab.assocComp=3400
de-gaap-ci:bs.eqLiab.liab.other.other=3500,3600
de-gaap-ci:bs.eqLiab.liab.other.theroffTax=3700,3800
de-gaap-ci:bs.eqLiab.defIncome=3900
de-gaap-ci:is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.unknownVAT=4000,4200,4500
de-gaap-ci:is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.taxExemptUStG4_8.other=4100
de-gaap-ci:is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.reducedRateVAT=4300
de-gaap-ci:is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.generalRateVAT=4400
de-gaap-ci:is.netIncome.regular.operatingTC.otherOpRevenue.ownConsumption.otherWithdrawals=4600
de-gaap-ci:is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.unknownVAT=4700
de-gaap-ci:is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.inventoryChange=4800
de-gaap-ci:is.netIncome.regular.operatingTC.otherOpRevenue.disposFixAss.sale.tan=4900
de-gaap-ci:is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.unknownVAT=5000,5200,5600,5700,5800
de-gaap-ci:is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.unknownVAT=5100
de-gaap-ci:is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.reducedRateVAT=5300
de-gaap-ci:is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.generalRateVAT=5400
de-gaap-ci:is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.intraEU=5500
de-gaap-ci:is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.services.unknownVAT=5900
de-gaap-ci:is.netIncome.regular.operatingTC.staff.salaries.misc=6000
de-gaap-ci:is.netIncome.regular.operatingTC.staff.social.other=6100
de-gaap-ci:is.netIncome.regular.operatingTC.deprAmort.fixAss.otherIntan=6200
de-gaap-ci:is.netIncome.regular.operatingTC.otherCost.miscellaneous=6300
de-gaap-ci:is.netIncome.regular.operatingTC.otherCost.insurance=6400
de-gaap-ci:is.netIncome.regular.operatingTC.otherCost.vehicles=6500
de-gaap-ci:is.netIncome.regular.operatingTC.otherCost.marketing=6600
de-gaap-ci:is.netIncome.regular.operatingTC.otherCost.freight=6700
de-gaap-ci:is.netIncome.regular.operatingTC.otherCost.communication=6800
de-gaap-ci:is.netIncome.regular.operatingTC.otherCost.disposFixAss.sale.tan=6900
de-gaap-ci:is.netIncome.regular.fin.netParticipation.earnings.other=7000
de-gaap-ci:is.netIncome.regular.fin.netInterest.income.deposits.banks=7100
de-gaap-ci:is.netIncome.regular.fin.netParticipation.amortFinanc.financialsExcept.misc=7200
de-gaap-ci:is.netIncome.regular.fin.netInterest.expenses.regularInterest.other=7300
de-gaap-ci:is.netIncome.incomeSharing.gain=7400
de-gaap-ci:is.netIncome.extraord.income.EGHGB=7500
de-gaap-ci:is.netIncome.tax.kst=7600
de-gaap-ci:incomeUse.gainLoss.retainedEarningsPrevYear=7700
de-gaap-ci:incomeUse.gainLoss.dividensPlanned=7800,7900,8000,8100,8200,8300,8400,8500,8600,8700,8800,8900
de-gaap-ci:bs.eqLiab.equity.netIncome=0
ignore=9000,9008,9009
de-gaap-ci:BVV.profitLoss.assetsPreviousYear.assets=2900,2970,2978,2010,2050,2060
de-gaap-ci:BVV.profitLoss.withdrawalDistrib=2100,2500
de-gaap-ci:BVV.profitLoss.contribution=2180,2580
de-gaap-ci:BVV.profitLoss.assetsCurrentYear=0,2900,2970,2978,2010,2050,2060,2100,2500,2180,2580
de-gaap-ci:bs.eqLiab.liab.bank.other=3200

[xbrl]
de-gaap-ci:bs.ass.fixAss.intan.concessionBrands=100
de-gaap-ci:bs.ass.fixAss.tan.landBuildings=300
de-gaap-ci:bs.ass.fixAss.tan.machinery=400
de-gaap-ci:bs.ass.fixAss.tan.otherEquipm.other=500
de-gaap-ci:bs.ass.fixAss.tan.otherEquipm.gwgsammelposten=675
de-gaap-ci:bs.ass.fixAss.tan.inConstrAdvPaym=700
de-gaap-ci:bs.ass.fixAss.fin.sharesInAffil.other=800
de-gaap-ci:bs.ass.fixAss.fin.securities=900
de-gaap-ci:bs.ass.fixAss.tan.otherEquipm.passengerCars=520
de-gaap-ci:bs.ass.fixAss.tan.otherEquipm.otherTransportMeans=560
de-gaap-ci:bs.ass.currAss.inventory.material=1000
de-gaap-ci:bs.ass.currAss.inventory.finishedAndMerch=1100
de-gaap-ci:bs.ass.currAss.receiv.trade=1200,1210
de-gaap-ci:bs.ass.currAss.receiv.affil=3695
de-gaap-ci:bs.ass.currAss.receiv.other.secondaryPaym=1300
de-gaap-ci:bs.ass.currAss.receiv.other.employees=1340
de-gaap-ci:bs.ass.currAss.receiv.other.other=1355
de-gaap-ci:bs.ass.currAss.receiv.other.socInsur=1361,1457
de-gaap-ci:bs.ass.currAss.receiv.other.tradeTaxOverpayment=1435
de-gaap-ci:bs.ass.currAss.receiv.other.vat=1400
de-gaap-ci:bs.ass.currAss.securities.affil=1500
de-gaap-ci:bs.ass.currAss.cashEquiv.cash=1600
de-gaap-ci:bs.ass.currAss.cashEquiv.bank=1700,1800,1801,1802,1803,1804,1805,1806,1807,1808,1809,1810,1891
de-gaap-ci:bs.ass.currAss.cashEquiv.other=1890
de-gaap-ci:bs.ass.prepaidExp=1900
de-gaap-ci:bs.ass.defTax=2000,2100,2200,2300,2400,2500,2600,2700,2800
de-gaap-ci:bs.eqLiab.accruals.pensions.direct=3000
de-gaap-ci:bs.eqLiab.accruals.tax.gewst=3035
de-gaap-ci:bs.eqLiab.accruals.tax.kst=3040
de-gaap-ci:bs.eqLiab.accruals.tax.other=3050,3060
de-gaap-ci:bs.eqLiab.accruals.tax.additionalTax=3065
de-gaap-ci:bs.eqLiab.liab.securities=3100
de-gaap-ci:bs.eqLiab.liab.assocComp=3400
de-gaap-ci:bs.eqLiab.liab.other.other=3500,3600
de-gaap-ci:bs.eqLiab.liab.other.theroffTax=3800,3751
de-gaap-ci:bs.eqLiab.liab.other.thereoffSocSec=3740,3759
de-gaap-ci:is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.unknownVAT=4000,4200,4500
de-gaap-ci:is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.taxExemptUStG4_8.other=4100
de-gaap-ci:is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.reducedRateVAT=4300
de-gaap-ci:is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.grossSales.generalRateVAT=4400
de-gaap-ci:is.netIncome.regular.operatingTC.otherOpRevenue.ownConsumption.otherWithdrawals=4600
de-gaap-ci:is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.netSales.reductionsFromGrossSales.unknownVAT=4700
de-gaap-ci:is.netIncome.regular.operatingTC.grossTradingProfit.totalOutput.inventoryChange=4800
de-gaap-ci:is.netIncome.regular.operatingTC.otherOpRevenue.disposFixAss.sale.tan=4900
de-gaap-ci:is.netIncome.regular.operatingTC.otherOpRevenue.ownConsumption.nonCashBenefitsCompCar=4947
de-gaap-ci:is.netIncome.regular.operatingTC.otherOpRevenue.ownConsumption.nonCashBenefitsOther=4982
de-gaap-ci:is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.unknownVAT=5000,5200,5600,5700,5800
de-gaap-ci:is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.rawMatConsSup.unknownVAT=5100
de-gaap-ci:is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.reducedRateVAT=5300
de-gaap-ci:is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.generalRateVAT=5400
de-gaap-ci:is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.material.purchased.intraEU=5500
de-gaap-ci:is.netIncome.regular.operatingTC.grossTradingProfit.materialServices.services.unknownVAT=5900
de-gaap-ci:is.netIncome.regular.operatingTC.staff.salaries.misc=6000,6010
de-gaap-ci:is.netIncome.regular.operatingTC.staff.salaries.inKind=6020
de-gaap-ci:is.netIncome.regular.operatingTC.staff.social.other=6100,6110
de-gaap-ci:is.netIncome.regular.operatingTC.deprAmort.fixAss.otherIntan=6200
de-gaap-ci:is.netIncome.regular.operatingTC.deprAmort.fixAss.tan.otherMisc=6220
de-gaap-ci:is.netIncome.regular.operatingTC.otherCost.miscellaneous=6300,6850,6851,6855,6611
de-gaap-ci:is.netIncome.regular.operatingTC.otherCost.leaseFix.other=6310
de-gaap-ci:is.netIncome.regular.operatingTC.otherCost.energyCost=6325
de-gaap-ci:is.netIncome.regular.operatingTC.otherCost.insurance=6400,6420
de-gaap-ci:is.netIncome.regular.operatingTC.otherCost.fees=6011,6430,6436
de-gaap-ci:is.netIncome.regular.operatingTC.otherCost.otherOrdinary=6485,6845
de-gaap-ci:is.netIncome.regular.operatingTC.otherCost.fixing=6450,6470,6490
de-gaap-ci:is.netIncome.regular.operatingTC.otherCost.vehicles=6500,6520,6530,6540,6570
de-gaap-ci:is.netIncome.regular.operatingTC.otherCost.leasingAll.moveable=6560,6595
de-gaap-ci:is.netIncome.regular.operatingTC.otherCost.marketing=6600,6643
de-gaap-ci:is.netIncome.regular.operatingTC.otherCost.limitedDeductible.entertainment.deductible=6640
de-gaap-ci:is.netIncome.regular.operatingTC.otherCost.employee=6660,6663
de-gaap-ci:is.netIncome.regular.operatingTC.otherCost.administration=6815
de-gaap-ci:is.netIncome.regular.operatingTC.otherCost.freight=6700,5840
de-gaap-ci:is.netIncome.regular.operatingTC.otherCost.communication=6800,6805
de-gaap-ci:is.netIncome.regular.operatingTC.otherCost.training=6820,6821
de-gaap-ci:is.netIncome.regular.operatingTC.otherCost.staffRelated=6822
de-gaap-ci:is.netIncome.regular.operatingTC.otherCost.legalConsulting=6825,6826
-de-gaap-ci:is.netIncome.regular.operatingTC.otherCost.concessLicenses=6837
de-gaap-ci:is.netIncome.regular.operatingTC.otherCost.disposFixAss.sale.tan=6900
-de-gaap-ci:bs.eqLiab.equity.association.withdrawals=7790
de-gaap-ci:is.netIncome.regular.operatingTC.otherOpRevenue.ownConsumption.otherWithdrawals=7790
-de-gaap-ci:bs.eqLiab.equity.association.withdrawals=7790
-de-gaap-ci:is.netIncome.regular.operatingTC.otherOpRevenue.ownConsumption.otherWithdrawals=7790
de-gaap-ci:is.netIncome.regular.fin.netParticipation.earnings.other=7000,7011
de-gaap-ci:is.netIncome.regular.fin.netInterest.income.deposits.banks=7100
de-gaap-ci:is.netIncome.regular.fin.netInterest.income.valueDiscount=7141
de-gaap-ci:is.netIncome.regular.fin.netParticipation.amortFinanc.financialsExcept=7200
de-gaap-ci:is.netIncome.regular.fin.netInterest.expenses.regularInterest.other=7300
de-gaap-ci:is.netIncome.regular.fin.netInterest.expenses.regularInterest.relatedPayments=7303
de-gaap-ci:is.netIncome.incomeSharing.gain=7400
de-gaap-ci:is.netIncome.extraord.income.EGHGB=7500
de-gaap-ci:is.netIncome.tax.kst=7600,7603
de-gaap-ci:is.netIncome.tax.soli=7608
de-gaap-ci:is.netIncome.tax.gewst=7610
de-gaap-ci:is.netIncome.tax.kest=3700,3708
-de-gaap-ci:incomeUse.gainLoss.retainedEarningsPrevYear=7700
de-gaap-ci:incomeUse.gainLoss.releaseCapReserves=7799
de-gaap-ci:incomeUse.gainLoss=7798
de-gaap-ci:is.netIncome.incomeSharing.gain=7001
de-gaap-ci:is.netIncome.incomeSharing.loss=6291
de-gaap-ci:is.netIncome.regular.operatingTC.otherOpRevenue.currGains=7720,7730,7731
de-gaap-ci:is.netIncome.regular.operatingTC.otherCost.currLoss=7740,7700,7701,7702
-de-gaap-ci:is.netIncome.regular.operatingTC.otherOpRevenue.currGains=7740,7700,7701,7702
-de-gaap-ci:is.netIncome.regular.operatingTC.otherCost.currLoss=7720,7730,7731
-de-gaap-ci:incomeUse.gainLoss.dividensPlanned=7800,7900,8000,8100,8200,8300,8400,8500,8600,8700,8800,8900
-de-gaap-ci:incomeUse.gainLoss.dividensPlanned=7720,7730,7800,7900,8000,8100,8200,8300,8400,8500,8600,8700,8800,8900
-de-gaap-ci:incomeUse.gainLoss.dividensPlanned=7790
de-gaap-ci:bs.eqLiab.equity.netIncome=7639
de-gaap-ci:bs.eqLiab.equity.subscribed.corp=2900
de-gaap-ci:bs.eqLiab.equity.retainedEarnings=2970,2971,2972,2978
-de-gaap-ci:BVV.profitLoss.withdrawalDistrib=2100,2500
-de-gaap-ci:BVV.profitLoss.withdrawalDistrib=7790
de-gaap-ci:BVV.profitLoss.contribution=2180,2580
de-gaap-ci:bs.eqLiab.liab.bank=3200
de-gaap-ci:bs.eqLiab.equity.revenueRes.unappropriated.otherMeansDueCourse.finalPrev=2082
-de-gaap-ci:bs.ass.deficitNotCoveredByCapital=2970,2971,2972,2978
de-gaap-ci:BVV.profitLoss.assetsCurrentYear=2087
de-gaap-ci:BVV.profitLoss.assetsPreviousYear=2085
ignore=9000,9008,9009


[ini]
AutoSum=1

[bundesanzeiger]
depthGuV=9
depthB=9
depthBVV=9


[bal]
'''


        bal = '''
de-gaap-ci:bs.ass.fixAss.tan.otherEquipm.---ART---!de-gaap-ci:grossCost.beginning="[-NR-A-]"
de-gaap-ci:bs.ass.fixAss.tan.otherEquipm.---ART---!de-gaap-ci:gross.addition="[-NR-B-]"
de-gaap-ci:bs.ass.fixAss.tan.otherEquipm.---ART---!de-gaap-ci:accDepr.beginning="[-NR-C-]"
de-gaap-ci:bs.ass.fixAss.tan.otherEquipm.---ART---!de-gaap-ci:accDepr.DeprPeriod.regular="[-NR-D-]"
de-gaap-ci:bs.ass.fixAss.tan.otherEquipm.---ART---!de-gaap-ci:all_Prev_period="[-NR-E-]"
'''

        for nr in (["0300","landBuildings"],["0500","other"],["0520","passengerCars"],["0560","otherTransportMeans"],["0675","gwgsammelposten"]):
            bal1 = bal.replace("-NR-","-"+nr[0]).strip()
            erg = erg + bal1.replace("---ART---",nr[1]) + "\n"
                


        if int(jahr) < 20:
            erg = re.sub("otherEquipm.passengerCars","branche_kfz.compCar",erg,9999)
            erg = re.sub("otherEquipm.otherTransportMeans","branche_kfz.demoModel",erg,9999)
        
        if int(jahr) < 18:
            erg = re.sub(",BVV,",",",erg,9999)
            erg = re.sub("\n\-?de-gaap-ci:BVV.*?\n","\n",erg,9999)
            erg = re.sub("\n\-?de-gaap-ci:BVV.*?\n","\n",erg,9999)
            erg = re.sub("\n\-?de-gaap-ci:BVV.*?\n","\n",erg,9999)
        

        return(erg)



#        deleted='''
#de-gaap-ci:bs.ass.fixAss.tan.landBuildings.misc=200
#de-gaap-ci:bs.ass.fixAss.tan.landBuildings.buildingsOnOwnLand.buildings=300
#de-gaap-ci:bs.eqLiab.liab.trade.genOther=3300
#
#-de-gaap-ci:is.netIncome.regular.fin.commPart=7720,7730,7731
#-de-gaap-ci:is.netIncome.regular.fin.lossCommPart=7740,7700,7701,7702
#'''


#        if int(jahr) > 19:
#            erg1 = ('''
#de-gaap-ci:bs.ass.fixAss.tan.otherEquipm.passengerCars=520
#de-gaap-ci:bs.ass.fixAss.tan.otherEquipm.otherTransportMeans=560
#'''.strip())
#        else:
#            erg1 = ('''
#de-gaap-ci:bs.ass.fixAss.tan.branche_kfz.compCar=520
#de-gaap-ci:bs.ass.fixAss.tan.branche_kfz.demoModel=560
#'''.strip())
#
#        erg = erg.replace("---INSERT---",erg1)
#
#        m = re.search(r"^(.*?\[xbrl\])(.*?)(\[.*)$",erg,re.DOTALL)
#        erg0 = m.group(1)
#        erg1 = m.group(2)
#        erg2 = m.group(3)
#
#        davon = {}
#        for zeile in erg1.split("\n"):
#            m = re.search(r"^(.*?)\.(misc)=",zeile)
#            if m:
#                davon[m.group(1)] = ""
#        
#        for zeile in erg1.split("\n"):
#            for dline in list(davon.keys()):
#                if zeile.startswith(dline):
#                    m = re.search(r"=(.*?) *$",zeile)
#                    davon[dline] = davon[dline] + "," + m.group(1)
#
#        erg3 = ""
#        for zeile in erg1.split("\n"):
#            for dline in list(davon.keys()):
#                if zeile.startswith(dline+".misc="):
#                    zeile = dline + "=" + davon[dline][1:]
#            erg3 = erg3 + zeile + "\n"
#        
#        if int(jahr) < 2:
#            erg = erg0 + erg3 + erg2
#
#        for k in davon.keys():
#            print("DAVON",k,davon[k])



#**********************************************************************************************

if __name__ == "__main__":

    Bilanz().base_bilanz(*(sys.argv[1:]))
    
