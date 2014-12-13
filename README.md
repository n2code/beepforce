Beepforce United
=========
:sound: *Let's put that old PC speaker on your motherboard to use!* :notes:

This is a project I worked on in my spare time at school back in 2010. The python script can play self-composed or transcribed songs on the tiny internal speaker/buzzer/beeper or whatever you want to call it which may or may not be present on your motherboard. (They are quite rare these days but if there is none the OS sometimes makes up for it by generating the sound via the sound card... Of course the real deal is way better :smile:)

Requirements:
- **Python 3** installed
- any **Windows** OS (I used the `winsound` module which provides `Beep(frequency, duration)` but feel free to contribute an alternative - I would be more than happy to see a platform-independent solution)

Features:
- 3 demo songs included!
- songs with multiple tracks
- frequency visualisation
- exporting tracks as standalone python script
- **orchestration: client&server for parallel playback** (hence: Beepforce *United* :wink:)
- sorry, no english translation

## First steps
### Standalone
**beepforce.py** is the main script. It can load and play a song by itself and provides a server for centralised distribution. Once started you are presented with a terminal. You can list all commands by entering
```
>>> commands
```
and you can get further help with
```
>>> help [command]
```

Let's go for a song:
```
>>> load tetris.bfu
Analysiere Datei...
- Dateiformat: 6
- Musikstück: Tetris Theme, Type A
- Komponist: -
- Autor: Niko
- Einheitendauer (ms): 100
- Standardakzentuierung: t
- Oktavierung: 1
=> Datei geladen, 3 Tracks gefunden.
```
Three tracks were found and we chose the first one which is usually the lead melody:
```
>>> track 1
Verarbeite Spur 1...
Akzentuiere & optimiere Track...
=> Track konvertiert, 254 Noten und Pausen notiert.
```
This track consists of 254 notes and rests. If we played the song right now it would be executed sequentially which might sound a bit wonky because of the minor delay in between the execution of each line. Therefore you normally want to put these on a timeline meaning that by threaded execution the accuracy is greatly improved. A cut-off interval has to be specified to force pauses between notes - otherwise some speakers skip a few notes in rapid succession.
20 milliseconds tend to work well:
```
>>> timeline 20
Erstelle Timeline...
Verkürze Noten...
=> Timeline erstellt, 133 Objekte, Liedlänge 51.2sek, 12 Kürzungen
```
The song is about 52 seconds long and ready to be played - have fun!
```
>>> play
Quelle: Timeline
[ Musik starten mit Enter ]
...playing...

▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒░ 1319 Hz
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒░ 988 Hz
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒░ 1047 Hz
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒░ 1175 Hz
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒░ 1319 Hz
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒░ 1175 Hz
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒░ 1047 Hz
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒░ 988 Hz
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒░ 880 Hz
...
```
### Server mode
*TODO*
