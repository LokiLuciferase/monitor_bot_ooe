import os
import textwrap
from time import sleep

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
def divvy(fullmess):

    def photocall(msg):
        os.makedirs("./data/snaps", exist_ok=True)
        timestamp = True if "ts" in msg else False
        mode = "night" if "night" in msg else "default"
        try:
            if len(msg) == 1:
                return Answer(snap(), 'image')
            else:
                return Answer(snap(ts=timestamp, mode=mode, qual=msg[1]), 'image')
        except:
            return Answer(snap(ts=timestamp, mode=mode), 'image',
                          comments="An error occured in photocall. Using default settings.")

    def videocall(msg):
        os.makedirs("./data/snaps", exist_ok=True)
        if not lib.timelapse.time_lapse_running:
            return Answer(vid(int(msg[1])), 'vid')
        return Answer("Eine Zeitrafferaufnahme läuft gerade. Videofunktion außer Kraft gesetzt.", 'txt')

    def timelapsecall(msg):
        os.makedirs("./data/timelapses", exist_ok=True)
        if msg[1] == 'retrieve':
            lapsefile = lib.timelapse.get_timelapse()
            if lapsefile is not None:
                return Answer(lapsefile, "vid")
            if lib.timelapse.time_lapse_running:
                tlstatus = "Eine Aufnahme läuft momentan. Erwartete Endzeit (incl.Konversion):\n%s" % str(
                    lib.timelapse.endtimes)
            else:
                tlstatus = "Keine Aufnahme aktiv."
            return Answer("Es wurde kein neues Zeitraffervideo gefunden. %s" % tlstatus, 'txt')

        if not lib.timelapse.time_lapse_running:

            delay = msg[msg.index("waitfor") + 1] if "waitfor" in msg else 0
            fpers = msg[msg.index("fps") + 1] if "fps" in msg else "25"

            timestamp = lib.timelapse.start_timelapse(msg[1], msg[2], delay, fpers)
            sleep(1)
            totaldur = round(((60 / int(msg[1])) * int(msg[2])), 3)
            runmess = "Zeitraffer gestartet. Zeitsignatur: %s.\n" \
                      "Gesamtdauer der Aufnahme: %s min.\n" \
                      "Erwartete Endzeit (incl. Konversion):\n%s\n" \
                      "Abrufen des fertigen Zeitrafferfilms mit 'timelapse retrieve'." % (timestamp, totaldur,
                                                                                          str(lib.timelapse.endtimes))
            return Answer(runmess, 'txt')
        return Answer("Eine Zeitrafferaufnahme läuft bereits.", "txt")

    def relaiscall(msg):
        activate_relais(msg[1], msg[2])
        return Answer("Relais geschaltet.", "txt")

    def call_for_help(msg):
        tirade = "Dies ist der PiMonitorBot.\nFunktionen (ohne Anführungszeichen eingeben):\n" \
                 "'photo': Schießt ein Foto und sendet es. " \
                 "Optional: zusätzliches Argument 'hd' für HD Foto, 'ts' für Zeitstempel und 'night' für Nachtaufnahme.\n" \
                 "'video <sekunden>': Schießt ein Video von <sekunden> Länge und sendet es.\n" \
                 "'timelapse <photos_pro_h> <gesamtzahl_photos>': Zeitrafferaufnahme. Optional: 'waitfor <stunden>.\n" \
                 "'relais <1,2> <sekunden>': Schaltet das Relais <1,2> für <sekunden> ein.\n" \
                 "'$stats': gibt eine Übersicht über alle wichtigen Eckdaten des Raspberry Pi.\n" \
                 "'$stats -v': Wie $stats, aber ausführlichere infos.\n" \
                 "Alle anderen Kommandos werden als shell commands für den RPi interpretiert.\n"
        return Answer(tirade, "txt")

    def keyboardcall(msg):

        admin = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text='$exceptions'), KeyboardButton(text='$stats')],
            [KeyboardButton(text='$historylog'), KeyboardButton(text='$errorlog')],
            [KeyboardButton(text='$update'), KeyboardButton(text='$clean'), KeyboardButton(text='$reboot')],
            [KeyboardButton(text='keyboard AV'), KeyboardButton(text='keyboard relais')]
        ])

        auvi = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text='photo')],
            [KeyboardButton(text='video 5'), KeyboardButton(text='video 10')],
            [KeyboardButton(text='video 30'), KeyboardButton(text='video 60')],
            [KeyboardButton(text='timelapse retrieve')]
        ])

        rels = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text='relais 1 1'), KeyboardButton(text='relais 2 1')],
            [KeyboardButton(text='relais 1 5'), KeyboardButton(text='relais 2 5')],
            [KeyboardButton(text='relais 1 20'), KeyboardButton(text='relais 2 20')],
            [KeyboardButton(text='relais 1 inf'), KeyboardButton(text='relais 2 inf')],
        ])

        boards = {"admin": admin, "AV": auvi, "relais": rels}
        try:
            return Answer("Keyboard aktiviert.", "txt", keys=boards[msg[1]])
        except KeyError:
            return Answer("Unbekanntes Keyboard.", "txt")


    if fullmess[0] == '$':
        return Answer(macro(fullmess[1:]), "txt")

    splitmsg = fullmess.split()
    calldic = {'photo': photocall, 'video': videocall,
               'timelapse': timelapsecall, 'relais': relaiscall,
               'keyboard': keyboardcall, 'hilfe': call_for_help}

    try:
        return calldic[splitmsg[0]](splitmsg)
    except KeyError:
        return Answer(chaincall(fullmess), "txt")
    except IndexError:
        return Answer("Falsche Anzahl von Argumenten gegeben. Für Hilfe 'hilfe' eingeben.", 'txt')


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
                "reboot"      : "sudo reboot now"
                }

    if querystring == "macros":
        return "Existierende Makros:\n" + "".join(["%s : %s\n" % (x, y) for x, y in macrodic.items()])

    if querystring == "clean":
        if lib.timelapse.time_lapse_running:
            return chaincall("rm data/snaps/*")
        else:
            return chaincall("rm data/snaps/* && rm -rf data/timelapses/*")

    try:
        answer = macrodic[querystring]
        return chaincall(answer)
    except KeyError:
        return "Ein solches Makro existiert nicht."


# ReplyMarkupKeyboard definitions here


