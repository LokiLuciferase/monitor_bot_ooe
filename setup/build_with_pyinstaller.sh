#!/usr/bin/env bash

# builds the bot to a single binary in the folder /home/pi/scripts/pyi_mbo , then move it back here
# this path is defined in buildspec where it has to be changed if necessary

if [[ $USER != "root" ]]; then
    echo "This script requires root privileges."
    exit 1
fi

if [[ -n $1 ]]; then
    if [[ $1 = "--minimal" ]]; then

        echo "Building bot with minimal (shell commands only) functionality."
        cp -r ../../monitor_bot_ooe/ ../../pyi_mbo
        cp buildspec ../../pyi_mbo/build.spec
        pushd ../../pyi_mbo
        sed -i 's/building=False/building=True/g' ./lib/textparser.py
        pyinstaller build.spec
        popd
    fi
else
echo "Building bot with full RPi functionality."
cp -r ../../monitor_bot_ooe/ ../../pyi_mbo
cp buildspec ../../pyi_mbo/build.spec
pushd ../../pyi_mbo
pyinstaller build.spec
popd
fi

mv ../../pyi_mbo/dist .
cp -a ../scripts ./dist
rm -rf ../../pyi_mbo
chown -R $SUDO_USER dist

# write build note
tokenfile="../../data/tokens.py"
allowed_users=$(grep "valid_users" $tokenfile)
thistoken=$(grep "TOKEN" $tokenfile)

echo "Token of this bot and its ID on telegram: ${thistoken}
Telegram nicknames allowed to interact with this bot: ${allowed_users}" > dist/buildnotes.txt