import os,re,sys,glob,time

#  Erstellt Gehaltsbescheinigungen und publiziert sie

#  Grundsaetzlich werden alle Lohnkonten durchgegangen, optional kann aber ein Parameter angegeben werden,
#  der ein Pattern-Matching auf dem Namen der Lohnbuchhaltung macht.

filter = ""
try:
    filter = sys.argv[1]
except:
    filter = ""

endmonat = ""
try:
    endmonat = sys.argv[2]
except:
    endmonat = ""
    
    
m = re.search(r"^(\d+)$",filter)
if m:
    ee = endmonat
    endmonat = filter
    filter = ee
    
if endmonat == "":
    print("Endmonat muss angegeben werden (JJMM)")
    exit()


if __name__ == "__main__":

    if filter == "":
        mk_gehalt = os.popen("grep LOHN-AN [a-z]*/*/*.kto").read().split("\n")
    else:
        mk_gehalt = os.popen("grep LOHN-AN "+filter+"*/*/*.kto").read().split("\n")
    mk_gehalt.sort()
    pp = {}

#    os.system("rm -r _tmp_")
    os.system("mkdir _tmp_")
    for zeile in mk_gehalt:
        m      = re.search(r"(\d\d\d\d)(\d\d).*?([a-z]+)-LOHN",zeile)
        if not m:
            continue
        p      = m.group(3)
        if glob.glob(p+"/*gehalts*") == 0:
            continue
        yy     = m.group(1)  #  Jahr
        monat  = m.group(1) + m.group(2)
        monat1 = m.group(1) + "_" + m.group(2)
        
        if monat > "20" + endmonat:
            continue

#  1. Gehaltsbescheinigung erstellen

        new_gehalt = 0
        x      = glob.glob(p+"/*/gehaltsbe*"+ monat1+"*md") # + glob.glob(p+"/*/gehaltsbe*"+ yy +"*md")
        if len(x) == 0: # aber nur, wenn es noch keine Gehaltsbescheinigung gibt
            print(p,monat1)
            os.system("cd " + glob.glob(p+"/*gehalt*")[0] + "; python3 -m konto.base.konto; python3 -m konto.lohnbuchhaltung.lohn " + monat)
            os.system("rm /var/www/html/*/web/gehalt/*/gehaltsbe*"+p+"*"+monat1+".pdf")
            os.system("rm /var/www/html/*/web/gehalt/*/gehaltsbe*"+p+"*"+yy+"_12.pdf")
            os.system("rm /var/www/html/*/web/gehalt/*/gehaltsbe*"+p+"*"+yy+".pdf")
            pp[p] = 1
            os.system("cd " + glob.glob(p+"/*gehalt*")[0] + "; python3 -m konto.base.konto")  #  die urspruengliche Form des Kontos wiederherstellen
            new_gehalt = 1
            time.sleep(0.1)

#  2. die pdfs ins Netz stellen

        x = glob.glob("/var/www/html/*/web/gehalt/*/."+p)
        if len(x) > 0:
            m      = re.search(r"^(.*)[\\\/]\.[a-z]+$",x[0])
            ablage = m.group(1)  #  das ist das gefundene Verzeichnis, in das zu publizieren ist
#            print( "ln -s " + os.path.abspath(p+"/52_sozialversicherungsmeldungen") + " " + ablage)
#            print(glob.glob(p))
            if not os.path.isdir(ablage+"/Sozialversicherung"):
                try:
                    os.system( "ln -s " + os.path.abspath(  glob.glob(p+"/*sozialvers*")[0] ) + " " + ablage + "/Sozialversicherung")
                except:
                    pass
            if not os.path.isdir(ablage+"/Weitere_Dokumente"):
                try: 
                    os.system( "ln -s " + os.path.abspath(  glob.glob(p+"/*misc*")[0] ) + " " + ablage + "/Weitere_Dokumente")
                except:
                    pass
            if not os.path.isdir(ablage+"/Lohnsteuerbescheinigungen"):
                try:
                    os.system( "ln -s " + os.path.abspath(  glob.glob(p+"/*lohnsteuerbeschei*")[0] ) + " " + ablage + "/Lohnsteuerbescheinigungen")
                except:
                    pass
            if m:
                x = glob.glob(ablage+"/gehaltsbe*"+monat1+".pdf") + glob.glob(ablage+"/gehaltsbe*"+yy+".pdf")
                if len(x) == 0 or new_gehalt == 1:
                    os.system("cp " + p + "/*/gehaltsbe*"+monat1+"*md _tmp_; cd _tmp_; " +
                              "python3 -m iftlib.md.gx md2svg *.md; cp *.pdf " + m.group(1))
                    os.system("rm _tmp_/gehalt*;")
                    time.sleep(0.1)
            for jahr in (2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,
                         2021,2022,2023,2024,2025,2026,2027,2028,2029,2030,
                         2031,2032,2033,2034,2035,2036,2037,2038,2039,2040,
                         2041,2042,2043,2044,2045,2046,2047,2048,2049,2050,
                         2051,2052,2053,2054,2055,2056,2057,2058,2059,2060):
                         
                jahr1 = str(jahr)
                x = glob.glob(ablage+"/gehaltsbe*"+jahr1+"*pdf")
                if len(x) == 12:
                    x1 = re.sub(r"_\d\d\.pdf",".pdf",x[0])
                    os.system("cd " + ablage + "; pdftk gehaltsbe*"+jahr1+"*pdf output " + x1)
                    for x2 in x:
                        os.unlink(x2)
                    time.sleep(0.1)
                
#    os.system("rm -r _tmp_")



#    for p in pp.keys():
#        os.system("cd " + p + "; yy")
            