#!/usr/bin/env bash

# disable power saving mode of wifi
cat interfaces > /etc/network/interfaces
echo "options 8192cu rtw_power_mgnt=0 rtw_enusbss=0 rtw_ips_mode=1" > /etc/modprobe.d/8192cu.conf
