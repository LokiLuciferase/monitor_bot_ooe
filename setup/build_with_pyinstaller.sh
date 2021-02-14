#!/usr/bin/env bash

# builds the bot with main in sourcepath to the build directory buildpath , then move it back here

sourcepath="/home/pi/scripts/monitor_bot_ooe"
buildpath="/home/pi/scripts/pyi_mbo"
binpath="/home/pi/scripts/monitor_bot_ooe/setup"

cd $sourcepath/setup

if [[ $USER != "root" ]]; then
    echo "This script requires root privileges."
    exit 1
fi

cp -r ../../monitor_bot_ooe/ $buildpath
cp buildspec $buildpath/build.spec
pushd $buildpath
sed -i "s|buildpath|${buildpath}|g" build.spec

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
mv $buildpath/dist .
cp -a $buildpath/scripts $binpath/dist
rm -rf $buildpath
chown -R $SUDO_USER dist

# write build note
echo "Token of this bot: ${token}
Telegram nicknames allowed to interact with this bot: ${valid_users}
Telegram ID of this bot (search for it): ${botname}" > dist/buildnotes.txt

echo "Build has completed."