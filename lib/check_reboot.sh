#!/usr/bin/env bash

sleep 10  # give enough time on startup
running=$(ps aux | grep '[M]onitorBot_main.py')

if [[ $running -eq "" ]] ; then
    echo "[$(date)] Rebooted due to bot crash." >> /home/pi/scripts/monitor_bot_ooe/logs/reboots.log
    sudo reboot now
fi
