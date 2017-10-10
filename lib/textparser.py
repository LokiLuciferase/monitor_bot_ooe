# textparser determines the type of input (shell command, macro, or bot function command)
# and routes the input accordingly
# the response is packaged up in an Answer object and returned to the bot to be sent.


import textwrap
import sys

from lib.processor import chaincall

minimal = True if (len(sys.argv) == 2 and sys.argv[1] == "--minimal") else False
try:
    import lib.timelapse
    from lib.camcont import snap, vid
    from lib.relaiscont import activate_relais
except ModuleNotFoundError:
    minimal = True
    print("Running in minimal configuration (shell commands only).")


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


# define useful macros here which would be tedious to write on a phone.
def macro(querystring):

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
        return "Existing macros:\n" + "".join(["%s : %s\n" % (x, y) for x, y in macrodic.items()])

    if querystring == "clean":
        if lib.timelapse.time_lapse_running:
            return chaincall("rm -rf data/snaps/*")
        else:
            return chaincall("rm -rf data/snaps/* && rm -rf data/timelapses/*")

    try:
        answer = macrodic[querystring]
        return chaincall(answer)
    except KeyError:
        return "Such a macro does not exist."


# divides text inputs from the user up and calls module functions from hash of functions from functions.py
def divvy(fullmess):

    from lib.functions import calldic
    noslash = fullmess[1:] if fullmess[0] == '/' else fullmess # remove trailing telegram link character

    # if the message is a macro
    if noslash[0] == '$':
        return Answer(macro(fullmess[1:]), "txt")

    # if the message is no macro
    # try running bot function
    splitmsg = noslash.split()
    try:
        return calldic[splitmsg[0]](splitmsg)
    except KeyError:
        # if no appropriate function found, run shell call
        return Answer(chaincall(noslash), "txt")
    except IndexError:
        return Answer("Missing arguments. For help, enter 'help'.", 'txt')
