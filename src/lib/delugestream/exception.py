# -*- coding: utf-8 -*-

__author__ = 'hal9000'
__all__ = ['DelugeStreamError', 'HttpError', 'ResponseError', 'BencodeError']

class DelugeStreamError(Exception):
    pass

class HttpError(DelugeStreamError):
    pass

class ResponseError(DelugeStreamError):
    pass

class BencodeError(DelugeStreamError):
    pass
