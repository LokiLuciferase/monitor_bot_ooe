import textwrap

from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton

import lib.timelapse
from lib.processor import chaincall
from lib.camcont import snap, vid
from lib.relaiscont import activate_relais


# packages up response of bot, flavor of response and eventual changes in keyboard
class Answer:
    def __init__(self, values, itemtype, comments="", keys=None):
        self.type = itemtype
        self.comments = comments
        self.keys = keys

        if self.type == 'txt' and type(values) == str:
            wrapper = textwrap.TextWrapper(4096, replace_whitespace=False)
            self.payload = wrapper.wrap(values)

        if type(values) is tuple:
            wrapper = textwrap.TextWrapper(4096, replace_whitespace=False)
            self.payload = wrapper.wrap("\n".join(values))
        
        if self.type in ('vid', 'image'):
            self.payload = values


# divides text inputs from the user up and calls module functions
def divvy(msg):

    if msg[0] == '$':
        std = Answer(macro(msg[1:]), "txt")

    elif msg == 'photo':
        std = Answer(snap(), "image")

    elif msg.startswith('video'):
        if len(msg.split()) < 2:
            std = Answer("Die Videofunktion benötigt die Dauer des Videos in Sekunden.\n", "txt")
        elif lib.timelapse.time_lapse_running:
            std = Answer("Eine Zeitrafferaufnahme läuft gerade. Videofunktion außer Kraft gesetzt.", "txt")
        else:
            comm, dur = msg.split()
            std = Answer(vid(int(dur)), "vid")

    elif msg.startswith('timelapse'):
        if msg == "timelapse retrieve":
            lapsefile = lib.timelapse.get_timelapse()
            if lapsefile is not None:
                std = Answer(lapsefile, "vid")
            else:
                std = Answer("Es wurde kein neues Zeitraffervideo gefunden.", "txt")
        elif len(msg.split()) != 3:
            std = Answer("Die Zeitrafferfunktion benötigt folgende Argumente: timelapse <fotos pro stunde> <gesamtzahl>", "txt")
        else:
            comm, sph, ts = msg.split()
            timestamp = lib.timelapse.start_timelapse(sph, ts)
            totaldur = (60 / sph) * ts
            std = Answer("Zeitraffer gestartet. Zeitsignatur: %s\n"
                         "Gesamtdauer der Aufnahme: %s Minuten (=%s Stunden).\n"
                         "Abrufen des fertigen Zeitrafferfilms mit 'timelapse retrieve'." % (timestamp, totaldur, totaldur / 60), "txt")

    elif msg.startswith('relais'):
        if len(msg.split()) != 3:
            std = Answer("Funktionsweise: Relais <1,2> <sekundenzahl oder 'inf'>", "txt")
        else:
            comm, relid, dur = msg.split()
            activate_relais(relid, dur)
            std = Answer("Relais geschaltet.", "txt")

    elif msg.startswith("keyboard"):
        boards = {"admin": admin, "AV": auvi, "relais": rels}
        try:
            returnkb = boards[msg.split()[1]]
            std = Answer("Keyboard aktiviert.", "txt", keys=returnkb)
        except KeyError:
            std = Answer("Unbekanntes Keyboard.", "txt")

    elif msg == "hilfe":
        tirade = "Dies ist der PiMonitorBot.\nFunktionen (ohne Anführungszeichen eingeben):\n" \
                 "'photo': Schießt ein Foto und sendet es\n" \
                 "'video <sekunden>': Schießt ein Video von <sekunden> Länge und sendet es.\n" \
                 "'relais <1,2> <sekunden>': Schaltet das Relais <1,2> für <sekunden> ein.\n" \
                 "'$stats': gibt eine Übersicht über alle wichtigen Eckdaten des Raspberry Pi.\n" \
                 "'$stats -v': Wie $stats, aber ausführlichere infos.\n" \
                 "Alle anderen Kommandos werden als shell commands für den RPi interpretiert.\n"
        std = Answer(tirade, "txt")
        
    else:
        std = Answer(chaincall(msg), "txt")

    return std


def macro(querystring):

    # define useful macros here which would be tedious to write on a phone.
    macrodic = {"checkbots"   : "ps aux | grep -i '[b]ot'",
                "checksamba"  : "ps aux | grep -i 'smbd'",
                "stats"       : "./scripts/stats.sh",
                "stats -v"    : "./scripts/stats.sh -v",
                "bothistory"  : "cat ./logs/history.log | tail -500",
                "exceptions"  : "cat ./logs/monitorlog.log | grep 'Traceback' | wc -l",
                "historylog"  : "tail -30 logs/history.log",
                "errorlog"    : "tail -30 logs/monitorlog.log",
                "update"      : "scripts/update.sh",
                "clean"       : "rm data/snaps/*",
                "reboot"      : "sudo reboot now"
                }

    if querystring == "macros":
        return "Existierende Makros:\n" + "".join(["%s : %s\n" % (x, y) for x, y in macrodic.items()])

    try:
        answer = macrodic[querystring]
        return chaincall(answer)
    except KeyError:
        return "Ein solches Makro existiert nicht."


# ReplyMarkupKeyboard definitions here

admin = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='$exceptions'), KeyboardButton(text='$stats -v')],
    [KeyboardButton(text='$historylog'), KeyboardButton(text='$errorlog')],
    [KeyboardButton(text='$update'), KeyboardButton(text='$clean'), KeyboardButton(text='$reboot')]
])

auvi = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='photo')],
    [KeyboardButton(text='video 5'), KeyboardButton(text='video 10')],
    [KeyboardButton(text='video 30'), KeyboardButton(text='video 60')]
])

rels = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='relais 1 1'), KeyboardButton(text='relais 2 1')],
    [KeyboardButton(text='relais 1 5'), KeyboardButton(text='relais 2 5')],
    [KeyboardButton(text='relais 1 20'), KeyboardButton(text='relais 2 20')],
    [KeyboardButton(text='relais 1 inf'), KeyboardButton(text='relais 2 inf')],
])
