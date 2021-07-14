# -*- coding: utf-8 -*-

import os,xbmc,xbmcaddon,xbmcplugin,xbmcgui,xbmcvfs


integer = 1000

thisAddon = xbmcaddon.Addon(id='plugin.video.movieshark')

lang = xbmcaddon.Addon(id='plugin.video.movieshark').getLocalizedString

setting = xbmcaddon.Addon(id='plugin.video.movieshark').getSetting

setSetting = xbmcaddon.Addon(id='plugin.video.movieshark').setSetting

addon = xbmcaddon.Addon(id='plugin.video.movieshark')

#addon = xbmcaddon.Addon

addItem = xbmcplugin.addDirectoryItem

item = xbmcgui.ListItem

directory = xbmcplugin.endOfDirectory

content = xbmcplugin.setContent

property = xbmcplugin.setProperty

addonInfo = xbmcaddon.Addon(id='plugin.video.movieshark').getAddonInfo

#addonInfo = xbmcaddon.Addon().getAddonInfo

infoLabel = xbmc.getInfoLabel

condVisibility = xbmc.getCondVisibility

jsonrpc = xbmc.executeJSONRPC

window = xbmcgui.Window(10000)

dialog = xbmcgui.Dialog()

progressDialog = xbmcgui.DialogProgress()

windowDialog = xbmcgui.WindowDialog()

button = xbmcgui.ControlButton

image = xbmcgui.ControlImage

keyboard = xbmc.Keyboard

sleep = xbmc.sleep

execute = xbmc.executebuiltin

skin = xbmc.getSkinDir()

player = xbmc.Player()

playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)

resolve = xbmcplugin.setResolvedUrl

openFile = xbmcvfs.File

makeFile = xbmcvfs.mkdir

deleteFile = xbmcvfs.delete

listDir = xbmcvfs.listdir

transPath = xbmc.translatePath

skinPath = xbmc.translatePath('special://skin/')

addonPath = xbmc.translatePath(addonInfo('path'))

dataPath = xbmc.translatePath(addonInfo('profile')).decode('utf-8')

cacheFile = os.path.join(dataPath, 'cache.db')

metaFile = os.path.join(dataPath, 'meta.7.db')

viewsFile = os.path.join(dataPath, 'views.db')

bookmarksFile = os.path.join(dataPath, 'bookmarks.db')

capthaFile = os.path.join(dataPath, 'captcha.png')


def addonIcon():
    try: return os.path.join(addonInfo('path'), 'icon.png')
    except: pass


def addonFanart():
    try: return os.path.join(addonInfo('path'), 'fanart.jpg')
    except: pass


def infoDialog(message, heading=addonInfo('name'), icon='', time=3000):
    if icon == '': icon = addonIcon()
    try: dialog.notification(heading, message, icon, time, sound=False)
    except: execute("Notification(%s,%s, %s, %s)" % (heading, message, time, icon))


def okDialog(heading, line1):
    return dialog.ok(heading, line1)


def yesnoDialog(line1, line2, line3, heading=addonInfo('name'), nolabel='', yeslabel=''):
    return dialog.yesno(heading, line1, line2, line3, nolabel, yeslabel)


def selectDialog(list, heading=addonInfo('name')):
    return dialog.select(heading, list)


def version():
    num = ''
    try: version = addon('xbmc.addon').getAddonInfo('version')
    except: version = '999'
    for i in version:
        if i.isdigit(): num += i
        else: break
    return int(num)


def openSettings(query=None, id=addonInfo('id')):
    try:
        idle()
        execute('Addon.OpenSettings(%s)' % id)
        if query == None: raise Exception()
        c, f = query.split('.')
        execute('SetFocus(%i)' % (int(c) + 100))
        execute('SetFocus(%i)' % (int(f) + 200))
    except:
        return


def openPlaylist():
    return execute('ActivateWindow(VideoPlaylist)')


def refresh():
    return execute('Container.Refresh')


def idle():
    return execute('Dialog.Close(busydialog)')


def busy():
    return execute('ActivateWindow(busydialog)')


def queueItem():
    return execute('Action(Queue)')


def openPlaylist():
    return execute('ActivateWindow(VideoPlaylist)')


def getCurrentViewId():
    win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
    return str(win.getFocusId())
