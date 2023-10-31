#  coding:  utf8

import os,sys,re,glob,time

try:
    from konto_custom import config
except:
    from konto.base import config


#*********************************************************************************

class Unicredit (object):

    def __init__ (self,dir="."):
        self.dir     = dir
    
#*********************************************************************************

    def mark (self,remark=""):

        t = time.perf_counter()
        if 't0' in vars(self):
            print ( ("%9.2f" % ((t-self.t0)*1000)) + " ms for:  " + remark )
        self.t0 = t

#********************************************************************************

    def parse_unicredit (self,*pars):


        ktoauszuege = glob.glob(self.dir+"/*.pdf")
        
        for ktoauszug in ktoauszuege:
        
            m = re.search(r"^(.*?)\-([A-Za-z0-9]+)",ktoauszug)
            if m:
                fileroot = m.group(2)
            else:
                m = re.search(r"^(.*?)\_(\d\d\d\d\d\d\d\d)\_(\d\d\d)",ktoauszug)
                if m:
                    fileroot = m.group(1)
#                else:
#                    continue

#            os.system("pdftotext -layout " + ktoauszug)
            file1 = ktoauszug[:-4]
#            os.system("mv " + file1 + ".txt " + file1 + ".ocr")
            
            text   = ""
            datum  = ""
            betrag = ""
            remark = ""
            nr     = ""
            zeile0 = ""
            fileroot = "IzvodPLReport"
            for zeile in open(file1+".ocr").read().split("\n"):
                if "VALUTI" in zeile:
                    fileroot = "IzvodDevPLReport"
                m = re.search("IZVOD BRO[J\)].*?(\d+)",zeile)
                if m:
                    auszug_nr = m.group(1)
                    continue
                m = re.search("Na dan.*?(\d\d)\.(\d\d)\.(\d\d\d\d)",zeile)
                if m:
                    auszug_datum = m.group(3) + m.group(2) + m.group(1)
                    continue

                if "UKUPNO" in zeile:
                    break
                m = re.search(r"^(.*?)(\d\d\.\d\d\.\d\d\d\d)(.*?) +([0123456789,]+\.\d\d) +([0123456789,]+\.\d\d)",zeile)
                if m:
                    text   = text + zeile0 + "  " + nr + "\n"
                    nr     = m.group(1).strip()
                    datum  = m.group(2)
                    betrag = m.group(5)
                    if betrag == "0.00":
                        betrag = "-" + m.group(4)
                    betrag = betrag.replace(",","")
                    betrag = betrag.replace(".",",")
                    zeile0 = datum + ";" + betrag + ";" + m.group(3).strip()
                    continue
                if not zeile.strip() == "" and not zeile0 == "":
                    zeile0 = zeile0 + " " + zeile.strip()
                                    
            text   = text + zeile0 + "  " + nr + "\n"
            text   = text.replace("  "," ")
            text   = text.replace("  "," ")
            text   = text.replace("  "," ")
            text   = text.replace("  "," ")
            text   = text.replace("  "," ")
            text   = text.replace("  "," ")
            text   = text.replace("¬"," ")
            
#            fileroot = fileroot.replace("_ocr","")
#            fileroot = fileroot.replace("_ocr","")
            fileroot = fileroot + "_" + auszug_datum + "_" + ("%03u" % int(auszug_nr))
            
            open(fileroot+".csv","w").write(text.strip()+"\n")
            os.system("mv " + file1 + ".pdf " + fileroot+".pdf")
            os.system("mv " + file1 + ".ocr " + fileroot+".ocr")
    

#******************************************************************************



if __name__ == "__main__":

    Unicredit().parse_unicredit()
    
    

