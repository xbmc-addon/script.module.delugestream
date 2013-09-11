# -*- coding: utf-8 -*-

__author__ = 'hal9000'
__all__ = ['config']

import socket

import xbmcaddon

def config(plugin=None):
    if not plugin:
        plugin = 'script.module.delugestream'

    addon = xbmcaddon.Addon(id=plugin)

    host = addon.getSetting(id='delugestream_host')
    
    return dict(
        host           = host,
        local          = bool(host == '127.0.0.1' or host in socket.gethostbyname_ex(socket.gethostname())[2]),
        port           = int(addon.getSetting(id='delugestream_port')),
        buffer_percent = int(addon.getSetting(id='delugestream_buffer_percent')),
        buffer_min     = int(addon.getSetting(id='delugestream_buffer_min')),
        valign         = 'middle'
    )
