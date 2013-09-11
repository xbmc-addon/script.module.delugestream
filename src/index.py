# -*- coding: utf-8 -*-

import sys

import xbmcplugin

import delugestream

torrents = delugestream.torrents()

xbmcplugin.endOfDirectory(int(sys.argv[1]))
