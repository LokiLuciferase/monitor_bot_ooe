# functions packages available functionalities up in a dictionary
# which is then returned to textparser.


import os
from textwrap import dedent
from time import sleep

from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton

from lib.textparser import Answer
from lib.textparser import minimal

try:
    import lib.timelapse
    from lib.camcont import snap, vid
    from lib.relaiscont import activate_relais
except ModuleNotFoundError:
    pass

TIMELAPSE_DEFAULT_PPH = 200
TIMELAPSE_MAX_PPH = 360
TIMELAPSE_MIN_FPS = 20
TIMELAPSE_MAX_FPS = 80


# if first call to bot by a user
def startcall(msg):
    startmess = """
    This is MonitorBot v0.1.
    Use this bot to issue shell commands to a computer via the standard bash syntax,
    and stdout/stderr of the called process is returned to the chat.
    
    For Raspberry Pi with installed Picamera module,
    functionality is included to snap photos, record videos and timelapse videos.
    For Raspberry Pi with installed PiFace2Digital (circuit board) module,
    functionality is included to remote control relais activation.
    
    For further information, enter 'hilfe'.
    """
    return Answer(dedent(startmess), "txt")


# make photo with picamera
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


# make video with picamera
def videocall(msg):
    os.makedirs("./data/snaps", exist_ok=True)
    if not lib.timelapse.time_lapse_running:
        return Answer(vid(int(msg[1])), 'vid')
    return Answer("A timelapse recording is running at the moment. Video function temporarily disabled.", 'txt')


# instantiate thread with timelapse photography function
def timelapsecall(msg):
    os.makedirs("./data/timelapses", exist_ok=True)
    if msg[1] == 'retrieve':
        lapsefile = lib.timelapse.get_timelapse()
        if lapsefile is not None:
            return Answer(lapsefile, "vid")
        if lib.timelapse.time_lapse_running:
            tlstatus = "A recording is currently running. Expected time of completion (incl. conversion):\n%s" % str(
                lib.timelapse.endtimes)
        else:
            tlstatus = "No recording is currently running.."
        return Answer("No new timelapse video has been found. %s" % tlstatus, 'txt')

    if not lib.timelapse.time_lapse_running:

        if len(msg) % 2 != 0:
            pph = int(msg[1]) if (int(msg[1]) < 360) else TIMELAPSE_MAX_PPH
            ptot = int(msg[2])
        else:
            pph = TIMELAPSE_DEFAULT_PPH  # allow for 200 photos per hour as default. Rather play with fps
            ptot = int(msg[1]) * pph  # make length of timelapse directly settable

        delay = int(msg[msg.index("waitfor") + 1]) if "waitfor" in msg else 0
        fpers = msg[msg.index("fps") + 1] if "fps" in msg else "25"

        if int(fpers) <= TIMELAPSE_MIN_FPS:
            fpers = TIMELAPSE_MIN_FPS
        elif int(fpers) >= TIMELAPSE_MAX_FPS:
            fpers = TIMELAPSE_MAX_FPS

        timestamp = lib.timelapse.start_timelapse(pph, ptot, delay, fpers)
        sleep(1)
        totaldur = round(((60 / pph) * ptot), 3)

        runmess_eng = """
        Timelapse started. Signature: {tp}
        Total duration of timelapse: {td} min
        Frames per second: {fs}
        Estimated time of completion: {tc}
        Retrieve the finished movie with 'timelapse retrieve'.
        """.format(tp=timestamp, td=totaldur, fs=fpers, tc=str(lib.timelapse.endtimes))

        return Answer(dedent(runmess_eng), 'txt')
    return Answer("A timelapse video recording is already running.", "txt")


# activate relais of PiFaceDigital II board
def relaiscall(msg):
    activate_relais(msg[1], msg[2])
    return Answer("Relais toggled.", "txt")


# Print help message
def call_for_help(msg):
    helpmess_eng = """
    MonitorBot defines some internal functions which should be entered without quotation marks.
    All unrecognized commands are sent to the underlying OS as a shell command, and the stdout
    (and potential stderr) output is returned.
    
    Internal functions:
        'help': display this message
        '$macros': display the available shell macros
        '$stats': displays some data of the underlying machine
        'keyboard admin': brings up a keyboard with the most important control commands for the bot.
    
    If the picamera module is installed:
        'keyboard AV': activates a keyboard with shortcuts for handling camera functions.
        'photo': take a snapshot. Optional arguments:
        <sd, hd, uhd> to select quality
        'ts' to add a timestamp
        'night' to make a long-exposure photo
    
        'video <duration_sec>': records a video.
    
        'timelapse <duration_h>: records a timelapse video in a seperate thread (which means you can continue using the bot).
        Optional arguments:
        'fps <frames_per_sec>' to change output framerate
        'waitfor <hours>' to wait for the designated time before starting timelapse.
    
    If the pifacedigitalio and pifacecommon modules are installed:
    'keyboard relais': brings up a keyboard with common shortcuts for handling relais.
    'relais <1,2> <duration_sec>': activate the relais 1 or 2 for the designated duration.
    
    """

    return Answer(dedent(helpmess_eng), "txt")


# activate new keyboard
def keyboardcall(msg):
    admin = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='$exceptions'), KeyboardButton(text='$stats')],
        [KeyboardButton(text='$historylog'), KeyboardButton(text='$errorlog')],
        [KeyboardButton(text='$update'), KeyboardButton(text='$clean'), KeyboardButton(text='$reboot')],
        [KeyboardButton(text='keyboard AV'), KeyboardButton(text='keyboard relais')]
    ])

    auvi = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='photo')],
        [KeyboardButton(text='video 10'), KeyboardButton(text='video 60')],
        [KeyboardButton(text='timelapse 2'), KeyboardButton(text='timelapse 10 fps 70')],
        [KeyboardButton(text='timelapse retrieve')]
    ])

    rels = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='relais 1 1'), KeyboardButton(text='relais 2 1')],
        [KeyboardButton(text='relais 1 5'), KeyboardButton(text='relais 2 5')],
        [KeyboardButton(text='relais 1 20'), KeyboardButton(text='relais 2 20')],
        [KeyboardButton(text='relais 1 inf'), KeyboardButton(text='relais 2 inf')],
    ])

    boards = {"admin": admin, "AV": auvi, "relais": rels} if not minimal else {"admin": admin}
    try:
        return Answer("Keyboard activated.", "txt", keys=boards[msg[1]])
    except KeyError:
        return Answer("Unknown keyboard.", "txt")


if not minimal:
    calldic = {'photo': photocall, 'video': videocall,
               'timelapse': timelapsecall, 'relais': relaiscall,
               'start': startcall, 'keyboard': keyboardcall, 'help': call_for_help}
else:
    calldic = {'start': startcall, 'keyboard': keyboardcall, 'help': call_for_help}

if __name__ == "__main__":
    os._exit(1)
