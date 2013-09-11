# -*- coding: utf-8 -*-

__author__ = 'hal9000'
__all__ = ['play', 'resolve']

import os
import sys
import time
import threading

import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs

import config
import http
from files import files
from player import Player
from exception import DelugeStreamError, HttpError


MIN_BUFFER = 0.5


class Dialog(xbmcgui.WindowDialog):
    def onFocus(self, control):
        pass

    def onAction(self, action):
        if action.getId() in (9, 10, 92):
            self.callback_stop()

    def init(self, valign, lang, callback_stop):
        self.lang = lang
        self.callback_stop = callback_stop

        offset = self.calc_offset(valign)
        black = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../resources/media/black.jpg'))
        white = os.path.normpath(os.path.join(os.path.dirname(__file__), '../../resources/media/white.jpg'))

        self.setCoordinateResolution(0)

        self.label = xbmcgui.ControlLabel(1860, offset + 25, 1380, 40, u' ', textColor='0xAAFFFFFF', alignment=5)

        self.addControl(xbmcgui.ControlImage(0, offset, 1920, 440, black, colorDiffuse='0xDD000000'))
        self.addControl(xbmcgui.ControlImage(0, offset + 85, 1920, 1, white, colorDiffuse='0x22FFFFFF'))

        self.addControl(xbmcgui.ControlLabel(60, offset + 25, 370, 40, '[B]DelugeStream[/B]', font='font16', textColor='0xAAFFFFFF', alignment=4))
        #self.addControl(self.percent)
        self.addControl(self.label)
        
        self.progress = {}
        self.percent = {}
        self.bytes = {}
        for i, tag in enumerate(('buffer', 'file', 'total')):
            self.addControl(xbmcgui.ControlLabel(60, offset + 125 + 110*i, 370, 40, self.lang['label_' + tag], textColor='0xAAFFFFFF', alignment=4))
            self.addControl(xbmcgui.ControlImage(60, offset + 175 + 110*i, 1800, 8, white, colorDiffuse='0x22FFFFFF'))

            self.bytes[tag] = xbmcgui.ControlLabel(1680, offset + 125 + 110*i, 1000, 40, u' ', textColor='0xAAFFFFFF', alignment=5)
            self.addControl(self.bytes[tag])

            self.percent[tag] = xbmcgui.ControlLabel(1860, offset + 125 + 110*i, 130, 40, '[B]0%[/B]', font='font16', textColor='0xAAFFFFFF', alignment=5)
            self.addControl(self.percent[tag])

            self.progress[tag] = xbmcgui.ControlImage(60, offset + 175 + 110*i, 0, 8, white, colorDiffuse='0x77FFFFFF')
            self.addControl(self.progress[tag])



    def update(self, state, peers, seeds, dspeed, uspeed, filename, download, size, rbuffer, tdownload, tupload, tsize, tbuffer):
        if state in ('init', 'stop'):
            self.label.setLabel(self.lang[state])
        else:

            if state == 'seed':
                speed = self.human(uspeed, True)
            else:
                speed = self.human(dspeed, True)

            self.label.setLabel(self.lang['status'] % (seeds, peers, speed, self.lang[state]))

            for tag, b, s in (('buffer', rbuffer, tbuffer), ('file', download, size), ('total', tdownload, tsize)):
                percent = self.calc_percent(b, s)
                self.bytes[tag].setLabel(u' / '.join([self.human(b, False), self.human(s, False)]))
                self.percent[tag].setLabel(u'[B]' + str(percent) + u'%[/B]')
                self.progress[tag].setWidth(18*percent)


    def human(self, bytes, is_bit):
        tags = ('kbit', 'mbit', 'gbit', 'tbit') if is_bit else ('kb', 'mb', 'gb', 'tb')
        human = None
        for h, f in ((tags[0], 1024), (tags[1], 1024*1024), (tags[2], 1024*1024*1024), (tags[3], 1024*1024*1024*1024)):
            if bytes/f > 0:
                human = h
                factor = f
            else:
                break
        if human is None:
            return (u'%10.1f %s' % (bytes, self.lang[tags[0]])).replace(u'.0', u'').strip()
        else:
            return (u'%10.2f %s' % (float(bytes)/float(factor), self.lang[human])).strip()


    def calc_percent(self, num, total):
        if not total:
            return 0
        r = int(float(num)*100.0/float(total))
        return 100 if r > 100 else r


    def calc_offset(self, valign):
        if valign == 'top':
            return 0
        elif valign == 'bottom':
            return 635
        else:
            # middle
            return 315







class Play:
    def __init__(self, torrent, fid, title, image, plugin):
        self.torrent = torrent
        self.fid = fid
        self.title = title
        self.image = image

        self.config = config.config(plugin)

        self.filename = None

        self.stopped = False
        self.level = 0
        self.dialog = None
        self.player = None
        self.state = {}
        self.err = 0
        self.language()


    def run(self):
        self.tid = self.add()
        if not self.tid:
            xbmcgui.Dialog().ok('DelugeStream', *xbmcaddon.Addon('script.module.delugestream').getLocalizedString(30050).split('|'))
        else:
            self.state = {'state': 'init'}
            self.show()

            self.log('Start init')

            if not self.config['local']:
                self.clear_dir()
                self.buffer = 0
                self.thread_stopped = False
                self.thread = threading.Thread(target=self.download)
                self.thread.start()

            timeout = 0.0
            while not self.stopped:
                if timeout < time.time():
                    self.get_state()
                    self.check()
                    timeout = time.time() + 1.0
                else:
                    self.check()
                xbmc.sleep(50)

            self.log('Init stop')

            self.hide()
            if self.player:
                self.player.stop()

            if not self.config['local']:
                self.thread_stopped = True
                self.thread.join()
                self.clear_dir()

            self.log('Stopped')


    def check(self):
        if self.stopped:
            pass

        elif self.state['state'] == 'stop':
            self.log("Got the response 'stop'")
            self.stopped = True

        elif self.level == 0:
            print str(self.state)
            if self.state['state'] == 'down' and (self.state['buffer'] == 0 or self.state['fbuffer'] < self.state['tbuffer']):
                self.state['state'] = 'buffer'
                self.state['rbuffer'] = self.state['fbuffer']

            if self.state['state'] in ('up', 'seed', 'down'):

                self.log('First buffer is full')

                if self.config['local']:
                    self.level = 2
                else:
                    self.level = 1 if self.buffer < self.state['tbuffer'] else 2


        elif self.level == 1:
            self.state['state'] = 'copy'
            if self.buffer >= self.state['tbuffer']:
                self.level = 2
                self.log('First buffer has been copied')
                

        elif self.level == 2:
            self.log('Init player')
            self.player = Player()
            if self.player.start(self.filename, self.title, self.image):
                self.level = 3
                self.hide()
                self.log('Player started')
            else:
                self.hide()
                self.stopped = True
                self.log("Player didn't started")
                xbmcgui.Dialog().ok('DelugeStream', *xbmcaddon.Addon('script.module.delugestream').getLocalizedString(30051).split('|'))


        elif self.level == 3:
            if not self.player.hasMedia():
                self.stopped = True

            elif self.state['state'] in ('up', 'seed'):
                if self.player.isPausedApp():
                    self.hide()
                    self.player.play()
                self.level = 4

            elif self.state['state'] == 'down':
                watch = self.player.getProgress()

                if self.player.isPausedApp():
                    self.state['rbuffer'] = self.state['buffer'] - int(watch)*self.state['size']/100
                    if self.state['rbuffer'] < 0:
                        self.state['rbuffer'] = 0

                    if self.state['rbuffer'] >= self.state['tbuffer']:
                        self.state['rbuffer'] = self.state['tbuffer']
                        if not self.player.play():
                            self.stopped = True
                        self.hide()
                    else:
                        self.state['state'] = 'buffer'

                else:
                    min_buffer = 0
                    if self.player.isPlaying():
                        min_buffer = MIN_BUFFER
                    else:
                        min_buffer = MIN_BUFFER*self.player.getSpeedForwarding()

                    if min_buffer and 100.0*float(self.state['buffer'])/float(self.state['size']) - watch <= min_buffer:
                        self.state['state'] = 'buffer'
                        self.state['rbuffer'] = 0
                        self.show()
                        if not self.player.pause():
                            self.stopped = True
                            self.log('PAUSE FAIL')
                        else:
                            self.log('PAUSE SUCCESS')

        elif self.level == 4:
            if not self.player.hasMedia():
                self.stopped = True

        self.update()


    def get_state(self):
        try:
            response = http.get(url = 'http://' + self.config['host'] + ':' + str(self.config['port']) + '/state', params = {})
        except DelugeStreamError, e:
            self.err += 1
            if self.err > 10:
                if self.state['state'] in ('up', 'seed'):
                    self.err = 0
                else:
                    self.stop()
        else:
            self.err = 0

            if not self.config['local']:
                response['buffer'] = self.buffer

            if not self.filename and response.get('filename'):
                if self.config['local']:
                    self.filename = response['filename']
                else:
                    self.size = response['size']
                    self.filename = xbmc.translatePath('special://temp/delugestream/file' + str(int(time.time())) + '.' + str(response['filename'].split('.')[-1]))

            response['rbuffer'] = min(response['buffer'], response['tbuffer'])
            self.state = response


    def stop(self):
        self.stopped = True


    def show(self):
        if not self.dialog:
            self.dialog = Dialog()
            self.dialog.init(self.config['valign'], self.lang, self.stop)
            self.dialog.show()
        self.update()


    def hide(self):
        if self.dialog:
            self.dialog.close()
            del self.dialog
            self.dialog = None


    def update(self):
        if self.dialog:
            self.dialog.update(*[self.state.get(x) for x in ('state', 'peers', 'seeds', 'dspeed', 'uspeed', 'filename', 'download', 'size', 'rbuffer', 'tdownload', 'tupload', 'tsize', 'tbuffer')])


    def add(self):
        self.log('Try to add the torrent to Deluge')
        try:
            response = http.post(url = 'http://' + self.config['host'] + ':' + str(self.config['port']) + '/add', params = {'fid': self.fid, 'buffer_percent': self.config['buffer_percent'], 'buffer_min': self.config['buffer_min']}, files={'torrent_file': ('name.torrent', self.torrent)})
        except HttpError, e:
            self.log('Could not connect to the Deluge server')
            return None
        else:
            tid = response.get('tid')
            self.log('The torrent added. tid=' + str(tid))
            return tid


    def download(self):
        while not self.thread_stopped:
            if not self.filename:
                time.sleep(1)
            else:
                print self.filename
                try:
                    data = http.get(url = 'http://' + self.config['host'] + ':' + str(self.config['port']) + '/download', params = {'offset': self.buffer}, raw=True)
                except DelugeStreamError, e:
                    print str(e)
                    time.sleep(1)
                else:
                    print 'DATA: ' + str(len(data))
                    if data:
                        f = open(self.filename, 'ab')
                        f.write(data)
                        f.close()
                        self.buffer += len(data)
                        if self.buffer == self.size:
                            break


            


    def clear_dir(self):
        dirname = xbmc.translatePath('special://temp/delugestream/')
        if not xbmcvfs.exists(dirname):
            xbmcvfs.mkdir(dirname)
        else:
            files = xbmcvfs.listdir(dirname)[1]
            if files:
                for filename in files:
                    xbmcvfs.delete(dirname + filename)



    def language(self):
        tags = dict(
            status = 30000,

            init   = 30001,
            buffer = 30002,
            down   = 30003,
            up     = 30004,
            seed   = 30005,
            stop   = 30006,
            copy   = 30007,

            label_buffer = 30031,
            label_file   = 30032,
            label_total  = 30033,

            b  = 30100,
            kb = 30101,
            mb = 30102,
            gb = 30103,
            tb = 30104,

            bit  = 30200,
            kbit = 30201,
            mbit = 30202,
            gbit = 30203,
            tbit = 30204
        )
        addon = xbmcaddon.Addon('script.module.delugestream')
        self.lang = {}
        for tag, key in tags.iteritems():
            self.lang[tag] = addon.getLocalizedString(key)

    def log(self, msg):
        xbmc.log('DELUGESTREAM: ' + msg + ': ' + str(self.state), xbmc.LOGDEBUG)



def play(torrent, file_id, title=None, image=None, plugin=None):
    Play(torrent, file_id, title, image, plugin).run()

