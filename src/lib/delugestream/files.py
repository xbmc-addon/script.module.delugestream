# -*- coding: utf-8 -*-

__author__ = 'hal9000'
__all__ = ['files']

import os

import bencode
from exception import BencodeError

def files(torrent):
    try:
        info = bencode.bdecode(torrent)['info']
    except bencode.BTFailure, e:
        raise BencodeError(e)
    else:
        if 'files' in info:
            return [dict(fid=str(i), path=x['path'], name=x['path'][-1], size=x['length']) for i, x in enumerate(info['files'])]
        else:
            return [dict(fid='0', path=[info['name']], name=info['name'], size=info['length'])]
