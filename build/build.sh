#!/bin/sh
cd `dirname $0`/../src
rm -rf $HOME/Library/Application\ Support/Kodi/addons/script.module.delugestream/*
cp -R ./* $HOME/Library/Application\ Support/Kodi/addons/script.module.delugestream/
