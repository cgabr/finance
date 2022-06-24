#!/usr/bin/python3
#  coding:  utf8

import os,sys,re,glob,time

from konto.base.konto import Konto
from konto.steuer.usteuer import USteuer
from konto.steuer.abschreibung import Abschreibung
from konto.bilanz.jahresabschluss import Jahresabschluss
from konto.parser.csv import CSV

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

        kto          = Konto()
        self.dataset = kto.read_config()
#        print(self.dataset)

        local_dir    = os.path.abspath(".")

        for anchor_dir in (  glob.glob(kto.base_dir+"/../anchor.txt") +
                             glob.glob(kto.base_dir+"/../*/anchor.txt") +
                             glob.glob(kto.base_dir+"/../*/*/anchor.txt") +
                             glob.glob(kto.base_dir+"/../*/*/*/anchor.txt") +
                             glob.glob(kto.base_dir+"/../*/*/*/*/anchor.txt") +
                             glob.glob(kto.base_dir+"/../*/*/*/*/*/anchor.txt") ):
        
            anchor_dir = re.sub(r"^(.*)[\\\/](.*)$","\\1",anchor_dir)
            os.chdir(anchor_dir)
            kto.kto()
            if CSV().to_kto() == 0:
                print("Anchor is broken in " + os.path.abspath(anchor_dir))
                return()
            kto.kto()
            os.chdir(local_dir)
            
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
        Jahresabschluss().jahressteuer("",self.dataset["gesellschaftsform"])
        kto.kto()




#**********************************************************************************************

if __name__ == "__main__":

    Synchronize().synchronize_accounts("13-D6a-6220")
    
