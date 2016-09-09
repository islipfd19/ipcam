import os
import sys

import xbmc
import xbmcaddon
import xbmcgui

ACTION_PREVIOUS_MENU = 10
ACTION_BACKSPACE = 110
ACTION_NAV_BACK = 92
ACTION_STOP = 13

__addon__ = xbmcaddon.Addon()

__id__ = __addon__.getAddonInfo('id')
__icon__  = __addon__.getAddonInfo('icon').decode("utf-8")
__version__ = __addon__.getAddonInfo('version')

TEXTURE_FMT = os.path.join(__addon__.getAddonInfo('path'), 'resources', 'media', '{0}.png')


def get_string(ident):
    return __addon__.getLocalizedString(ident)

def get_setting(ident):
    return __addon__.getSetting(ident)

def open_settings():
    __addon__.openSettings()

def error_dialog(msg):
    xbmcgui.Dialog().ok(get_string(32000), msg, " ", get_string(32101))
    open_settings()
    sys.exit(1)

def log(message, level=xbmc.LOGNOTICE):
    xbmc.log("{0} v{1}: {2}".format(__id__, __version__, message), level=level)


class StopResumePlayer(xbmc.Player):
    def maybe_stop_current(self):
        if self.isPlaying():
            self.seek_time = self.getTime()
            self.previous_file = self.getPlayingFile()
            self.stop()
        else:
            self.previous_file = None

    def maybe_resume_previous(self):
        if self.previous_file is not None:
            self.play(self.previous_file)
            xbmc.sleep(1000) # wait for file to actually play before we can seek
            self.seekTime(self.seek_time - 2.)


class CameraControlDialog(xbmcgui.WindowDialog):
    def __enter__(self):
        return self
    
    def start(self):
        self.playVideo()
    
        focusTexture = TEXTURE_FMT.format('close-focus')
        noFocusTexture = TEXTURE_FMT.format('close')
        self.close_button = xbmcgui.ControlButton(1228, 20, 32, 32, "", focusTexture, noFocusTexture)
        self.addControl(self.close_button)
    
        self.doModal()

    def playVideo(self):
        self.player = StopResumePlayer()
        self.player.maybe_stop_current()
        url = __addon__.getSetting('url')
        if not url:
            error_dialog(get_string(32102))
        log(url)
        self.player.play(url)

    def onAction(self, action):
        if action in (ACTION_PREVIOUS_MENU, ACTION_BACKSPACE,
                      ACTION_NAV_BACK, ACTION_STOP):
            self.stop()

    def onControl(self, control):
        if control == self.close_button:
            self.stop()

    def stop(self):
        self.player.stop()
        self.close()
        self.player.maybe_resume_previous()

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()

with CameraControlDialog() as camera:
    camera.start()

