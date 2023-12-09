#  coding:  utf8

import os,sys,re,glob,time

from konto.base import config

#*********************************************************************************

class Tocsv (object):

    def __init__ (self,maxzeile=200,dir="."):
        self.dir      = dir
        self.maxzeile = maxzeile
    
#*********************************************************************************

    def mark (self,remark=""):

        t = time.perf_counter()
        if 't0' in vars(self):
            print ( ("%9.2f" % ((t-self.t0)*1000)) + " ms for:  " + remark )
        self.t0 = t

#*********************************************************************************

    def to_csv (self):     # open the csv and kto files and prepare for processing
    
        ktofiles = glob.glob(self.dir+"/*.*")
        ktofiles.sort()
        
        for ktofile in ktofiles:
        
            m = re.search("^(.*)\.(.*)$",ktofile)
            if m:
                fileroot = m.group(1)
                if not m.group(2).lower() in ("kto","html"):
                    continue
            else:
                continue
        
            print("process " + ktofile)
            text        = open(ktofile).read()
            text        = re.sub(r"^\<PRE\>","",text)
            text        = re.sub(r"\<\/PRE\> *\n *$","",text,re.DOTALL)
            text1       = []
            text2       = []
            einrueckung = {}
            
            maxzeile1   = 0
            
            for zeile in text.split("\n"):
                            
                m = re.search(r"^(\S+|\S+ +\S+) +([0123456789abcdef]+) +(\-?\d+\.\d\d) *",zeile)
                if m:
                    betrag = re.sub(r"\.",".",m.group(3))
                    text1.append('"' + m.group(1) + '";;;"' + m.group(2) + '";;' + betrag + ";")
                    text2.append( self.normalize_text(zeile) )
                    continue

                m = re.search(r"^\d\d(\d\d)(\d\d)(\d\d) +(\-?\d+\.\d\d) +(\S+) +(\S+) +(\-?\d+\.\d\d) +(.*)$",zeile)
                if m:
                    betrag1 = re.sub(r"\.",".",m.group(4))
                    betrag2 = re.sub(r"\.",".",m.group(7))
                    text1.append('"' + m.group(3) + "." + m.group(2) + "." + m.group(1) + '";' + betrag1 + ';;"' + m.group(5) + '";"' + m.group(6) + '";' + betrag2 + ';;"' + m.group(8) + '";')
                    text2.append( self.normalize_text(zeile)[0:self.maxzeile] )
                    maxzeile1 = min( max(maxzeile1,len(text2[-1])), self.maxzeile)
                    continue
                    
                m = re.search(r"^ +(\-?\d+\.\d\d) *$",zeile)
                if m:
                    betrag           = re.sub(r"\.",".",m.group(1))
                    text1.append(";" + betrag + ";")
                    text2.append( self.normalize_text(zeile) )
                    continue
                    
                m = re.search(r"^(\S+) +(\-?\d+\.\d\d) *$",zeile)
                if m:
                    betrag           = re.sub(r"\.",".",m.group(2))
                    ind              = zeile.index(".")
                    if not ind in einrueckung:
                        einrueckung[ind] = len(einrueckung) + 2
                    text1.append('"' + m.group(1) + '";' + (";" * einrueckung[ind]) + betrag + ";")
                    text2.append( self.normalize_text(zeile) )
                    continue
                    
                if "<PRE>" in zeile.upper() or "</PRE>" in zeile.upper():
                    continue
                    
                text1.append('"' + zeile + '"')
                text2.append(self.normalize_text(zeile)[0:self.maxzeile])
                maxzeile1 = min( max(maxzeile1,len(text2[-1])), self.maxzeile)
                
            open(self.dir + "/" + fileroot + ".csv","w").write("\n".join(text1)+"\n")
                
            open("__tt.txt","w").write("\n".join(text2)+"\n")
            print(maxzeile1)
            os.system("a2ps -B -1 -l " + str(maxzeile1) + " -r -o __tt.ps __tt.txt")
            os.system("ps2pdf __tt.ps " + fileroot + ".pdf")
            os.unlink("__tt.txt")
            os.unlink("__tt.ps")


        gesamt_csv = ""


        ktofiles = glob.glob(self.dir+"/????.kto.csv")
        ktofiles.sort()
        for ktofile in ktofiles:
        
            text = open(ktofile).read()
            
            gesamt_csv = gesamt_csv + "KONTO;" + re.sub(r"\D","",ktofile,9999)[0:4] + ";;\"<<<<<<<<<<<<<\";\"<<<<<<<<<<<<\";\"<<<<<<<<<<<<\"" + "\n\"\"\n" + text
            gesamt_csv = gesamt_csv + "\n\"\"\n\"\"\n\"\"\n"

        jahr = re.sub(r"[\\\/]$","",os.path.abspath("."))
        if re.search(r"kn(\d\d)$",jahr):
            jahr = jahr[-2:]
        else:
            jahr = ""
            
        if len(jahr) > 1:
            text1 = ""
            non_empty_lines = 0
            for zeile in gesamt_csv.split("\n"):
                
                m = re.search(r"^(\d\d\.\d\d\.\d\d)",zeile[1:])
                if m:
                    datum = m.group(1)
                    if not datum[6:] == jahr:
                        continue
                else:
                    m = re.search(r"^[^- ]+\-",zeile[1:])
                    if m:
                        continue
                    else:
                        if zeile[1:4] == "---":
                            continue
                            
#                print(non_empty_lines,zeile)
                if len(zeile) < 3:
                    if non_empty_lines < 2:
                        non_empty_lines = 0
                        continue
                    non_empty_lines = 0
                else:
                    non_empty_lines = non_empty_lines + 1
                            
                text1 = text1 + zeile + "\n"
            jahr = "_" + jahr
            gesamt_csv = "Kontennachweise " + jahr + ";\n" + text1.replace("KONTO;","\"\"\n\"\"\n\"\"\n\"\"\n\"\"\nKONTO;",999999)

            
        if len(gesamt_csv) > 10:
            open("kontennachweise"+jahr+".csv","w").write(gesamt_csv)



            
#************************************************************************************************************

    def normalize_text (self,text):
    
        text = re.sub(r"ä",   "ae",text,99999999)
        text = re.sub(r"ö",   "oe",text,99999999)
        text = re.sub(r"ü",   "ue",text,99999999)
        text = re.sub(r"Ä",   "Ae",text,99999999)
        text = re.sub(r"Ö",   "Oe",text,99999999)
        text = re.sub(r"Ü",   "Ue",text,99999999)
        text = re.sub(r"ß",   "ss",text,99999999)
        text = re.sub(r"a\"", "ae",text,99999999)
        text = re.sub(r"o\"", "oe",text,99999999)
        text = re.sub(r"u\"", "ue",text,99999999)
        text = re.sub(r"A\"", "Ae",text,99999999)
        text = re.sub(r"O\"", "Oe",text,99999999)
        text = re.sub(r"U\"", "Ue",text,99999999)
        text = re.sub(r"s\"", "ss",text,99999999)
        text = re.sub(r"&",   "u", text,99999999)
        text = re.sub(r"\t",  "  ",text,99999999)
        text = re.sub(chr(13),"",  text,99999999)
        
        return(text)


#******************************************************************************



if __name__ == "__main__":

    Tocsv().to_csv()
    
    

