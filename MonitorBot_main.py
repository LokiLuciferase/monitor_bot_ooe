# -*- coding: utf-8 -*-
import sys, os, socket
import time
import datetime

import telepot
from telepot.loop import MessageLoop
from urllib3.exceptions import NewConnectionError

from lib.textparser import divvy
from data.tokens import pimonitor_token, valid_users

sys.path.insert(0, sys.path[0])
TOKEN = pimonitor_token


def main():

    def chathandle(msg):

        content_type, chat_type, chat_id = telepot.glance(msg)
        chatlib = msg["from"]
        username = (chatlib["username"])
        txtmess = (msg["text"])
        try:

            with open("./logs/history.log", "a") as logfile:
                if username not in valid_users:
                    intrudermess = "INTRUDER detected. Username: %s. Message: %s" % (username, txtmess)
                    print(intrudermess)
                    logfile.write(intrudermess)
                logfile.write("[%s] %s: %s\n" % (datetime.datetime.now(), username, txtmess))

            print("Text message from @%s reading '%s'" % (username, txtmess))
            say = divvy(txtmess)

            if say.type == 'txt':
                if len(say.payload) != 0:
                    if len(say.payload) > 1:
                        for item in say.payload[:-1]:
                            print("Response: '%s'" % item)
                            mh_bot.sendMessage(chat_id, item)
                        mh_bot.sendMessage(chat_id, say.payload[-1])
                    else:
                        mh_bot.sendMessage(chat_id, say.payload[0], reply_markup=say.keys)

            elif say.type == 'image':
                print("Image: %s" % say.payload)
                with open(say.payload, "rb") as pic:
                    mh_bot.sendPhoto(chat_id, pic)

            elif say.type == 'vid':
                print("Video: %s" % say.payload)
                with open(say.payload, "rb") as vid:
                    mh_bot.sendVideo(chat_id, vid)
                    os.remove(say.payload)

            if say.comments:
                print("Comments: '%s'" % say.comments)

        except (NewConnectionError, socket.gaierror):
            connectmess = "MonitorBot: Verbindungsproblem aufgetreten.\nZum rebooten 'sudo reboot now' eingeben."
            with open("./logs/connections.log", "a") as conlog:
                conlog.write(datetime.datetime.now())
            mh_bot.sendMessage(chat_id, connectmess)
    
    mh_bot = telepot.Bot(TOKEN)
    MessageLoop(mh_bot,
                {'chat': chathandle}).run_as_thread()
    while True:
        time.sleep(10)


if __name__ == "__main__":

    if sys.platform != "linux":
        print("Warning: This bot is optimized for controlling linux machines.")
    main()
