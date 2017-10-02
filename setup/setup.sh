#!/usr/bin/env bash


pip install telepot picamera pifacedigitalio pifacecommons

# disable power saving mode of wifi
cat interfaces > /etc/network/interfaces
echo "options 8192cu rtw_power_mgnt=0 rtw_enusbss=1 rtw_ips_mode=1" > /etc/modprobe.d/8192cu.conf

# disable camera LED
echo "disable_camera_led=1" >> /boot/config.txt