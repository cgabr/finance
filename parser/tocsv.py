#  coding:  utf8

import os,sys,re,glob,time

from konto.base import config

#*********************************************************************************

class Tocsv (object):

    def __init__ (self,dir="."):
        self.dir = dir
    
#*********************************************************************************

    def mark (self,remark=""):

        t = time.perf_counter()
        if 't0' in vars(self):
            print ( ("%9.2f" % ((t-self.t0)*1000)) + " ms for:  " + remark )
        self.t0 = t

#*********************************************************************************

    def to_csv (self):     # open the csv and kto files and prepare for processing
    
        for ktofile in glob.glob(self.dir+"/*.*"):
        
            m = re.search("^(.*)\.(.*)$",ktofile)
            if m:
                fileroot = m.group(1)
                if not m.group(2) in ("kto","html"):
                    continue
            else:
                continue
        
            text        = open(ktofile[0]).read()
            text1       = []
            einrueckung = {}
            
            for zeile in text.split("\n"):
            
                m = re.search(r"^(\S+|\S+ +\S+) +([0123456789abcdef]+) +(\-?\d+\.\d\d) +",zeile)
                if m:
                    betrag = re.sub(m.group(3),"\.",",")
                    text1.append(m.group(1) + ";;" + m.group(2) + ";;" + betrag + ";")
                    continue

                m = re.search(r"^(\d\d\d\d)(\d\d)(\d\d) +(\-?\d+\.\d\d) +(\S+) +(\S+) +(\-?\d+\.\d\d) +(.*)$",zeile)
                if m:
                    betrag1 = re.sub(m.group(2),"\.",",")
                    betrag2 = re.sub(m.group(5),"\.",",")
                    text1.append(m.group(1) + ";" + betrag1 + ";" + m.group(3) + ";" + m.group(4) + ";" + betrag2 + ";" + m.group(6) + ";")
                    continue
                    
                m = re.search(r"^ +(\-?\d+\.\d\d) +$",zeile)
                if m:
                    betrag           = re.sub(m.group(1),"\.",",")
                    ind              = betrag.index(",")
                    einrueckung[ind] = 2
                    text1.append(";;" + betrag)
                    continue
                    
                m = re.search(r"^(\S+) +(\-?\d+\.\d\d) +$",zeile)
                if m:
                    betrag           = re.sub(m.group(2),"\.",",")
                    ind              = betrag.index(",")
                    if not ind in einrueckung:
                        einrueckung[ind] = len(einrueckung) + 1
                    text1.append(m.group(1) + (";" * einrueckung[ind]) + betrag)
                    continue
                    
                if "<PRE>" in zeile.upper() or "</PRE>" in zeile.upper():
                    continue
                    
                text1.append(";")
                
                open(self.dir + "/" + fileroot + ".csv","w").write("\n".join(text1)+"\n")
            
#******************************************************************************



if __name__ == "__main__":

    Tocsv().to_csv()
    
    

