#!/usr/bin/env bash

pushd /home/pi/scripts/monitor_bot_ooe
git fetch --all
git reset --hard origin/master
chmod +x scripts/*
popd