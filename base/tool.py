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
                
#**************************************************************************


if __name__ == "__main__":
    
    tool = Tool()

    print(sys.argv)

    Tool.__dict__[sys.argv[1]](tool,*sys.argv[2:])
