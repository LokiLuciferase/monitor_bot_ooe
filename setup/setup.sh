#!/usr/bin/env bash


# install bot dependencies
pip3 install telepot picamera pifacedigitalio pifacecommon

# disable power saving mode of wifi
cat interfaces > /etc/network/interfaces
echo "options 8192cu rtw_power_mgnt=0 rtw_enusbss=1 rtw_ips_mode=1" > /etc/modprobe.d/8192cu.conf

# disable stats LEDs
echo "dtparam=act_led_trigger=none" >> /boot/config.txt
echo "dtparam=act_led_activelow=off" >> /boot/config.txt

echo "dtparam=pwr_led_trigger=none" >> /boot/config.txt
echo "dtparam=pwr_led_activelow=off" >> /boot/config.txt

# brute force disable LEDs
echo 0 >/sys/class/leds/led0/brightness
echo 0 >/sys/class/leds/led1/brightness

# disable camera LED
echo "disable_camera_led=1" >> /boot/config.txt

# overvolt and start X
echo "start_x=1" >> /boot/config.txt
echo "over_voltage=2" >> /boot/config.txt
