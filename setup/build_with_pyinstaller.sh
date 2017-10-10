#!/usr/bin/env bash

# builds the bot to a single binary in the folder /home/pi/scripts/pyi_mbo , then move it back here
# this path is defined in buildspec where it has to be changed if necessary

cd /home/pi/scripts/monitor_bot_ooe/setup

if [[ $USER != "root" ]]; then
    echo "This script requires root privileges."
    exit 1
fi

cp -r ../../monitor_bot_ooe/ ../../pyi_mbo
cp buildspec ../../pyi_mbo/build.spec
pushd ../../pyi_mbo

if [[ -n $1 ]]; then
    if [[ $1 = "--minimal" ]]; then
        echo "Building bot with minimal (shell commands only) functionality."
        sed -i 's/building=False/building=True/g' ./lib/textparser.py
    fi
else
echo "Building bot with full RPi functionality."
fi

# replace secrets.py in the compiled bot with the following:
token=$(cat secrets/token)
botname=$(cat secrets/botname)
valid_users=$(cat secrets/valid_users)
echo "TOKEN = '${token}'
valid_users = ${valid_users}
botname = '${botname}'
" > secrets/tokens.py

# compile
pyinstaller build.spec
popd
mv ../../pyi_mbo/dist .
cp -a ../scripts ./dist
rm -rf ../../pyi_mbo
chown -R $SUDO_USER dist

# write build note
echo "Token of this bot: ${token}
Telegram nicknames allowed to interact with this bot: ${valid_users}
Telegram ID of this bot (search for it): ${botname}" > dist/buildnotes.txt

echo "Build has completed."