# -*- coding: utf-8 -*-

__author__ = 'hal9000'
__all__ = ['Player']

import time

import xbmc

class Player:
    is_paused_app = False

    def hasMedia(self):
        return self._cond('Player.HasMedia')

    def hasAudio(self):
        return self._cond('Player.HasAudio')

    def hasDuration(self):
        return self._cond('Player.HasDuration')

    def hasVideo(self):
        return self._cond('Player.HasVideo')

    def isPlaying(self):
        return self._cond('Player.Playing')

    def isPaused(self):
        return self._cond('Player.Paused')

    def isPausedApp(self):
        return self.is_paused_app

    def isForwarding(self):
        return self._cond('Player.Forwarding')

    def isRewinding(self):
        return self._cond('Player.Rewinding')

    def canRecord(self):
        return self._cond('Player.CanRecord')

    def isRecording(self):
        return self._cond('Player.Recording')

    def isCaching(self):
        return self._cond('Player.Caching')

    def isSeekBar(self):
        return self._cond('Player.SeekBar')

    def isDisplayAfterSeek(self):
        return self._cond('Player.DisplayAfterSeek')

    def isSeeking(self):
        return self._cond('Player.Seeking')

    def isShowTime(self):
        return self._cond('Player.ShowTime')

    def isShowInfo(self):
        return self._cond('Player.ShowInfo')

    def isShowCodec(self):
        return self._cond('Player.ShowCodec')

    def isMuted(self):
        return self._cond('Player.Muted')

    def isRandom(self):
        return self._cond('Playlist.IsRandom')

    def isRepeat(self):
        return self._cond('Playlist.IsRepeat')

    def isRepeatOne(self):
        return self._cond('Playlist.IsRepeatOne')

    def getSpeedForwarding(self):
        if not self._cond('Player.Forwarding'):
            return 0
        for speed in ('32', '16', '8', '4', '2'):
            if self._cond(speed.join(['Player.Forwarding', 'x'])):
                return int(speed)
        return 0

    def getSpeedRewinding(self):
        if not self._cond('Player.Rewinding'):
            return 0
        for speed in ('2', '4', '8', '16', '32'):
            if self._cond(speed.join(['Player.Rewinding', 'x'])):
                return int(speed)
        return 0


    def getChapter(self):
        return self._get('Player.Chapter', 2)

    def getChapterCount(self):
        return self._get('Player.ChapterCount', 2)

    def getTime(self):
        return self._get('Player.Time', 1)

    def getTimeRemaining(self):
        return self._get('Player.TimeRemaining', 3)

    def getDuration(self):
        return self._get('Player.Duration', 1)

    def getSeekTime(self):
        return self._get('Player.SeekTime', 1)

    def getSeekOffset(self):
        return self._get('Player.SeekOffset', 1)

    def getVolume(self):
        return float(self._get('Player.Volume', 0).replace('dB', '').strip())

    def getCacheLevel(self):
        return self._get('Player.CacheLevel', 3)

    def getProgressCache(self):
        return self._get('Player.ProgressCache', 1)

    def getPosition(self):
        return self._get('Playlist.Position', 2)

    def getLength(self):
        return self._get('Playlist.Length', 2)

    def getProgress(self):
        duration = self.getDuration()
        if duration == 0:
            return 0.0
        watch = self.getTime()
        if watch == 0:
            return 0
        return 100.0*float(watch)/float(duration)


    def start(self, path, title=None, image=None, timeout=10):
        self.stop()
        if isinstance(path, unicode):
            path = path.encode('utf8')
        self._exe('xbmc.PlayMedia(' + path + ')')
        timeout = time.time() + float(timeout)
        while not self.isPlaying() and time.time() < timeout:
            xbmc.sleep(10)
        return self.isPlaying()


    def stop(self):
        if self.hasMedia():
            self._exe('xbmc.PlayerControl(Stop)')
            while self.hasMedia():
                xbmc.sleep(10)
        self.is_paused_app = False


    def pause(self):
        if not self.hasMedia():
            return False
        if self.isForwarding() or self.isRewinding():
            self._exe('xbmc.PlayerControl(Play)')
            while self.hasMedia() and (self.isForwarding() or self.isRewinding()):
                xbmc.sleep(10)
        if not self.hasMedia():
            return False
        self._exe('xbmc.PlayerControl(Play)')
        while self.hasMedia() and not self.isPaused():
            xbmc.sleep(10)
        if not self.isPaused():
            return False
        self.is_paused_app = True
        return True


    def play(self):
        if not self.hasMedia():
            return False
        if self.isPlaying():
            return True
        self._exe('xbmc.PlayerControl(Play)')
        while self.hasMedia() and not self.isPlaying():
            xbmc.sleep(10)
        self.is_paused_app = False
        return self.isPlaying()


    def _cond(self, cond):
        return bool(xbmc.getCondVisibility(cond))

    def _exe(self, exe):
        xbmc.executebuiltin(exe)

    def _get(self, label, act):
        r = xbmc.getInfoLabel(label).replace(' ', '').strip()
        if act == 1:
            pair = r.split(':')
            return (60*int(pair[0]) + int(pair[1])) if len(pair) == 2 else 0
        elif act == 2:
            return int(r) if r else 0
        elif act == 3:
            return int(r) if r else None
        else:
            return r
