#  coding: utf8
import os,re,sys
for papfile in '''
Lst2006 ,Lohnsteuer2006Big.xml
Lst2007 ,Lohnsteuer2007Big.xml
Lst2008 ,Lohnsteuer2008Big.xml
Lst2009 ,Lohnsteuer2009Big.xml
Lst2010 ,Lohnsteuer2010Big_alt.xml
Lst2011 ,Lohnsteuer2011BisNovember.xml
Lst2011c,Lohnsteuer2011Dezember.xml
Lst2012 ,Lohnsteuer2012.xml
Lst2013 ,Lohnsteuer2013_2.xml
Lst2014 ,Lohnsteuer2014.xml
Lst2015 ,Lohnsteuer2015BisNovember.xml
Lst2015c,Lohnsteuer2015Dezember.xml
Lst2016 ,Lohnsteuer2016.xml
Lst2017 ,Lohnsteuer2017.xml
Lst2018 ,Lohnsteuer2018.xml
Lst2019 ,Lohnsteuer2019.xml
Lst2020 ,Lohnsteuer2020.xml
Lst2021 ,Lohnsteuer2021.xml
'''.split("\n"):
    m = re.search(r"^(.*?) *,(.*) *$",papfile)
    if m and "Lst" in papfile:
        print    ("lstgen -x " + m.group(2) + " -l python --class-name " + m.group(1) + " > " + m.group(1).lower() + ".py")
        os.system("lstgen -x " + m.group(2) + " -l python --class-name " + m.group(1) + " > " + m.group(1).lower() + ".py")
        text     = open(m.group(1).lower() + ".py").read()
        text     = re.sub("\(self, scale, rounding\)","(self, scale, rounding=ROUND_DOWN)",text)
        open(m.group(1).lower() + ".py","w").write(text)

