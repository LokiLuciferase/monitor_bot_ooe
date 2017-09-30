import os

from datetime import datetime

from data.tokens import valid_users
from lib.textparser import divvy


def queries(bot, chat_id, username, txtmess):

    with open("./logs/history.log", "a") as logfile:
        if username not in valid_users:
            intrudermess = "INTRUDER detected. Username: %s. Message: %s" % (username, txtmess)
            print(intrudermess)
            logfile.write(intrudermess)
        logfile.write("[%s] %s: %s\n" % (datetime.now(), username, txtmess))

    print("Text message from @%s reading '%s'" % (username, txtmess))
    say = divvy(txtmess)

    if say.type == 'txt':
        if len(say.payload) != 0:
            if len(say.payload) > 1:
                for item in say.payload[:-1]:
                    print("Response: '%s'" % item)
                    bot.sendMessage(chat_id, item)
                bot.sendMessage(chat_id, say.payload[-1])
            else:
                bot.sendMessage(chat_id, say.payload[0], reply_markup=say.keys)

    elif say.type == 'image':
        print("Image: %s" % say.payload)
        with open(say.payload, "rb") as pic:
            bot.sendPhoto(chat_id, pic)

    elif say.type == 'vid':
        print("Video: %s" % say.payload)
        with open(say.payload, "rb") as vid:
            bot.sendVideo(chat_id, vid)
            #os.remove(say.payload)

    if say.comments:
        print("Comments: '%s'" % say.comments)
