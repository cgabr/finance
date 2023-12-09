import os,sys,re,time,datetime
import matplotlib.pyplot as plt


class Schedule (object):

#******************************************************************************

    def __init__ (self):
    
        self.gfac = 0.6
        
        
#******************************************************************************

    def block (self,plt,shape,a,b,y,h,c,t,ha="center",ctext="white",tsize="x-large"):

#        a  = a-1
        a1 = a + 0.1
        b1 = b - 0.1
        h  = h - 0.2
    
        einrueckung = 0.5 * self.gfac
    
        a2 = a + einrueckung
        b2 = b - einrueckung
        m  = y + h/2
        y9 = y + h
    
        if shape == "arrow":
            print(a,a2,b,b2)
            plt.gca().fill([a ,a2,a,b2,b,b2],
                           [y9,m ,y,y,m,y9],linewidth=0,color=c)
        if shape == "block":
            plt.gca().fill([a1,a1,b1,b1],
                           [y9,y ,y ,y9],linewidth=0,color="grey")
    
#        plt.gca().add_patch(plt.Rectangle( (a,y), b-a, h, color=c  ) )
        if ha == "left":
            plt.text(a1,y+h/2,t,ha=ha,va="center",size=tsize,color=ctext,weight=700)
        else:
            plt.text(a1+(b1-a1)/2,y+h/2,t,ha=ha,va="center",size=tsize,color=ctext,weight=700)


#******************************************************************************

    def read_data (self,text):
    
        self.data = text.split("\n")
        
        self.max_datum = 0
        self.min_datum = 99999999
        
        self.projects  = []
        
        self.pools     = {}

#******************************************************************************

    def project (self,pname):
    
        nproj          = {}
        nproj['steps'] = []

        for line in self.data:
        
            if not ("-" + pname) in line:
                continue
            m = re.search(r"(\d\d\d\d\d\d\d\d) +(\-?\d+\.\d\d) +(\S+) +(\S+) +(\-?\d+\.\d\d) +(.+?) *$",line)
            if not m:
                continue
            datum  = m.group(1)
            betrag = m.group(2)
            ktoa   = m.group(3)
            ktob   = m.group(4)
            remark = m.group(6)

            self.min_datum = min(int(datum),self.min_datum)
            self.max_datum = max(int(datum),self.max_datum)
            
#            if len(nproj['steps']) > 0:
#                nproj['steps'][-1][1] = datum
            
            print(remark)
            if not 'title' in nproj:
                nproj['title'] = remark
                datum0         = datum
                continue

#            m = re.search(r"^END\: *(.*?) *$",remark)
#            if m:
#                print(123,remark)
#                nproj['title'] = m.group(1)
#                break
                
            scolor = "grey"
            for pool in self.pools:
                if pool in ktob:
                    scolor = self.pools[pool]

            pstep  = [datum0,datum,scolor,remark]
            datum0 = datum
            
            nproj['steps'].append(pstep)
            
        self.projects.append(nproj)

#******************************************************************************
    
    def make_schedule (self,text):

        fig,ax = plt.subplots()
        plt.figure(figsize=(15,8.27),dpi=300) #  11.69,8.27
        plt.subplots_adjust(left=-0.0,right=1.0,bottom=0.0,top=1.0)
        plt.axis('off')
        plt.rc('font',size=int(10*self.gfac))

        breite   =  self.gfac
        linediff =  breite *1.3

#        plt.plot([0.00]+gesamt,color="blue",linewidth=1.2)
#        plt.axhline(0,color="green",linewidth=0.3)
        plt.axvline(1,color="black",linewidth=0.0) #,linestyle="dashed")
        plt.axvline(60,color="black",linewidth=0.0)
        plt.axhline(-1,color="black",linewidth=0.0)
        plt.axhline(-9,color="black",linewidth=0.0)

        line = -1
        
        self.min_datum = 20231001
        self.max_datum = 20241231
        
        print(self.projects)
        
        for quartal in self.projects:
        

            min_d = int( datetime.datetime.strptime("%8u"%self.min_datum,"%Y%m%d").strftime("%s") )
            max_d = int( datetime.datetime.strptime("%8u"%self.max_datum,"%Y%m%d").strftime("%s") )

            for qu in [
                         ["20231001","20231230","23/IV"],
                         ["20240101","20240330","24/I"],
                         ["20240401","20240630","24/II"],
                         ["20240701","20240930","24/III"],
                         ["20241001","20241230","24/IV"] ]:
                         
                a_d = int( datetime.datetime.strptime("%8u"%float(qu[0]),"%Y%m%d").strftime("%s") )
                b_d = int( datetime.datetime.strptime("%8u"%float(qu[1]),"%Y%m%d").strftime("%s") )
                a   = "%3.1f" % (7 + 52 * (a_d - min_d)/(max_d - min_d))
                b   = "%3.1f" % (7 + 52 * (b_d - min_d)/(max_d - min_d))
#                print(a,b,pstep,min_d,max_d)
                self.block(plt,"block",float(a),float(b),line,breite,"#999999",qu[2],tsize="xx-large")


        for project in self.projects:
        

            min_d = int( datetime.datetime.strptime("%8u"%self.min_datum,"%Y%m%d").strftime("%s") )
            max_d = int( datetime.datetime.strptime("%8u"%self.max_datum,"%Y%m%d").strftime("%s") )

            line = line - linediff
            self.block(plt,"block",1,7,line,breite,"#777777", project['title'], "left")
            
            for pstep in project['steps']:
                a_d = int( datetime.datetime.strptime("%8u"%float(pstep[0]),"%Y%m%d").strftime("%s") )
                b_d = int( datetime.datetime.strptime("%8u"%float(pstep[1]),"%Y%m%d").strftime("%s") )
                a   = "%3.1f" % (7 + 52 * (a_d - min_d)/(max_d - min_d))
                b   = "%3.1f" % (7 + 52 * (b_d - min_d)/(max_d - min_d))
                print(project['title'])
                print(a,b,pstep,min_d,max_d)

                
                self.block(plt,"arrow",float(a),float(b),line,breite,pstep[2],pstep[3])
        

            
        plt.savefig("tools_roadmap.svg",orientation="landscape",bbox_inches='tight',pad_inches=0.0)
#os.system("cp "+filename+".pdf test.pdf")
#    
#



