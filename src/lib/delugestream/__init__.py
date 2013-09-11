# -*- coding: utf-8 -*-

__author__ = 'hal9000'
__all__ = ['play', 'files', 'torrents', 'DelugeStreamError', 'HttpError', 'ResponseError', 'BencodeError']

from play import play
from files import files
from torrents import torrents
from exception import (DelugeStreamError, HttpError, ResponseError, BencodeError)

version = "0.0.1"
version_info = (0, 0, 1)
