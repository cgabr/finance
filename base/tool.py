import os,re,sys,glob

#**************************************************************************

class Tool ():

    def join (self):

        zeile0 = ""
        for file in sys.stdin:
            file1 = file.strip()
            text = open(file1).read()
        
            text1  = ""
            zeile0 = ""
            for zeile in text.split("\n"):
                zeile = zeile.strip()
                if re.search(r"^\"\d\d\.\d\d\.\d\d\d\d\"",zeile):
                    text1  = text1 + zeile0 + "\n"
                    zeile0 = zeile
                else:
                    zeile0 = zeile0 + zeile
                    
            open(file1+"~","w").write(text)
            open(file1,"w").write(text1)
                

#************************************************************************

    def mirror (self):   #  spiegelt ein Konto in eine andere Buchhaltung
    

        ktofile0 = glob.glob("*.kto")
        if len(ktofile0) > 1:
            print("More than one ktofile.")
            return(0)
        if len(ktofile0) == 0:
            print("No ktofile found.")
            return(0)
        ktofile0 = ktofile0[0]

        ktodir1 = ""
        if os.path.isfile("mirror.sh"):

            ktodir1 = re.sub("\s","",open("mirror.sh").read())
            ktodir1 = re.sub(r"^(.+)[ \=](.*)$","\\2",ktodir1)
            if not os.path.isdir(ktodir1):
                ktodir1 = ""
       
        if ktodir1 == "":   #   jetzt die richtige Verzeichnisstruktur suchen
            akt_path = os.path.abspath(".")
            m = re.search(r"^(.*)[\\\/](\d*\_?)(.*)[\\\/](.*)$",akt_path)
            targetdir = m.group(4) + "/" + m.group(3)
            
            parent0 = ""
            parent  = "."            

            while 0 == 0:

                if len(os.path.abspath(parent)) < 3:
                    break
                if parent0 == parent:
                    break
                if parent == "/home":
                    break
                sublevel = "/"
                while 0 == 0:
                    print(parent + sublevel + "*_" + targetdir)
                    ktodir1 = glob.glob(parent + sublevel + "*_" + targetdir) + glob.glob(parent + sublevel + targetdir)
                    if len(ktodir1) > 0:
                        break
                    sublevel = "/*" + sublevel
                    if len(sublevel) > 15:
                        break
                print("XX",ktodir1)
                if len(ktodir1) == 1:
                    open("mirror.sh","w").write("AN="+ktodir1[0]+"\n")
                    break
                parent0 = parent
                parent  = "../" + parent
#                print(ktofile0,ktodir1)
                        
            if len(ktodir1) == 0:
                print("no mirror found")
                return(1)
        
            ktodir1  = ktodir1[0]
        print("XX",ktodir1)

        ktotext  = [ open(ktofile0).read() ]

        ktofile1 = glob.glob(ktodir1 + "/*.kto")
#        print("VV",ktofile1)
        if len(ktofile1) > 1:
            print("More than one ktofile in mirror dir " + ktodir1)
            return(0)
        if len(ktofile1) == 1:
            ktofile1 = ktofile1[0]
            ktotext.append( open(ktofile1).read() )
        else:
            ktofile1 = ktodir1 + "/extern.kto"

#        print(ktofile1,"<--")

        ktotext1 = ""
        zeilen   = {}
        ukto     = ""
        ukto1    = ""
        
        if len(ktotext) == 2:  #  wenn es ein Zielfile gibt, dieses untersuchen und das Konto heraussuchen
            m     = re.search(r"^(\S+) +\S\S\S\S\S\S\S\S\S\S\S\S ",ktotext[1].split("\n")[0])
            if not m:
                return(2)
            ukto1 = m.group(1)

        for zeile in ktotext[0].split("\n"):  #  erst das Quellfile aufbereiten
            m = re.search('^(\d\d\d\d\d\d\d\d) +(\-?\d+\.\d\d) +'+ukto+'\-(\S+?) +(\S+) +(\-?\d+\.\d\d) +(.*)', zeile)
            if not ukto == "" and m:
                zeile1    = m.group(1) + "  " + re.sub(r"--","","-"+m.group(2)) + "  " + ukto1 + "-" + m.group(4) + "  " + m.group(3)
                zeile_key = zeile1
                zeile1    = zeile1 + "  " + re.sub(r"--","","-"+m.group(5)) + "  " + m.group(6)
                zeile_key = re.sub(r" ","",zeile_key+m.group(6),99999999)
#                print(":::",zeile_key)
                zeilen[ zeile_key ] = zeile1  # dessen Zeilen werden in einem Hash gespeichert, dessen Keys die Zeile
                                              # ohne Leerzeichen und Saldofeld sind
            elif ukto == "":
                print("::::",zeile)
                m = re.search('^(\S+)\-(\S+) +\S\S\S\S\S\S\S\S\S\S\S\S',zeile)
                if m:
                    ukto  = m.group(1) + "-" + m.group(2)
                else:
                    print("END")
                    return(4)

        if len(ktotext) == 2:  #  Zielfile untersuchen und die passenden Zeilen so lassen
            for zeile in ktotext[1].split("\n"):
                m = re.search('^(\d\d\d\d\d\d\d\d +\-?\d+\.\d\d +\S+? +\S+) +(\-?\d+\.\d\d) +(.*)', zeile)
                if m:
                    zeile_key = re.sub(r" ","",m.group(1)+m.group(3),99999999)
#                    print("-->",zeile_key)
                    if zeile_key in zeilen:   #  Zeile gibt es schon im Zielfile
                        ktotext1 = ktotext1 + zeile + "\n"   # Zeile genau an dieser Stelle auch lassen
                        zeilen[ zeile_key ] = ""             # und aus dem Zeilen-Hash loeschen
                else:
                    ktotext1 = ktotext1 + zeile + "\n"

        for zeile in zeilen.values():  #  die nicht wiedergefundenen Zeilen beim Zielfile unten anhaengen
#            print("ZZZ",zeile)
            if not zeile == "":
                ktotext1 = ktotext1 + zeile + "\n"
                
        open( ktofile1 ,"w").write(ktotext1)

#**************************************************************************


if __name__ == "__main__":
    
    tool = Tool()

#    print(sys.argv)

    Tool.__dict__[sys.argv[1]](tool,*sys.argv[2:])
