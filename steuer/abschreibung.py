#  coding:  utf8

import os,sys,re,glob,time,sqlite3,hashlib,time,base64,datetime,random

from konto.base import config

#*********************************************************************************

class Abschreibung (object):

    def __init__ (self):
        pass
    
#*********************************************************************************

    def abschreibung (self,abschreibungskonto,ktotext0="",weitere_abschreibungskonten={}):

        text         = []
        inventarlist = {}
        ab_kto       = {}

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
            betrag = float(m.group(2))
            m1     = re.search(r"^(.*)\-AN$",m.group(3))
            m2     = re.search(r"^(.*?)-([^\-]+)",m.group(4))
            if not m1:
                m1 = re.search(r"^(.*)\-AN$",m.group(4))
                m2 = re.search(r"^(.*?)\-([^\-]+)",m.group(3))
            if m1:
                text.append(zeile)
                inventar = m1.group(1)
                if not inventar in inventarlist:
                    inventarlist[inventar] = betrag
                else:
                    inventarlist[inventar] = inventarlist[inventar] + betrag
                if m2 and betrag > 0.0:
                    ab_kto[inventar] = "-" + m2.group(2) + "-"
     
        for inventar in inventarlist:
            m = re.search(r"^(.*\-)(\d\d)([123456789ABC])\_(\d+)(.*?)$",inventar)
            if m:
                abschreibungsjahr   = m.group(2)
                kaufmonat           = m.group(3)
                abschreibungsanteil = int(m.group(4))
                betrag              = inventarlist[inventar]
                ktoa = m.group(1) + m.group(2) + m.group(3) + '_' + m.group(4) + m.group(5) + '-AS'
            else:
                continue
            if kaufmonat in 'ABC':
                kaufmonat = {'A': '10', 'B': '11', 'C': '12'}[kaufmonat]
            teilabschreibung = 13 - int(kaufmonat)
            if abschreibungsanteil == 1:
                teilabschreibung = 12
            restwert = betrag
            jahr = int('20' + abschreibungsjahr)
            zaehler = 1
            while (0 == 0):
                datum1 = '%04u' % jahr + '1228'
                erstjahresanteil = float(teilabschreibung) / 12.0
                abschreibungsbetrag = -float('%3.2f' % min(erstjahresanteil * betrag / abschreibungsanteil, restwert))
                restwert = float('%3.2f' % restwert) + float('%3.2f' % abschreibungsbetrag)
#                if float(restwert) / float(betrag) < 0.01 * abschreibungsanteil:
                if float(restwert) < 0.01 * float(betrag) / float(abschreibungsanteil) or abs(restwert) < 1.00:
                    abschreibungsbetrag = abschreibungsbetrag - restwert
                    restwert            = 0.0
                
                betrag1 = '%3.2f' % abschreibungsbetrag
                abschreibungskonto1 = re.sub("-xxx-",ab_kto[inventar],abschreibungskonto)
                if int(abschreibungsanteil) in weitere_abschreibungskonten:
                    abschreibungskonto1 = abschreibungskonto1[0:-4] + str(weitere_abschreibungskonten[abschreibungsanteil])

                if abs(restwert) < 0.001:
                    text.append(datum1 + '  ' + betrag1 + '  ' + ktoa + '  ' +
                                abschreibungskonto1 +
                                '  0.00  ' + 'Rest-Abschreibung, Kaufwert: ' + '%3.2f' % betrag)
                    break
                else:
                    remark1 = 'Abschreibung'
                    if teilabschreibung < 12:
                        remark1 = remark1 + ' (' + str(teilabschreibung) + '/12)*'
                    remark1 = remark1 + ', ' + str(zaehler) + '. Teil-Abschreibung (1/' + str(abschreibungsanteil) + ')'
                    remark1 = remark1 + ', Kaufwert: ' + '%3.2f' % betrag
                text.append(datum1 + '  ' + betrag1 + '  ' + ktoa + '  ' + abschreibungskonto1 + '  0.00  ' + remark1)
                jahr = jahr + 1
                zaehler = zaehler + 1
                teilabschreibung = 12

        ktotext = '\n'.join(text) + '\n'

        if ktotext0 == "":
            open(ktofile,"w").write(ktotext)

        return(ktotext)

#*********************************************************************************

if __name__ == "__main__":
    Abschreibung().abschreibung("13-D6a-6220")

