import textwrap
from lib.processor import chaincall, macro
from lib.camcont import snap, vid
from lib.relaiscont import activate_relais
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton

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

def divvy(msg):

    if msg[0] == '$':
        std = Answer(macro(msg[1:]), "txt")

    elif msg == 'photo':
        std = Answer(snap(), "image")

    elif msg.startswith('video'):
        if len(msg.split()) < 2:
            std = Answer("Die Videofunktion benötigt die Dauer des Videos in Sekunden.\n", "txt")
        else:
            comm, dur = msg.split()
            std = Answer(vid(int(dur)), "vid")

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
        except:
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

admin = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='$exceptions'), KeyboardButton(text='$stats -v')],
    [KeyboardButton(text='tail -30 logs/history.log')],
    [KeyboardButton(text='tail -30 logs/monitorlog.log')]
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
