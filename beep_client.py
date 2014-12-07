#BEEPFORCE UNITED - Das Orchester im Infosaal
#   (c) Copyright by Niko Berkmann 2010
# *** CLIENT-SKRIPT ***

print('Willkommen zum BEEPFORCE-Client! (V1.6)')
import winsound, socket, pickle, datetime, time, _thread, sys, traceback, math, os
def fehler_zeigen():
    print('[!] Ein Fehler ist aufgetreten:\n'+traceback.format_exc()+'[!] Die Programmausführung wird trotz des Fehlers fortgesetzt.')
timeline = []
ip = ''
EOT = b'*EOT*'
animation = abbruch = False

input('\nKurze Anleitung:\n   Alt+Enter: Vollbild ein/aus\n   Strg+C: Programm beenden (ggf. mehrmals benutzen)\n   ansonsten: Anweisungen folgen ;)\n\nDieses Programm kann (auch im Fehlerfall) problemlos mit dem Fenster-X beendet werden. Mit [ ENTER ] gehts weiter...\n')
if (len(sys.argv)>1):
    ip = sys.argv[1].strip()
    print('Server-IP ist bereits vorkonfiguriert: '+ip)
else:
    ip = input('Bitte Server-IP eingeben: ')

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

def do_play():
    global timeline, abbruch
    abbruch = False
    print('...playing...')
    startpunkt = datetime.datetime.now()
    i = 0
    def note_spielen(freq, laenge):
        if animation:
            _thread.start_new_thread(winsound.Beep, (freq, laenge))
            faktor = (2.0**(1.0/12.0))
            taste = math.log(freq/110*faktor**(-9),faktor)
            print(('▓'*(int(taste)+27)+'▒░')[:78])
        else:
            winsound.Beep(freq, laenge)
    if (len(timeline)<=0):
        print('=> Kein Abspielen nötig, da Leertrack empfangen.\nWarte auf Server...')
        return False
    while True:
        if (datetime.datetime.now()>=(startpunkt+datetime.timedelta(0,0,timeline[i][2]*1000))):
            _thread.start_new_thread(note_spielen, (timeline[i][0],timeline[i][1]))
            i += 1
            if (i>(len(timeline)-1)):
                break
        if abbruch:
            print('[!] Abspielen abgebrochen.')
            abbruch = False
            break
    time.sleep(1)
    print('=> Abspielen beendet.\nWarte auf Server...')

while True:
    try:
        input('[ ENTER zum Verbinden ]')
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Kontaktiere Server...')
        client.connect((ip, 51337))
        print('Verbunden!')
        while True:
            print('Warte auf Server...')
            antwort = empfangen(client)
            if (antwort=='senddata'):
                print('Übertrage Daten...')
                timeline = empfangen(client)
                print('Transfer abgeschlossen, '+str(len(timeline))+' Timelineobjekte empfangen')
            elif (antwort=='check'):
                print('Bestätige Anwesenheit...')
                schicken(client,'Still alive!')
            elif (antwort=='animation_on'):
                animation = True
                print('Visualisierungen aktiviert!')
            elif (antwort=='animation_off'):
                animation = False
                print('Visualisierungen deaktiviert :(')
            elif (antwort=='tcp_launch'):
                print('\n'*100+'TCP-Launch initialisiert, warte auf Startschuss vom Server...')
                latenz = int(empfangen(client))
                time.sleep(latenz/1000.0)
                try:
                    _thread.start_new_thread(do_play,())
                except:
                    fehler_zeigen()
            elif (antwort=='udp_launch'):
                print('\n'*100+'UDP-Launch initialisiert, warte auf Startschuss vom Server...')
                try:
                    warter = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    warter.bind(('', 53731))
                    daten, addr = warter.recvfrom(128)
                    time.sleep(float(pickle.loads(daten))/1000.0)
                    _thread.start_new_thread(do_play,())
                except:
                    fehler_zeigen()
                finally:
                    warter.close()
            elif (antwort=='shutdown'):
                print('Der Server stellt seinen Betrieb ein!')
                break
            elif (antwort=='stop_playing'):
                print('Signal vom Server: Wiedergabe anhalten')
                abbruch = True
            elif (antwort=='logout_client'):
                print('Der Server hat den Logout angeordnet!')
                os.system('shutdown -l -t 10')
                break
            elif (antwort[:len('input:')]=='input:'):
                antwort = input('Server: '+antwort[len('input:'):]+' [ Bestätigen mit ENTER ]:\n')
                print('Sende Antwort...')
                schicken(client,antwort)
            else:
                print('Server: '+antwort)
    except KeyboardInterrupt:
        break
    except:
        fehler_zeigen()
    finally:
        client.close()
        print('\n---------- NEUSTART ----------')
print('Auf Wiedersehen!')
