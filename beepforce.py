#BEEPFORCE UNITED - Das Orchester im Infosaal
#   (c) Copyright by Niko Berkmann 2010
# *** SERVER-SKRIPT (Verarbeitung & Distribution) ***

programmversion = 6 #eigentlich Programmrevision
print('Willkommen zu BEEPFORCE UNITED! (V1.7,rev'+str(programmversion)+')')
import cmd, csv, winsound, socket, pickle, datetime, _thread, time, select, socketserver, threading, struct, sys, traceback, math
def fehler_zeigen():
    return '[!] Ein Fehler ist aufgetreten:\n'+traceback.format_exc()+'[!] Die Programmausführung wird trotz des Fehlers fortgesetzt.'
print('(Befehlshilfe mit "commands" aufrufen)')
pfad = musik = stuecktitel = komponist = autor = standardlaenge = schlange = ''
oktavierung = basisdauer = spurauswahl = dateiversion = server_aktiv = broadcast_aktiv = trackanzahl = starteinheit = 0
countdown = 10
musik = melodie = clienten = timeline = []

class beepforce(cmd.Cmd):
    
    def __init__(self): 
        cmd.Cmd.__init__(self) 
        self.prompt = "\n>>> "
    
    def help_load(self):
        print('Lädt eine Datei in den Speicher.\nBeispiel-Aufruf, lädt Datei namens "testdatei.bfu.csv", (Achtung, im Dateinamen bzw. -pfad dürfen keine Leerzeichen vorkommen!): load testdatei.bfu.csv\nAls zweites Argument kann angegeben werden ab welcher Noteneinheit das Stück eingelesen werden soll (Standard ist 0 = Anfang).\nBeispiel-Aufruf, lädt ab Noteneinheit 10: load testdatei.bfu.csv 10\nHinweis: Bei Laden ab einem bestimmten Takt wird aus technischen Gründen ein Wartungston an den Anfang eingefügt.')
    def help_track(self):
        print('Lädt einen bestimmten Track einer geladenen Datei.\nBeispiel-Aufruf, lädt Track Nummer 3: track 3\nMit dem Flag "no_akz" wird bei der Konvertierung jegliche Akzentuierung außer Acht gelassen.\nBeispiel-Aufruf: track 2 no_akz')
    def help_timeline(self):
        print('Erstellt eine Timeline für den geladenen Track, welche Threading und somit höchste Präzision garantiert, und kürzt dabei die Noten um Stocken zu vermeiden.\nBeispiel-Aufruf, erstellt die Timeline und sorgt für Abstände von 15ms zwischen den Noten: timeline 15')
    def help_play(self):
        print('Spielt den momentan geladenen Track (ggf. den der Timeline) ab.')
    def help_pyexport(self):
        print('Exportiert den momentan geladenen Track als Python-Skript.')
    def help_server(self):
        print('Startet den Beepforce-Server zur Musikdistribution.')
    def help_exit(self):
        print('Beendet das Programm... was sonst? =)')
    def do_commands(self, prm):
        print('BEFEHLSÜBERSICHT\n')
        print('Befehle: load, track, timeline, play, pyexport, server, exit\n"help befehl" ruft Hilfe auf und zeigt Befehlsparameter an\n')
        print('Serverbefehle: send, stop, queue, list, setup, benchmark, tcp_launch, udp_launch, logout, shutdown\n(keine Parameter vonnöten, keine weitere Hilfe verfügbar)')
    
    def do_load(self, prm):
        #Datei einlesen
        try:
            global pfad, musik, stuecktitel, komponist, autor, standardlaenge, oktavierung, basisdauer, dateiversion, trackanzahl, starteinheit
            if (len(prm)<3):
                print('Parameter fehlt!')
                return False
            prm_list = prm.split(' ')
            pfad = prm_list[0]
            if (len(prm_list)>=2):
                starteinheit = int(prm_list[1])
            else:
                starteinheit = 0
            try:
                musik = []
                datei = open(pfad,'r')
                tabelle = csv.reader(datei, delimiter=';')
                for zeile in tabelle:
                    musik.append(zeile)
                datei.close()
            except:
                print('Beim Laden der Datei ist ein Fehler aufgetreten!')
                return
            print('Analysiere Datei...')
            dateiversion = int(musik[0][0])
            print('- Dateiformat:',dateiversion)
            if dateiversion != programmversion:
                print('[!] WARNUNG: Das Dateiformat stimmt nicht mit der Programmversion überein, es könnten Probleme auftreten.')
            stuecktitel = musik[1][1]
            komponist = musik[2][1]
            autor = musik[3][1]
            basisdauer = int(musik[4][1])
            standardlaenge = musik[5][1] #1 = keine Pause; <1 = Kürzungsdauer in Prozent der Basisdauer; >1 = Kürzung absolut in Millisekunden
            oktavierung = int(musik[6][1])
            print('- Musikstück:',stuecktitel)
            print('- Komponist:',komponist)
            print('- Autor:',autor)
            print('- Einheitendauer (ms):',basisdauer)
            print('- Standardakzentuierung:',standardlaenge)
            print('- Oktavierung:',oktavierung)
            if (starteinheit!=0):
                print('-> Start ab Noteneinheit '+str(starteinheit))
            tracks = []
            for zeile in musik:
                if len(zeile[0])>= 6 and zeile[0][:4] == 'Spur' and zeile[0][5:].isdigit() and tracks.count(zeile[0][5:])<=0:
                    tracks.append(zeile[0][5:])
            trackanzahl = int(len(tracks))
            print('=> Datei geladen,',trackanzahl,'Tracks gefunden.')
        except:
            print(fehler_zeigen())
    
    def do_track(self, prm):
        try:
            #Trackauswahl & Konvertierung
            global melodie, spurauswahl, timeline, starteinheit
            if (len(prm)<1):
                print('Parameter fehlt!')
                return False
            prm_list = prm.split(' ')
            spurauswahl = int(prm_list[0])
            if (len(prm_list)>=2):
                starteinheit = int(prm_list[1])
            print('Verarbeite Spur '+str(spurauswahl)+'...')
            spur = []
            for zeile in musik:
                if zeile[0][:4] == 'Spur' and int(zeile[0][5:]) == spurauswahl:
                    spur.extend(zeile[1:zeile.index('EOL')])
            if (starteinheit>0):
                spur_cropped = ['423']
                spur_cropped.extend(spur[starteinheit:])
                spur = spur_cropped
            tonleiter = [['c','his'],['cis','des'],['d'],['dis','es'],['e','fes'],['eis','f'],['fis','ges'],['g'],['gis','as'],['a'],['b','ais','hes'],['h','ces']]
            melodie = []
            for note in spur:
                if note == "":
                    if len(melodie)>0 and melodie[len(melodie)-1][0] == 0:
                        melodie[len(melodie)-1][1] += basisdauer
                    else:
                        melodie.append([0,basisdauer,'1'])
                elif note[0] == "_":
                    melodie[len(melodie)-1][1] += basisdauer
                    if len(note)>=3 and note[1]=='-':
                        melodie[len(melodie)-1][2] = note[2:]
                elif note == "EOL":
                    continue
                else:
                    i = 0
                    while (i<len(note) and note[i].isdigit()==False):
                        i += 1
                    notenname = note[:i]
                    notenoktave = int(note[i])
                    notenlaenge = standardlaenge
                    if len(note)>=i+3 and note[i+1]=='-':
                        notenlaenge = note[i+2:]
                    i = 0.0
                    frequenz = 0.0
                    for ton in tonleiter:
                        for variante in ton:
                            if variante == notenname:
                                frequenz = 110*(2.0**(1.0/12.0))**(-9) #Frequenz von c0
                                frequenz *= (2.0**(1.0/12.0))**(i+(notenoktave+oktavierung)*12)
                                break
                        if frequenz > 0:
                            break
                        i += 1
                    frequenz = int(round(frequenz))
                    if not 37<frequenz<32767:
                        print('[!] Normalisiere Frequenz bei Element '+str(len(melodie))+': '+str(frequenz)+' Hz')
                        frequenz = int(min(32766,max(38,frequenz)))
                    melodie.append([frequenz,basisdauer,notenlaenge])
            #Akzentuierung/Tonverkürzungen
            if (len(prm_list)<2 or prm_list[1]!='no_akz'):
                print('Akzentuiere & optimiere Track...')
                melodie_akz = []
                for note in melodie:
                    if note[2]!='1' and note[2]!='l':
                        laenge = note[1]
                        if note[2] == 't': #t = tenuto
                            laenge = max(note[1]-100,round(laenge*0.8))
                        elif note[2] == 's': #s = staccato
                            laenge = min(round(laenge*0.2),50)
                        elif float(note[2])<1: # <1 = Kürzungsdauer in Prozent der Basisdauer
                            laenge = note[1]-basisdauer+(basisdauer*float(note[2]))
                        elif float(note[2])>1: # >1 = Kürzungsdauer absolut
                            laenge = note[1]-float(note[2])
                        melodie_akz.append([int(note[0]),int(round(laenge))])
                        melodie_akz.append([0,int(note[1]-round(laenge))])
                    else:
                        if len(melodie_akz)>0 and note[0]==0 and melodie_akz[len(melodie_akz)-1][0]==0:
                            melodie_akz[len(melodie_akz)-1][1] += note[1]
                        else:
                            melodie_akz.append([note[0],note[1]])
                melodie = melodie_akz
            timeline = []
            print('=> Track konvertiert,',len(melodie),'Noten und Pausen notiert.')
        except:
            print(fehler_zeigen())
    
    def do_timeline(self, prm):
        try:
            #Timelinekonvertierung
            if (len(prm)<1):
                print('Parameter fehlt!')
                return False
            prm_list = prm.split(' ')
            notenabstand = int(prm_list[0])
            print('Erstelle Timeline...')
            global timeline, melodie
            timeline = []
            cursor = 0
            for note in melodie:
                if int(note[0]) != 0:
                    timeline.append([note[0], note[1]-10, cursor])
                cursor += note[1]
            if (notenabstand>0):
                print('Verkürze Noten...')
                i = 0
                verkuerzt = 0
                for i in range(len(timeline)-1):
                    if ((timeline[i+1][2]-(timeline[i][2]+timeline[i][1]))<notenabstand):
                        timeline[i][1] = timeline[i+1][2]-notenabstand-timeline[i][1]
                        verkuerzt += 1
            print('=> Timeline erstellt, '+str(len(timeline))+' Objekte, Liedlänge '+str(round((cursor/1000.0),3))+'sek, '+(str(verkuerzt)+' Kürzungen' if notenabstand>0 else ''))
        except:
            print(fehler_zeigen())
        
    def do_play(self, prm):
        try:
            global timeline
            #Abspielen
            print('Quelle:',('Timeline' if (len(timeline)>0) else ('Melodiespeicher' if (len(melodie)>0) else 'keine!')))
            input('[ Musik starten mit Enter ]')
            print('...playing...')
            if (len(timeline)>0):
                startpunkt = datetime.datetime.now()
                i = 0
                def note_spielen(freq, laenge):
                    _thread.start_new_thread(winsound.Beep, (freq, laenge))
                    faktor = (2.0**(1.0/12.0))
                    taste = math.log(freq/110*faktor**(-9),faktor)
                    print(('▓'*(int(taste)+27)+'▒░')[:70]+' '+str(freq)+' Hz')
                while True:
                    if (datetime.datetime.now()>=(startpunkt+datetime.timedelta(0,0,timeline[i][2]*1000))):
                        _thread.start_new_thread(note_spielen, (timeline[i][0],timeline[i][1]))
                        i += 1
                        if (i>(len(timeline)-1)):
                            break
            elif (len(melodie)>0):
                for note in melodie:
                    if int(note[0]) == 0:
                        time.sleep(float(note[1])/1000.0)
                    else:
                        winsound.Beep(note[0],note[1])
            time.sleep(1)
            print('=> Abspielen beendet.')
        except:
            print(fehler_zeigen())
    
    def do_pyexport(self, prm):
        try:
            #Exportieren
            print('Exportiere Melodiespeicher als abspielbares Pythonskript...')
            exportdatei = 'Spur'+str(spurauswahl)+'_'+pfad+'.py'
            datei = open(exportdatei, "w")
            datei.write('#'+stuecktitel+' von '+komponist+', Spur '+str(spurauswahl)+', notiert von '+autor+'\n')
            datei.write('#automatisch generierte Trackexportdatei von Beepforce United\n')
            datei.write('import winsound\nimport time\n')
            datei.write('print("'+stuecktitel+' von '+komponist+', Spur '+str(spurauswahl)+', notiert von '+autor+'")\n')
            datei.write('input("[ Abspielen mit Enter ]")\nprint("...playing...")\n')
            for note in melodie:
                if int(note[0]) == 0:
                    datei.write('time.sleep('+str(float(note[1])/1000.0)+')\n')
                else:
                    datei.write('winsound.Beep('+str(note[0])+','+str(note[1])+')\n')
            datei.write('input("Fertig! [ Beenden mit Enter ]")\n#EOF')
            datei.close()
            print('=> Track exportiert ('+exportdatei+').')
        except:
            print(fehler_zeigen())

    def do_server(self, prm):
        try:
            print('Starte Server an '+socket.gethostbyname(socket.gethostname())+'...')
            global clienten
            clienten = []
            infos = []
            EOT = b'*EOT*'

            def broadcast_signal():
                global broadcast_aktiv
                broadcaster = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                broadcaster.bind(('', 53732))
                broadcaster.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                signal = pickle.dumps('!beepforce-server!')
                while broadcast_aktiv:
                    broadcaster.sendto(signal,0,('<broadcast>', 53731))
                    time.sleep(5)
                broadcaster.close()

            def schicken(client,data):
                client.sendall(pickle.dumps(data)+EOT)

            def empfangen(client):
                nachricht = b''
                daten = b''
                while True:
                        daten=client.recv(8192)
                        if EOT in daten:
                            nachricht += daten[:daten.find(EOT)]
                            break
                        nachricht += daten
                        if len(nachricht)>1:
                            if EOT in nachricht:
                                nachricht = nachricht[:nachricht.find(EOT)]
                                break
                return pickle.loads(nachricht)

            def listencheck():
                global clienten
                i = 0
                while (i<len(clienten)):
                    try:
                        schicken(clienten[i][0],'check')
                        antwort = empfangen(clienten[i][0])
                        if (antwort!='Still alive!'):
                            raise
                        print('\n*** Client '+str(i+1)+' ***\nIP: '+str(clienten[i][1][0])+'\nAngemeldet: '+str(clienten[i][1][1])+'\nInfos: '+str(clienten[i][1][2]))
                    except:
                        print('\n[!] Probleme mit Client '+str(i+1)+' => Wird gelöscht')
                        print(fehler_zeigen())
                        clienten.remove(clienten[i])
                        continue
                    i += 1
            
            class ClientHandler(socketserver.BaseRequestHandler):
                
                def handle(self):
                    global schlange, clienten
                    try:
                        schlange += 'Verbindung zu '+self.client_address[0]+' hergestellt.\n'
                        schicken(self.request,'input:Bitte PC-Infos eingeben (optional)')
                        info = empfangen(self.request)
                        clienten.append([self.request, [self.client_address[0],str(datetime.datetime.now()),info]])
                        schlange += 'Neuer Client ('+self.client_address[0]+') um '+str(datetime.datetime.now())+'.\n'
                        schicken(self.request,'Anmeldung erfolgreich! ('+str(len(clienten))+' Clienten online)\n=> DIE KONTROLLE GEHT HIERMIT AN DEN SERVER ÜBER :)')
                        while True:
                            a = 1337 #gibts nicht nen einfacheren Weg, unendlich zu warten? sowas verbraucht ja schließlich Speicher...
                    except:
                        schlange += fehler_zeigen()+'\n'

            server = socketserver.ThreadingTCPServer(('',51337), ClientHandler)
            server.allow_reuse_address = True
            global server_aktiv, schlange, timeline, broadcast_aktiv
            schlange = ''
            server_aktiv = 1

            class server_run(threading.Thread): 
                def __init__(self): 
                    threading.Thread.__init__(self) 
                def run(self): 
                    global server_aktiv
                    while server_aktiv:
                        server.handle_request()
                    server.server_close()
                    return

            meine_threads = [] 
            thread = server_run()
            meine_threads.append(thread)
            thread.start()
        except:
            print(fehler_zeigen())
         
        while True:
            global melodie, countdown
            try:
                eingabe = input('\nserver>>> ') 
                if eingabe == "queue":
                    print(schlange.strip())
                    schlange = ''
                elif eingabe == 'list':
                    print('CLIENTEN-LISTE (Auflistung & Statuscheck)')
                    listencheck()
                elif eingabe == 'broadcast':
                    if (broadcast_aktiv):
                        broadcast_aktiv = 0
                        print('Broadcast gestoppt.')
                    else:
                        broadcast_aktiv = 1
                        _thread.start_new_thread(broadcast_signal,())
                        print('Broadcast gestartet!')
                elif eingabe == 'send':
                    self.do_load(input('Datei: '))
                    if (musik==[]):
                        continue
                    abstand = input('Notenabstand in ms: ')
                    modus = int(input('\nDistributionsmodus\n   0: manuelle Trackauswahl\n   1: jeden Track möglichst einmal versenden\n   2: Tracks gleichmäßig an alle Clienten\nModus wählen: '))
                    trackzaehler = 0
                    print('Letzter Verbindungscheck...')
                    listencheck()
                    if (modus==0):
                        print('Nun werden die Tracks versendet, gebe die Tracknummer an, wähle 0 zum Versenden eines Leertracks oder x zum Abbrechen der Aktion.')
                    if not 0<=modus<=2:
                        continue
                    for i in range(len(clienten)):
                        client = clienten[i][0]
                        if (modus>0):
                            trackzaehler += 1
                            if (trackzaehler>trackanzahl):
                                if (modus==1):
                                    tracknummer = '0'
                                elif (modus==2):
                                    trackzaehler = 1
                                    tracknummer = str(trackzaehler)
                            else:
                                tracknummer = str(trackzaehler)
                            print('\n=> Client '+str(i+1)+' an '+clienten[i][1][0]+' ("'+clienten[i][1][2]+'")\n   bekommt Track '+tracknummer)
                        else:
                            tracknummer = input('\n=> Client '+str(i+1)+' an '+clienten[i][1][0]+' ("'+clienten[i][1][2]+'")\n    Track: ')
                        if (tracknummer!='x'):
                            if (int(tracknummer)==0):
                                melodie = [[0,100,'1']]
                            else:
                                self.do_track(tracknummer)
                            self.do_timeline(abstand)
                            print('Übertrage Daten...')
                            try:
                                schicken(client,'senddata')
                                time.sleep(0.5)
                                schicken(client, timeline)
                                print('Track übertragen.')
                            except:
                                print('[!] Probleme bei der Datenübertragung mit Client '+str(i+1)+':')
                                print(fehler_zeigen())
                        else:
                            break
                            print('[!] Datenverteilung abgebrochen.')
                    print('\n'+'#'*32+'\n=> DISTRIBUTION ABGESCHLOSSEN <=\n'+'#'*32)
                elif eingabe == 'tcp_launch' or eingabe == 'udp_launch':
                    latenz = int(input('Latenz in Millisekunden: '))
                    input('[ Mit Enter Startsequenz einleiten ]')
                    print('Initialisiere Startsequenz für '+eingabe[:3].upper()+'-Launch...')
                    for i in range(len(clienten)):
                        try:
                            schicken(clienten[i][0],eingabe)
                        except:
                            print('[!] Probleme bei Startmeldung an Client '+str(i+1)+':')
                            print(fehler_zeigen())
                    for i in range(countdown,0,-1):
                        print('\rCountdown läuft: '+str(i)+'...    ',end='')
                        time.sleep(1)
                    print('\rSende Startsignal...')
                    if eingabe == 'tcp_launch':
                        for i in range(len(clienten)):
                            try:
                                schicken(clienten[i][0],str((len(clienten)-(i+1))*latenz))
                            except:
                                print('[!] Probleme bei der Signalübertragung an Client '+str(i+1)+':')
                                print(fehler_zeigen())
                        print('=> Startsignal gesendet!')
                    elif eingabe == 'udp_launch':
                        udp_launcher = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        for i in range(len(clienten)):
                            try:
                                daten = pickle.dumps((len(clienten)-(i+1))*latenz)
                                udp_launcher.sendto(daten, (clienten[i][1][0], 53731))
                            except:
                                print('[!] Probleme bei der Signalübertragung an Client '+str(i+1)+':')
                                print(fehler_zeigen())
                        udp_launcher.close()
                        print('=> Startsignal gesendet!')
                elif eingabe == 'commands':
                    self.do_commands(self)
                elif eingabe == 'shutdown':
                    print('Server wird heruntergefahren...')
                    for i in range(len(clienten)):
                        try:
                            schicken(clienten[i][0],'shutdown')
                        except:
                            print('[?] Probleme bei Shutdownmeldung an Client '+str(i+1)+':')
                            print(fehler_zeigen())
                    server_aktiv = 0
                    time.sleep(1)
                    break
                elif eingabe == 'stop':
                    print('Stoppe Wiedergabe...')
                    for i in range(len(clienten)):
                        try:
                            schicken(clienten[i][0],'stop_playing')
                        except:
                            print('[!] Probleme bei Stoppnmeldung an Client '+str(i+1)+':')
                            print(fehler_zeigen())
                    print('Meldungen versandt.')
                elif eingabe == 'logout':
                    if(input('Clienten wirklich abmelden?( j/n): ')=='j'):
                        print('Sende Logout-Signal...')
                        for i in range(len(clienten)):
                            try:
                                schicken(clienten[i][0],'logout_client')
                            except:
                                print('[!] Probleme bei Logout-Signal an Client '+str(i+1)+':')
                                print(fehler_zeigen())
                        print('Signal versandt.')
                elif eingabe == 'setup':
                    print('\nCLIENTEINSTELLUNGEN')
                    animation = input('Musik-Visualisierungen aktivieren (j/n): ')
                    print('Versende Einstellungen...')
                    for i in range(len(clienten)):
                        try:
                            schicken(clienten[i][0],('animation_on' if (animation=='j') else 'animation_off'))
                        except:
                            print('[!] Probleme beim Versenden an Client '+str(i+1)+':')
                            print(fehler_zeigen())
                    print('Einstellungen geändert.')
                    print('\nSERVEREINSTELLUNGEN')
                    countdown = max(3,int(input('Countdown in Sekunden: ')))
                elif eingabe == 'benchmark':
                    print('\rStarte Benchmark...')
                    messung_start = datetime.datetime.now()
                    for i in range(len(clienten)):
                        try:
                            schicken(clienten[i][0],'Benchmark!')
                        except:
                            print('[!] Probleme bei der Signalübertragung an Client '+str(i+1)+':')
                    messung_stop = datetime.datetime.now()
                    print('=> Benchmark abgeschlossen:')
                    differenz = (messung_stop - messung_start)
                    dauer = differenz.microseconds/1000+differenz.seconds*1000
                    print('   Dauer: '+str(dauer)+'ms gesamt, '+str(dauer/len(clienten))+'ms pro Anfrage')
                else:
                    print('Unbekannter Befehl: '+eingabe+'\n(Befehlsliste mit "commands" aufrufen)')
            except:
                print(fehler_zeigen())
        print('=> Das Server-Interface wird nun geschlossen!')
        
    def do_credits(self, prm):
        print('###################################')
        print('# BEEPFORCE UNITED V1.7,rev'+str(programmversion)+'      #')
        print('#---------------------------------#')
        print('#   github.com/n2code/beepforce   #')
        print('###################################')
    
    def do_exit(self, prm): 
        print ('Auf Wiedersehen!')
        return True
    
konsole = beepforce()
konsole.cmdloop()
sys.exit(0)
#EOP, End of Program ;)
