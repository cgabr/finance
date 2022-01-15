#  coding:  utf8

import os,sys,re,glob,time,sqlite3,hashlib,time,base64,datetime,random

#*********************************************************************************

class Chain (object):

    def __init__ (self):
        pass
    
#*********************************************************************************

    def mark (self,remark=""):

        t = time.perf_counter()
        if 't0' in vars(self):
            print ( ("%9.2f" % ((t-self.t0)*1000)) + " ms for:  " + remark )
        self.t0 = t

#*********************************************************************************

    def round (self,file,sys_argv,a=0,b=0):
    
        if int(sys_argv[1]) < a or int(sys_argv[1]) > b:
            exit()
        else:
            print(file," execute ...")

#*********************************************************************************

    def connect_to_accounting (self):   #   ,buchhaltung=""):
    
        kto_copy = glob.glob("*.kto_copy")
        
        if len(kto_copy) == 1:
            copy_path = kto_copy[0][:-5]
        else:
            return()
        
        zaehler = 0
        while (0 == 0):
            zaehler * zaehler + 1
            if zaehler > 8:
                return()            
            copy_path = "../*/" + copy_path
            orig_kto  = glob.glob(copy_path)
            if len(orig_kto) > 1:
                orig_kto = orig_kto[0]
                break
                       
        os.system("cp " + orig_kto[0] + "  " + kto_copy[0] )
        
        self.copy_konto()
        
#*********************************************************************************
        
    def copy_konto(self):

 
        ktotext  = [ open(glob.glob("*.kto_copy")[0]).read(),  open(glob.glob("*.kto")[0]).read() )
        ktotext1 = ""
        zeilen   = {}
        ukto     = ""
        ukto1    = ""
        
        
        
        if len(ktotext) == 2:  #  wenn es ein Zielfile gibt, dieses untersuchen und die passenden Zeilen so lassen
            m     = re.search(r"^(\S+) +\(\S\S\S\S\S\S\) ",ktotext[1].split("\n")[0])
            if not m:
                return(None)
            ukto1 = m.group(1)

        for zeile in ktotext[0].split("\n"):  #  erst das Quellfile aufbereiten
#            print("::::",zeile)
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
                m = re.search('^(\S+)\-(\S+) +\(.*?\)',zeile)
                if m:
                    ukto  = m.group(1) + "-" + m.group(2)
                else:
                    return(None)

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
            if not zeile == "":
                ktotext1 = ktotext1 + zeile + "\n"
                
        open( glob.glob("*.kto")[0],"w").write(ktotext1) 

#*********************************************************************************


if __name__ == "__main__":

    Chain().connect_to_accounting()
    
    

