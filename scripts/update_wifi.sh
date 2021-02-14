#!/usr/bin/env bash
set -euo pipefail

[[ "$#" -ne 2 ]] && echo "No arguments supplied." && exit 1
# [[ ! -f "/etc/wpa_supplicant/wpa_supplicant.conf" ]] && echo "WPA config file not found." && exit 1

WIFI_SSID="$1"
WIFI_PW="$2"

cat <<EOF >>/etc/wpa_supplicant/wpa_supplicant.conf
network={
ssid="$WIFI_SSID"
psk="$WIFI_PW"
}
EOF

echo "Added SSID=$WIFI_SSID PW=$WIFI_PW to wpa_supplicant.conf."
