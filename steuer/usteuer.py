#  coding:  utf8

import os,sys,re,glob,time,sqlite3,hashlib,time,base64,datetime,random

from konto.base import config

#*********************************************************************************

class USteuer (object):

    def __init__ (self):
        pass
    
#*********************************************************************************

    def usteuer (self,ktotext0="",mode="-"):

        text                  = []
        text1                 = []
        umsatzsteuerbuchungen = {}
        neue_ust_buchungen    = {}
#        ul                    = len(config.UMSATZSTEUER_KONTO)
        
        if ktotext0 == "":
            ktofile = glob.glob("*.kto")[0]
            ktotext = open(ktofile).read()
        else:
            ktotext = ktotext0
            
        for zeile in ktotext.split('\n'):

            m = re.search('^(\d\d\d\d\d\d\d\d) +(\-?\d+\.\d\d) +(\S+?) +(\S+) +(\-?\d+\.\d\d) +(.*)', zeile)
            if not m:
                text.append(zeile)
                continue
                
            datum  = m.group(1)
            betrag = m.group(2)
            ktoa   = m.group(3)
            ktob   = m.group(4)
            remark = m.group(6)

#            if ktob[0:ul] == config.UMSATZSTEUER_KONTO:
#                continue

            text.append(zeile)
            
            if remark[0:2] == '++':
                steuersatz = 19
            elif remark[0:2] == '+-':
                steuersatz = 7
            elif remark[0:2] == '-+':
                steuersatz = 16
            elif remark[0:2] == '--':
                steuersatz = 5
            else:
                m = re.search(r"(USt. |Vorst. ).*?\((.*)\)",remark)
                if m:
                    umsatzsteuerbuchungen[datum+m.group(2)] = 1
                    print("XX",datum+m.group(2),zeile)
                continue

            ustbuchungen = [ [datum, betrag, ktoa, ktob, steuersatz, remark] ]

            for buchung in ustbuchungen:
                steuersatz = buchung[4]
                betrag     = buchung[1]
#                if mode == 0:
#                    gegenkto  = 1 - int(buchung[2][0:1] == '-' and not buchung[3][0:1] == '-')
#                else:
                gegenkto  = 1 - int(buchung[2].startswith(mode) and not buchung[3].startswith(mode))
                steuerart = 1 - (gegenkto + int(float(buchung[1]) < 0))
                steuerkto = ['U', 'I'][steuerart % 2]
                if steuersatz == 19:
                    steuerkto = steuerkto + '6'
                elif steuersatz == 7:
                    steuerkto = steuerkto + '7'
                elif steuersatz == 16:
                    steuerkto = steuerkto + '2'
                elif steuersatz == 5:
                    steuerkto = steuerkto + '1'
                                    
                steuerart = ['USt.', 'Vorst.'][steuerart % 2]
                if steuersatz < 100:
                    buchung[1] = '%3.2f' % (-steuersatz * 0.01 / (1.0 + steuersatz * 0.01) * float(buchung[1]))
                    buchung[5] = '   ' + str(steuersatz) + ' v.H. ' + steuerart + ' von ' + '%3.2f' % abs(float(betrag)) + ' (' + buchung[5][2:] + ')'
                else:
                    m = re.search(r"ST(\d\d)\__(\d+)\_(\d\d)",buchung[5])
                    if m:
                        buchung[1] = '%3.2f' % (float(m.group(3)+"."+m.group(3)) * [1,-1]*int(float(buchung[1])<1))
                        buchung[5] = '   ' + m.group(1) + ' v.H. ' + steuerart + ' enthalten in ' + '%3.2f' % abs(float(betrag)) + ' (' + buchung[5][2:] + ')'
                    else:
                        continue
                buchung[3 - gegenkto] = config.UMSATZSTEUER_KONTO + '-' + steuerkto
                buchung[4] = '0.00'
                datrem = datum+remark[2:]
                if not datrem in neue_ust_buchungen:
                    neue_ust_buchungen[datrem] = []
                neue_ust_buchungen[datrem].append('  '.join(buchung))

        for datrem in neue_ust_buchungen:
            print(datrem)
            if not datrem in umsatzsteuerbuchungen:
                for ust_buchung in neue_ust_buchungen[datrem]:
                    text.append(ust_buchung)
        
        ktotext =  '\n'.join(text) + '\n' 
        
        if ktotext0 == "":
            open(ktofile,"w").write(ktotext)

        return(ktotext)

#*************************************************************************

if __name__ == "__main__":
    USteuer().usteuer("","13")

