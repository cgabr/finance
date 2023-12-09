#  coding:  utf8

import os,sys,re,glob,time

try:
    from konto_custom import config
except:
    from konto.base import config

from konto.base.konto import Konto


#*********************************************************************************

class SVNET (object):

    def __init__ (self,dir="."):
        self.dir     = dir
        self.ktoa    = config.KTO_KRANKENKASSEN     
        self.ktob    = config.KTO_BEITRAGSNACHWEISE 
        self.kkmap   = re.sub(r"\s","",config.MAP_KRANKENKASSEN,99999999).split(",")

    
#*********************************************************************************

    def mark (self,remark=""):

        t = time.perf_counter()
        if 't0' in vars(self):
            print ( ("%9.2f" % ((t-self.t0)*1000)) + " ms for:  " + remark )
        self.t0 = t

#********************************************************************************

    def auswertung (self,*pars):

        Konto().kto()

        try:
            faktor = float(pars[0])
        except:
            faktor = 1.0

        print("")
        print(glob.glob("*.kto"))
        for zeile in os.popen("grep -P '^([A-Z0-9]+|KV-Z|KV-meldZUS) +(\S+) *$' *.kto").read().split("\n"):
            m = re.search(r"^(\S+) +(.*)$",zeile)
            if not m:
                continue
            if m.group(1) == "KV":
                kv = float(m.group(2))
            elif m.group(1) == "KV-Z":
                zus = float(m.group(2))
            elif m.group(1) == "KV-meldZUS":
                zus = zus + float(m.group(2))
                kv  = kv - zus
                print ("%-10s" % "KV" +     "%10.2f"%(kv/faktor))
                print ("%-10s" % "KV-ZUS" + "%10.2f"%(zus/faktor))
            elif m.group(1) == "AV":
                text = "%-10s" % m.group(1) + "%10.2F"%(float(m.group(2))/faktor)
            elif m.group(1) == "PV":
                text = text + "\n" + "%-10s" % m.group(1) + "%10.2f"%(float(m.group(2))/faktor)
            else:
                print("%-10s" % m.group(1) + "%10.2f"%(float(m.group(2))/faktor))
            if m.group(1) == "RV":
                print(text)
                


#******************************************************************************



if __name__ == "__main__":

    SVNET().auswertung(*sys.argv[1:])
    
