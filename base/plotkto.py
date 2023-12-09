import os,re,sys,glob,time,konto

from konto.base.konto import Konto
import matplotlib.pyplot as plt
from konto.base.tool import Tool
import time;

#**************************************************************************

class Plotkto ():


    def __init__  (self,plan=""):
        self.plan = plan + " "
        if self.plan == " ":
            self.plan = ""

#************************************************************************

    def test (self):

        plt.plot([1,4,6,7])
        plt.savefig("test.svg")
        
        
#**************************************************************************

    def analyse (self,expenses="13-D7f-[^-]+,",income= "12-D1a-[^-]+,",start="2302",end="2512",interval=1,marker=[]):
    
    
        gesamt = 0.00
        konto = Konto([])

        konto.startdatum = "20" + start
        konto.enddatum   = "20" + end
        
        exp_konten = konto.format_salden(expenses)
        inc_konten = konto.format_salden(income)
        
        exp_salden = {}
        exp_salden["SUM"] = []
        inc_salden = {}
        inc_salden["SUM"] = []
        gesamt = [0.00]
        for k in exp_konten:
            exp_salden[k[0]] = []
        for k in inc_konten:
            inc_salden[k[0]] = []

        int1 = start
        intervals1 = []
        intervals2 = []
        while (0 == 0):
            
            int2 = Tool().add(int1,interval-1)
            print(int1,int2)
            if int(int1) > int(end):
                break
            
            intervals1.append(len(intervals1))
            intervals2.append(int2)
            
            konto.startdatum = "20"+int1
            konto.enddatum   = "20"+int2

            erg = konto.format_salden(expenses)
            for k in erg:
                exp_salden[k[0]].append(-float(k[2]))
            exp_salden["SUM"].append(0.00)
            for k in exp_konten:
                if len(exp_salden[k[0]]) < len(exp_salden["SUM"]):
                    exp_salden[k[0]].append(0.00)
                exp_salden["SUM"][-1] = exp_salden["SUM"][-1] + float(exp_salden[k[0]][-1])

            erg = konto.format_salden(income)
            for k in erg:
                inc_salden[k[0]].append(-float(k[2]))
            inc_salden["SUM"].append(0.00)
            for k in inc_konten:
                if len(inc_salden[k[0]]) < len(inc_salden["SUM"]):
                    inc_salden[k[0]].append(0.00)
                inc_salden["SUM"][-1] = inc_salden["SUM"][-1] + float(inc_salden[k[0]][-1])
                
            gesamt.append( gesamt[-1] + exp_salden["SUM"][-1] + inc_salden["SUM"][-1] )
            
            int1 = Tool().add(int2,1)

        gesamt.pop(0)

        return([exp_salden,inc_salden,gesamt,intervals2])



        plt.plot(gesamt)
        
        skiptick = 4
        intervals3 = []
        for int3 in intervals2:
            if len(intervals3) % skiptick == 0:
                intervals3.append(int3)
            else:
                intervals3.append("")
        
        
        plt.xticks(intervals1,intervals3)


        plt.savefig("test.jpg")

        for k in exp_konten:
            print(k[0],exp_salden[k[0]])
        print(exp_salden["SUM"])
        for k in inc_konten:
            print(k[0],inc_salden[k[0]])
        print(inc_salden["SUM"])
        print(gesamt)
        print(intervals1,intervals2)
        
    
        





#**************************************************************************


if __name__ == "__main__":
    
    plotkto = Plotkto()

#    print(sys.argv)

    Plotkto.__dict__[sys.argv[1]](plotkto,*sys.argv[2:])
