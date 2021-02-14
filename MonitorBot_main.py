#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time

import telepot
from telepot.loop import MessageLoop

from lib.queries import queries
from secrets.tokens import TOKEN

sys.path.insert(0, sys.path[0])


def main():

    def chathandle(msg):

        content_type, chat_type, chat_id = telepot.glance(msg)
        chatlib = msg["from"]
        username = (chatlib["username"])

        if content_type is 'text':
            queries(mh_bot, chat_id, username, msg["text"])
    
    mh_bot = telepot.Bot(TOKEN)
    MessageLoop(mh_bot,
                {'chat': chathandle}).run_as_thread()
    while True:
        time.sleep(10)


if __name__ == "__main__":

    os.makedirs("./logs", exist_ok=True)
    if sys.platform != "linux":
        print("Warning: This bot is optimized for controlling linux machines.\n")
    main()
