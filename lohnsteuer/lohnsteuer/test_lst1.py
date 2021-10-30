#  coding: utf8

import lst2018

stobj = lst2018.Lst2018()

for o in (1,2):

#            <!-- 1, wenn die Anwendung des Faktorverfahrens gewählt wurden (nur in Steuerklasse IV) -->
#	        <INPUT name="af" type="int" default="1"/>
#
#	        <!-- Auf die Vollendung des 64. Lebensjahres folgende
#	             Kalenderjahr (erforderlich, wenn ALTER1=1) -->
#	        <INPUT name="AJAHR" type="int"/>
#	
#	        <!-- 1, wenn das 64. Lebensjahr zu Beginn des Kalenderjahres vollendet wurde, in dem
#	             der Lohnzahlungszeitraum endet (§ 24 a EStG), sonst = 0 -->
#	        <INPUT name="ALTER1" type="int"/>
#	
#	        <!-- in VKAPA und VMT enthaltene Entschädigungen nach §24 Nummer 1 EStG in Cent -->
#	        <INPUT name="ENTSCH" type="BigDecimal" default="new BigDecimal(0)"/>
#	
#	        <!-- eingetragener Faktor mit drei Nachkommastellen -->
#	        <INPUT name="f" type="double" default="1.0"/>
#	
#	        <!-- Jahresfreibetrag nach Maßgabe der Eintragungen auf der
#	             Lohnsteuerkarte in Cents (ggf. 0) -->
#	        <INPUT name="JFREIB" type="BigDecimal"/>
#	
#	        <!-- Jahreshinzurechnungsbetrag in Cents (ggf. 0) -->
#	        <INPUT name="JHINZU" type="BigDecimal"/>
#	
#	        <!-- Voraussichtlicher Jahresarbeitslohn ohne sonstige Bezüge und ohne Vergütung für mehrjährige Tätigkeit in Cent. 
#	             Anmerkung: Die Eingabe dieses Feldes (ggf. 0) ist erforderlich bei Eingabe „sonsti-ger Bezüge“ (Feld SONSTB) 
#	             oder bei Eingabe der „Vergütung für mehrjährige Tätigkeit“ (Feld VMT).
#	             Sind in einem vorangegangenen Abrechnungszeitraum bereits sonstige Bezüge gezahlt worden, so sind sie dem 
#	             voraussichtlichen Jahresarbeitslohn hinzuzurechnen. Vergütungen für mehrere Jahres aus einem vorangegangenen 
#	             Abrechnungszeitraum sind in voller Höhe hinzuzurechnen. --> 
#	        <INPUT name="JRE4" type="BigDecimal"/>
#	 
#	        <!-- In JRE4 enthaltene Versorgungsbezuege in Cents (ggf. 0) -->
#	        <INPUT name="JVBEZ" type="BigDecimal"/>
#	
#			<!--Merker für die Vorsorgepauschale
#				2 = der Arbeitnehmer ist NICHT in der gesetzlichen Rentenversicherung versichert.
#				
#				1 = der Arbeitnehmer ist in der gesetzlichen Rentenversicherung versichert, es gilt die 
#					Beitragsbemessungsgrenze OST.
#					
#				0 = der Arbeitnehmer ist in der gesetzlichen Rentenversicherung versichert, es gilt die 
#					Beitragsbemessungsgrenze WEST. -->
#	        <INPUT name="KRV" type="int"/>
                stobj.KRV = 0
#	
#			<!-- Einkommensbezogener Zusatzbeitragssatz eines gesetzlich krankenversicherten Arbeitnehmers, 
#			 auf dessen Basis der an die Krankenkasse zu zahlende Zusatzbeitrag berechnet wird,
#			 in Prozent (bspw. 0,90 für 0,90 %) mit 2 Dezimalstellen. 
#			 Der von der Kranken-kasse festgesetzte Zusatzbeitragssatz ist bei Abweichungen unmaßgeblich. -->
#			<INPUT name="KVZ" type="BigDecimal"/>
                try:
                    stobj.setKvz(1.25)
                except:
                    pass
#	
#	        <!-- Lohnzahlungszeitraum:
#	             1 = Jahr
#	             2 = Monat
#	             3 = Woche
#	             4 = Tag -->
#	        <INPUT name="LZZ" type="int"/>
                stobj.LZZ = 2
#	
#	        <!-- In der Lohnsteuerkarte des Arbeitnehmers eingetragener Freibetrag für
#	             den Lohnzahlungszeitraum in Cent -->
#	        <INPUT name="LZZFREIB" type="BigDecimal"/>
#	
#	        <!-- In der Lohnsteuerkarte des Arbeitnehmers eingetragener Hinzurechnungsbetrag
#	             für den Lohnzahlungszeitraum in Cent -->
#	        <INPUT name="LZZHINZU" type="BigDecimal"/>
#	
#	        <!-- Dem Arbeitgeber mitgeteilte Zahlungen des Arbeitnehmers zur privaten
#	             Kranken- bzw. Pflegeversicherung im Sinne des §10 Abs. 1 Nr. 3 EStG 2010
#	             als Monatsbetrag in Cent (der Wert ist inabhängig vom Lohnzahlungszeitraum immer 
#	             als Monatsbetrag anzugeben).-->
#	        <INPUT name="PKPV" type="BigDecimal" default="new BigDecimal(0)"/>
#	        
#	        <!-- Krankenversicherung:
#	             0 = gesetzlich krankenversicherte Arbeitnehmer
#	             1 = ausschließlich privat krankenversicherte Arbeitnehmer OHNE Arbeitgeberzuschuss
#	             2 = ausschließlich privat krankenversicherte Arbeitnehmer MIT Arbeitgeberzuschuss -->
#	        <INPUT name="PKV" type="int" default="0"/>
#	        
#	        <!-- 1, wenn bei der sozialen Pflegeversicherung die Besonderheiten in Sachsen zu berücksichtigen sind bzw. 
#	        	 	zu berücksichtigen wären, sonst 0. -->
#	        <INPUT name="PVS" type="int" default="0"/>
#	
#	        <!-- 1, wenn er der Arbeitnehmer den Zuschlag zur sozialen Pflegeversicherung 
#	        	 	zu zahlen hat, sonst 0. -->
#	        <INPUT name="PVZ" type="int" default="0"/>
#	        
#                stobj.setPvz( 1 )
#	        <!-- Religionsgemeinschaft des Arbeitnehmers lt. Lohnsteuerkarte (bei
#	             keiner Religionszugehoerigkeit = 0) -->
#	        <INPUT name="R" type="int"/>
                stobj.R = 0
#	
#	        <!-- Steuerpflichtiger Arbeitslohn vor Beruecksichtigung der Freibetraege
#	             fuer Versorgungsbezuege, des Altersentlastungsbetrags und des auf
#	             der Lohnsteuerkarte fuer den Lohnzahlungszeitraum eingetragenen
#	             Freibetrags in Cents. -->
#	        <INPUT name="RE4" type="BigDecimal"/>
                stobj.setRe4(100*5988)
#	
#	        <!-- Sonstige Bezuege (ohne Verguetung aus mehrjaehriger Taetigkeit) einschliesslich
#	             Sterbegeld bei Versorgungsbezuegen sowie Kapitalauszahlungen/Abfindungen,
#	             soweit es sich nicht um Bezuege fuer mehrere Jahre handelt in Cents (ggf. 0) -->
#	        <INPUT name="SONSTB" type="BigDecimal"/>
#	
#	        <!-- Sterbegeld bei Versorgungsbezuegen sowie Kapitalauszahlungen/Abfindungen,
#	             soweit es sich nicht um Bezuege fuer mehrere Jahre handelt
#	             (in SONSTB enthalten) in Cents -->
#	        <INPUT name="STERBE" type="BigDecimal" regex_test="" regex_transform=""/>
#	
#	        <!-- Steuerklasse:
#	             1 = I
#	             2 = II
#	             3 = III
#	             4 = IV
#	             5 = V
#	             6 = VI -->
#	        <INPUT name="STKL" type="int"/>
                stobj.STKL = 3
#	
#	        <!-- In RE4 enthaltene Versorgungsbezuege in Cents (ggf. 0) -->
#	        <INPUT name="VBEZ" type="BigDecimal"/>
#	
#	        <!-- Vorsorgungsbezug im Januar 2005 bzw. fuer den ersten vollen Monat
#	             in Cents-->
#	        <INPUT name="VBEZM" type="BigDecimal"/>
#	
#	        <!-- Voraussichtliche Sonderzahlungen im Kalenderjahr des Versorgungsbeginns
#	             bei Versorgungsempfaengern ohne Sterbegeld, Kapitalauszahlungen/Abfindungen
#	             bei Versorgungsbezuegen in Cents-->
#	        <INPUT name="VBEZS" type="BigDecimal"/>
#	
#	        <!-- In SONSTB enthaltene Versorgungsbezuege einschliesslich Sterbegeld
#	            in Cents (ggf. 0) -->
#	        <INPUT name="VBS" type="BigDecimal"/>
#	
#	        <!-- Jahr, in dem der Versorgungsbezug erstmalig gewaehrt wurde; werden
#	             mehrere Versorgungsbezuege gezahlt, so gilt der aelteste erstmalige Bezug -->
#	        <INPUT name="VJAHR" type="int" regex_test="" regex_transform=""/>
#	
#	        <!-- Kapitalauszahlungen / Abfindungen / Nachzahlungen bei Versorgungsbezügen 
#	             für mehrere Jahre in Cent (ggf. 0) -->     
#	        <INPUT name="VKAPA" type="BigDecimal" regex_test="" regex_transform=""/>
#	 
#			<!-- Vergütung für mehrjährige Tätigkeit ohne Kapitalauszahlungen und ohne Abfindungen 
#				 bei Versorgungsbezügen in Cent (ggf. 0) -->
#	        <INPUT name="VMT" type="BigDecimal" regex_test="" regex_transform=""/>
#	
#	        <!-- Zahl der Freibetraege fuer Kinder (eine Dezimalstelle, nur bei Steuerklassen
#	             I, II, III und IV) -->
#	        <INPUT name="ZKF" type="BigDecimal" regex_test="" regex_transform=""/>
#                stobj.ZKF = 2.0
#	
#	        <!-- Zahl der Monate, fuer die Versorgungsbezuege gezahlt werden (nur
#	             erforderlich bei Jahresberechnung (LZZ = 1) -->
#	        <INPUT name="ZMVB" type="int" regex_test="" regex_transform=""/>
#	        
#	        <!-- In JRE4 enthaltene Entschädigungen nach § 24 Nummer 1 EStG in Cent -->
#	    	<INPUT name="JRE4ENT" type="BigDecimal" default="BigDecimal.ZERO"/>
#	    	
#	    	<!-- In SONSTB enthaltene Entschädigungen nach § 24 Nummer 1 EStG in Cent -->
#	    	<INPUT name="SONSTENT" type="BigDecimal" default="BigDecimal.ZERO"/>


#    	<!--  AUSGABEPARAMETER  -->
#		<OUTPUTS type="STANDARD">
#	        <!-- Bemessungsgrundlage fuer die Kirchenlohnsteuer in Cents -->
#	        <OUTPUT name="BK" type="BigDecimal" default="new BigDecimal(0)"/>
#	
#	        <!-- Bemessungsgrundlage der sonstigen Einkuenfte (ohne Verguetung
#	             fuer mehrjaehrige Taetigkeit) fuer die Kirchenlohnsteuer in Cents -->
#	        <OUTPUT name="BKS" type="BigDecimal" default="new BigDecimal(0)"/>
#	
#	        <OUTPUT name="BKV" type="BigDecimal" default="new BigDecimal(0)"/>
#	
#	        <!-- Fuer den Lohnzahlungszeitraum einzubehaltende Lohnsteuer in Cents -->
#	        <OUTPUT name="LSTLZZ" type="BigDecimal" default="new BigDecimal(0)"/>
#	
#	        <!-- Fuer den Lohnzahlungszeitraum einzubehaltender Solidaritaetszuschlag
#	             in Cents -->
#	        <OUTPUT name="SOLZLZZ" type="BigDecimal" default="new BigDecimal(0)"/>
#	
#	        <!-- Solidaritaetszuschlag fuer sonstige Bezuege (ohne Verguetung fuer mehrjaehrige
#	             Taetigkeit) in Cents -->
#	        <OUTPUT name="SOLZS" type="BigDecimal" default="new BigDecimal(0)"/>
#	
#	        <!-- Solidaritaetszuschlag fuer die Verguetung fuer mehrjaehrige Taetigkeit in
#	             Cents -->
#	        <OUTPUT name="SOLZV" type="BigDecimal" default="new BigDecimal(0)"/>
#	
#	        <!-- Lohnsteuer fuer sonstige Einkuenfte (ohne Verguetung fuer mehrjaehrige
#	             Taetigkeit) in Cents -->
#	        <OUTPUT name="STS" type="BigDecimal" default="new BigDecimal(0)"/>
#	
#	        <!-- Lohnsteuer fuer Verguetung fuer mehrjaehrige Taetigkeit in Cents -->
#	        <OUTPUT name="STV" type="BigDecimal" default="new BigDecimal(0)"/>
#	        
#	        <!-- Für den Lohnzahlungszeitraum berücksichtigte Beiträge des Arbeitnehmers zur
#				 privaten Basis-Krankenversicherung und privaten Pflege-Pflichtversicherung (ggf. auch
#				 die Mindestvorsorgepauschale) in Cent beim laufenden Arbeitslohn. Für Zwecke der Lohn-
#				 steuerbescheinigung sind die einzelnen Ausgabewerte außerhalb des eigentlichen Lohn-
#				 steuerbescheinigungsprogramms zu addieren; hinzuzurechnen sind auch die Ausgabewerte
#				 VKVSONST -->
#			<OUTPUT name="VKVLZZ" type="BigDecimal" default="new BigDecimal(0)"/> 
#			
#			<!-- Für den Lohnzahlungszeitraum berücksichtigte Beiträge des Arbeitnehmers 
#				 zur privaten Basis-Krankenversicherung und privaten Pflege-Pflichtversicherung (ggf. 
#				 auch die Mindestvorsorgepauschale) in Cent bei sonstigen Bezügen. Der Ausgabewert kann
#				 auch negativ sein. Für tarifermäßigt zu besteuernde Vergütungen für mehrjährige 
#				 Tätigkeiten enthält der PAP keinen entsprechenden Ausgabewert. -->
#			<OUTPUT name="VKVSONST" type="BigDecimal" default="new BigDecimal(0)"/> 
#		
#		</OUTPUTS>
#		
#		<!--  AUSGABEPARAMETER DBA  -->
#		<OUTPUTS type="DBA">
#		
#			<!-- Verbrauchter Freibetrag bei Berechnung des laufenden Arbeitslohns, in Cent -->
#			<OUTPUT name="VFRB" type="BigDecimal" default="new BigDecimal(0)"/> 
#			
#			<!-- Verbrauchter Freibetrag bei Berechnung des voraussichtlichen Jahresarbeitslohns, in Cent -->
#			<OUTPUT name="VFRBS1" type="BigDecimal" default="new BigDecimal(0)"/> 
#			
#			<!-- Verbrauchter Freibetrag bei Berechnung der sonstigen Bezüge, in Cent -->
#			<OUTPUT name="VFRBS2" type="BigDecimal" default="new BigDecimal(0)"/> 
#			
#			<!-- Für die weitergehende Berücksichtigung des Steuerfreibetrags nach dem DBA Türkei verfügbares ZVE über 
#				dem Grundfreibetrag bei der Berechnung des laufenden Arbeitslohns, in Cent -->
#			<OUTPUT name="WVFRB" type="BigDecimal" default="new BigDecimal(0)"/> 
#			
#			<!-- Für die weitergehende Berücksichtigung des Steuerfreibetrags nach dem DBA Türkei verfügbares ZVE über dem Grundfreibetrag 
#				bei der Berechnung des voraussichtlichen Jahresarbeitslohns, in Cent -->
#			<OUTPUT name="WVFRBO" type="BigDecimal" default="new BigDecimal(0)"/> 
#			
#			<!-- Für die weitergehende Berücksichtigung des Steuerfreibetrags nach dem DBA Türkei verfügbares ZVE 
#				über dem Grundfreibetrag bei der Berechnung der sonstigen Bezüge, in Cent -->
#			<OUTPUT name="WVFRBM" type="BigDecimal" default="new BigDecimal(0)"/> 
#		</OUTPUTS>

#                 
#
#                    php_pars = "# " + jahr + '''         
#$_POST['stkl']      =  ''' + str(stkl)            + ''';
#$_POST['zkf']       =  ''' + str(kinder)          + ''';
#$_POST['r']         =  ''' + str(kst)             + ''';
#$_POST['kinderlos'] =  ''' + str(kinderlos)       + ''';
#$_POST['lzz']       =  ''' + intmode              + ''';
#$_POST['re4']       =  ''' + {"2":str(betrag),"1":str(lohnjahr)}[intmode]  + ''';
#$_POST['kvsatz']    =  ''' + "0"                  + ''';
#$_POST['anpdez']    =  ''' + "0"                  + ''';
#$_POST['e_krv']     =  ''' + str(rvbefreit%2)     + ''';
#
#'''


                stobj.setZkf(0)
                stobj.MAIN()


kirchensteuersatz = 20


ls = 0.01 * float( stobj.getLstlzz() )
sz = 0.01 * float( stobj.getSolzlzz() )
ks = 0.01 * ( float(stobj.getBk()) + float(stobj.getBks()) + float(stobj.getBkv()) ) * kirchensteuersatz


print (ls,sz,ks)

