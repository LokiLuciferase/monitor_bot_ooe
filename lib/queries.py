# queries writes the text input from the bot to a log file
# and determines the type of return value from textparser (text, video, image...)
# and calls the appropriate telepot function for sending it over telegram.

import os
from datetime import datetime

from lib.textparser import divvy
from secrets.tokens import valid_users


# sends queries to divvy and determines how to treat the Answer object returned by it.
# post txt, send video or image.
def queries(bot, chat_id, username, txtmess):

    print("Text message from @%s reading '%s'" % (username, txtmess))

    with open("./logs/history.log", "a") as logfile:
        if len(valid_users) and username not in valid_users:
            intrudermess = "INTRUDER detected. Username: %s. Message: %s" % (username, txtmess)
            print(intrudermess)
            logfile.write(intrudermess)
            return
        logfile.write("[%s] %s: %s\n" % (datetime.now(), username, txtmess))

    say = divvy(txtmess)

    if say.type == 'txt':
        if len(say.payload) != 0:
            if len(say.payload) > 1:
                for item in say.payload[:-1]:
                    #print("Response: '%s'" % item)
                    bot.sendMessage(chat_id, item)
                bot.sendMessage(chat_id, say.payload[-1])
            else:
                #print("Response: '%s'" % say.payload[0])
                bot.sendMessage(chat_id, say.payload[0], reply_markup=say.keys)

    elif say.type == 'image':
        print("Image: %s" % say.payload)
        with open(say.payload, "rb") as pic:
            bot.sendPhoto(chat_id, pic)

    elif say.type == 'vid':
        os.makedirs("./data/old_videos/", exist_ok=True)
        print("Video: %s" % say.payload)
        with open(say.payload, "rb") as vid:
            bot.sendVideo(chat_id, vid)
            os.rename(say.payload, "./data/old_videos/%s" % os.path.basename(say.payload))

    if say.comments:
        print("Comments: '%s'" % say.comments)
