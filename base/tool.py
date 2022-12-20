import os,re,sys,glob,time,konto

from konto.base.konto import Konto


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
    

#        print("DIR",os.path.abspath("."))


        if len(glob.glob("./mirror.sh")) == 0:   #  man ist nicht direkt in einem Spiegelkonto,
            akt_path0 = ""                       #  wir gehen jetzt maöl zu dem uebergeordneten 01_...er Konto
            while (0 == 0):
                akt_path = os.path.abspath(".")
                print(akt_path)
                if akt_path == akt_path0:
                    print("01_... directory not found.")
                    return(0)
                akt_path0 = akt_path
                new_path  = glob.glob(akt_path+"/01_*")
                new_path1 = []
                for path_item in new_path:
                    if os.path.isdir(path_item):
                        new_path1.append(path_item)
                if len(new_path1) == 1:
                    os.chdir(new_path1[0])
                    print(new_path1[0])
                    break
                os.chdir("..")


        mirror_dirs = ( glob.glob("*/mirror.sh") + glob.glob("*/*/mirror.sh") +
                        glob.glob("*/*/*/mirror.sh") + glob.glob("*/*/*/*/mirror.sh") +
                        glob.glob("*/*/*/*/*/mirror.sh") + glob.glob("*/*/*/*/*/*/mirror.sh") )
                        
        mirror_dirs.sort()
        mirror_changes = {}
        zaehler = 0
        
        while 0 == 0:
            zaehler = zaehler + 1
            if len(mirror_dirs) > 0:
                print("---------")
                print("ROUND " + str(zaehler) )
                print("---------")
                if zaehler > 1:
                    time.sleep(2)
            changes_done = 0
            for mirror_dir in mirror_dirs:
                orig_dir = os.path.abspath(".")
                os.chdir( re.sub(r"/mirror.sh","",mirror_dir) )
                Konto().kto()
                sign_before = open( glob.glob("*.kto")[0] ).read()
                self.mirror()
                sign_after  = open( glob.glob("*.kto")[0] ).read()
                if not sign_before == sign_after:
                    changes_done = 1
                os.chdir(orig_dir)
            if changes_done == 0:
                break
                
        if len(mirror_dirs) > 0:
            return()


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
                print("--->",ktodir1)
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
        print("-->",ktodir1)

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
#                print("::::",zeile)
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

#************************************************************************

    def rechnung (self,*pars):   #  spiegelt ein Konto in eine andere Buchhaltung
    

        rechnung_file = pars[0]
        text          = open(rechnung_file).read()
        m             = re.search(r" (\d+) ?\%",text)
        if not m:
            return(0)
        ust  = float(m.group(1))
        print(ust)
        
        text1   = text
        text0   = ""
        zahlen  = []
        zahlen1 = []
        
        while (0 == 0):
            m = re.search(r"^(.*?\>)(\d\d?\d?\,\d\d|\d\d?\d? \d\d\d\,\d\d|\d\d?\d? \d\d\d \d\d\d\,\d\d)(\<| EUR\<)(.*)$",text1,re.DOTALL)
            if not m:
                break
            betrag = re.sub(r" ","",m.group(2))
            betrag = re.sub(r",",".",betrag)
            betrag = float(betrag)
            text0  = text0 + m.group(1) + m.group(2)
            text1  = m.group(3) + m.group(4)
            zahlen.append(betrag)
            

        gesamt = 0.00
        while len(zahlen) > 0:
            if len(zahlen)%3 == 0:
                betrag = zahlen.pop(0)
                if len(zahlen) == 2:
                    betrag = gesamt
                gesamt = gesamt + betrag
                zahlen1.append(betrag)
            elif len(zahlen)%3 == 2:
                zahlen.pop(0)
                zahlen1.append( betrag * (ust/100) )
            elif len(zahlen)%3 == 1:
                zahlen.pop(0)
                zahlen1.append( betrag * ((100+ust)/100) )
                
        print(zahlen1)
 
        text1    = text
        text0    = ""
        while (0 == 0):
            m = re.search(r"^(.*?\>)(\d\d?\d?\,\d\d|\d\d?\d? \d\d\d\,\d\d|\d\d?\d? \d\d\d \d\d\d\,\d\d)(\<| EUR\<)(.*)$",text1,re.DOTALL)
            if not m:
                break
            betrag  = "%3.2f" % zahlen1.pop(0)
            betrag  =  re.sub("\.",",",betrag)
            betrag1 = betrag[-6:]
            betrag  = betrag[:-6]
            while not betrag == "":
                betrag1 = betrag[-3:] + " " + betrag1
                betrag  = betrag[:-3]
            text0  = text0 + m.group(1) + betrag1
            text1  = m.group(3) + m.group(4)
        text0 = text0 + text1
            
        open(rechnung_file+"~","w").write(text)
        open(rechnung_file,"w").write(text0)


#**************************************************************************


if __name__ == "__main__":
    
    tool = Tool()

#    print(sys.argv)

    Tool.__dict__[sys.argv[1]](tool,*sys.argv[2:])
