#!/usr/bin/python3
#  coding:  utf8

import os,sys,re,glob,time

from konto.base.konto import Konto
from konto.steuer.usteuer import USteuer
from konto.steuer.abschreibung import Abschreibung
from konto.bilanz.jahresabschluss import Jahresabschluss

#*********************************************************************************

class Synchronize (object):

    def __init__ (self):
        pass

#*********************************************************************************

    def mark (self,remark=""):

        t = time.perf_counter()
        if 't0' in vars(self):
            print ( ("%9.2f" % ((t-self.t0)*1000)) + " ms for:  " + remark )
        self.t0 = t

#*********************************************************************************

    def synchronize_accounts (self,*pars):     # open the csv and kto files and prepare for processing

        abschreibungskonto = pars[0]

        kto  = Konto()
        
        kto.kto("^12-")
        USteuer().usteuer()
        kto.kto()

        kto.kto("^13-")
        USteuer().usteuer()
        kto.kto()

        kto.kto("^10-A11-")
        Abschreibung().abschreibung(abschreibungskonto)
        kto.kto()

        kto.kto("^14-")
        Jahresabschluss().jahressteuer("","2")
        kto.kto()



#**********************************************************************************************

if __name__ == "__main__":

    Synchronize().synchronize_accounts("13-D6a-6220")
    
