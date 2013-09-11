# -*- coding: utf-8 -*-

__author__ = 'hal9000'
__all__ = ['torrents']

import xbmcgui
import xbmcaddon

import config
import http
from exception import HttpError

def torrents(plugin=None):
    conf = config.config(plugin)
    try:
        return http.get(url = 'http://127.0.0.1:' + str(conf['port']) + '/torrents', params = {})
    except HttpError:
        xbmcgui.Dialog().ok('DelugeStream', *xbmcaddon.Addon('script.module.delugestream').getLocalizedString(30050).split('|'))
        return []
