#!/usr/bin/env bash

if [[ -n "$1" ]]; then
    # if an cl argument is given, use arg as branch name
    pushd /home/pi/scripts/monitor_bot_ooe
    git fetch --all
    git reset --hard origin/$1
    chmod +x scripts/*
    popd
else
    pushd /home/pi/scripts/monitor_bot_ooe
    git fetch --all
    git reset --hard origin/master
    chmod +x scripts/*
    popd
fi