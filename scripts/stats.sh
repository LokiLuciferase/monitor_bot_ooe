#!/usr/bin/env bash

echo "===================="
echo "Raspberry Pi Status"
echo "===================="
echo ""
echo "Uptime:"
uptime
echo ""
echo "System temperature:"
cpu=$(</sys/class/thermal/thermal_zone0/temp)
echo "GPU: $(/opt/vc/bin/vcgencmd measure_temp)"
echo "CPU: temp=$((cpu/1000))'C"
echo ""
echo "Resource usage:"
iostat | grep -A 1 'avg-cpu'
echo ""
echo "File system:"
df -h
echo ""
echo "System stability: $(cat logs/monitorlog.log | grep "Traceback" | wc -l) python exceptions logged."
echo "Security:"
intruders=$(cat logs/history.log | grep -A 3 "INTRUDER")
if [[ $intruders = "" ]] ; then
    echo "No foreign attempts to control the bot were logged."
else
    echo $intruders
fi
if [[ $# -ne 0 ]] ; then
    if [[ $1 = "-v" ]] ; then
        echo ""
        echo "USB devices:"
        lsusb
        echo ""
        echo "Samba shared folders:"
        echo "Total size of /share-sd including folders: $(du -sh /share-sd)"
        ls -sh "/share-sd" | awk 'NR > 1 {print}'
        echo ""
        echo "Total size of /share including folders: $(du -sh /share)"
        ls -sh "/share" | awk 'NR > 1 {print}'
    fi
fi
