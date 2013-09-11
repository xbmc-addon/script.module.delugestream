# -*- coding: utf-8 -*-

__author__ = 'hal9000'
__all__ = ['get', 'post']

import mimetools
import urllib2
import json

from exception import HttpError, ResponseError

def get(url, params, raw=False):
    query = []
    for key, value in params.iteritems():
        query.append('='.join([str(key), str(value)]))
    if query:
        url += '?' + '&'.join(query)
    return fetch(url, raw)


def post(url, params, files):
    parts, boundary = [], mimetools.choose_boundary()

    for key, value in params.iteritems():
        parts.append('--' + boundary)
        parts.append('Content-Disposition: form-data; name="%s"' % str(key))
        parts.append('')
        parts.append(str(value))
    field = files.keys()[0]
    parts.append('--' + boundary)
    parts.append('Content-Disposition: file; name="%s"; filename="%s"' % (field, files[field][0]))
    parts.append('Content-Type: application/x-bittorrent')
    parts.append('')
    parts.append(files[field][1])
    parts.append('--' + boundary + '--')
    parts.append('')
    body = '\r\n'.join(parts)

    req = urllib2.Request(url)
    req.add_header('Content-type', 'multipart/form-data; boundary=%s' % boundary)
    req.add_header('Content-length', len(body))
    req.add_data(body)

    return fetch(req)


def fetch(request, raw=False):
    try:
        data = urllib2.urlopen(request).read()
    except (urllib2.URLError, urllib2.HTTPError), e:
        raise HttpError(e)
    else:
        if raw:
            return data
        else:
            try:
                return json.loads(data)
            except Exception, e:
                raise ResponseError(e)