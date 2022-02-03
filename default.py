import os, sys, re, xbmcaddon, xbmcgui, xbmcplugin, shutil, json, datetime
import resolveurl as urlresolver

from resources.lib import client
from resources.lib import control
from resources.lib import fanart
from resources.lib import metacache
from resources.lib import views
from resources.lib import debrid
from resources.lib.utils import py2_encode, py2_decode

if sys.version_info[0] == 3:
    from urllib.parse import urlencode, unquote, quote_plus
    import urllib.parse as urlparse
    from functools import reduce
else:
    from urllib import urlencode, unquote
    import urlparse

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
thisAddon = xbmcaddon.Addon(id='plugin.video.movieshark')
addonID = thisAddon.getAddonInfo('id')
thisAddonDir = py2_decode(xbmc.translatePath(thisAddon.getAddonInfo('path')))
sys.path.append(os.path.join(thisAddonDir, 'resources', 'lib'))
sys.path.append(os.path.join(thisAddonDir, 'resources', 'media'))
MediaDir = py2_decode(xbmc.translatePath(os.path.join(thisAddonDir, 'resources', 'media')))
SettingsDir = py2_decode(xbmc.translatePath(os.path.join(thisAddonDir, 'resources')))
UserDataDir = py2_decode(xbmc.translatePath(thisAddon.getAddonInfo('profile')))


if sys.platform == 'win32':
    download_script = thisAddonDir + '\\default.py'
    favourite_file = UserDataDir + '\\favourite.dat'
    favourite_tmp = UserDataDir + '\\favourite.tmp'
    watched_file = UserDataDir + '\\watched.dat'
    watched_tmp = UserDataDir + '\\watched.tmp'
    search_file = UserDataDir + '\\search.dat'
    settings_orig = SettingsDir + '\\settingsorig.xml'
    settings_temp = SettingsDir + '\\settingstemp.xml'
    settings_file = SettingsDir + '\\settings.xml'
    usersettings_file = UserDataDir + '\\settings.xml'
else:
    download_script = thisAddonDir + '/default.py'
    favourite_file = UserDataDir + '/favourite.dat'
    favourite_tmp = UserDataDir + '/favourite.tmp'
    watched_file = UserDataDir + '/watched.dat'
    watched_tmp = UserDataDir + '/watched.tmp'
    search_file = UserDataDir + '/search.dat'
    settings_orig = SettingsDir + '/settingsorig.xml'
    settings_temp = SettingsDir + '/settingstemp.xml'
    settings_file = SettingsDir + '/settings.xml'
    usersettings_file = UserDataDir + '/settings.xml'

sort_set = ['nezettseg','abc','feltoltve','imdb']

quality_set = ['0','2','3','4','5']

language_set = ['0','2','3']

category_set = [['0', '0'], ['18', '18+'], ['akcio', u'Akci\xF3'], ['animacio', u'Anim\xE1ci\xF3'], ['anime', 'Anime'], ['csaladi', u'Csal\xE1di'], ['dokumentum', 'Dokumentum'], ['dorama', u'\xC1zsiai'], ['drama', u'Dr\xE1ma'], ['eletrajzi', u'\xC9letrajzi'], ['fantasy', 'Fantasy'], ['haborus', u'H\xE1bor\xFAs'], ['horror', 'Horror'], ['kaland', 'Kaland'],
    ['krimi', 'Krimi'], ['misztikus', 'Misztikus'], ['romantikus', 'Romantikus'], ['sci-fi', 'Sci-Fi'], ['sorozat', 'Sorozat'], ['sport', 'Sport'], ['thriller', 'Thriller'], ['tortenelmi', u'T\xF6rt\xE9nelmi'], ['vigjatek', u'V\xEDgj\xE1t\xE9k'], ['western', 'Western'], ['zenes', u'Zen\xE9s']]

base_filmezz = control.setting('base_filmezz')


def decode_movie_info(lang, qual):
    l = lang.lower()
    if l == 'lhun':
        movie_info = '[COLOR green] SZINKRON[/COLOR]'
    elif l == 'lsub':
        movie_info = '[COLOR red] FELIRAT[/COLOR]'
    else:
        movie_info = '[COLOR yellow] NINCS FELIRAT[/COLOR]'

    movie_info = movie_info + ' | ' + '[COLOR blue]%s[/COLOR]' % qual

    return movie_info

def open_search_panel():
    search_text = ''
    keyb = xbmc.Keyboard('',u'Add meg a keresend\xF5 film c\xEDm\xE9t')
    keyb.doModal()

    if (keyb.isConfirmed()):
        search_text = keyb.getText()

    return search_text

def get_trailer(title, id):
    try:
        from resources.lib import trailer
        trailer.trailer().play(title, id)
    except:
        return

def build_kategoriak_directory(foldername, pagenum, action):
    for poz in range(len(category_set)):
        if not category_set[poz][0] == '0':
            try:
                url = build_url({'mode': 'main_folder', 'foldername': poz, 'pagenum': '0', 'action' : 'none'})
                li = xbmcgui.ListItem(py2_encode(category_set[poz][1]))
                li.setArt({'icon': MediaDir + '\\Kategoriak.png'})
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                        listitem=li, isFolder=True)
            except:
                pass

    control.content(addon_handle, 'addons')
    control.directory(addon_handle, cacheToDisc=True)

    return

def build_evek_directory(foldername, pagenum, action):
    for poz in range(1950,datetime.date.today().year+1,1):
        url = build_url({'mode': 'main_folder', 'foldername': poz, 'pagenum': '0', 'action' : 'none'})
        li = xbmcgui.ListItem(str(poz))
        li.setArt({'icon': MediaDir + '\\Evek.png'})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                     listitem=li, isFolder=True)

    control.content(addon_handle, 'addons')
    control.directory(addon_handle, cacheToDisc=True)

    return

def build_settings_directory():
    url = build_url({'mode': 'open_settings'})
    li = xbmcgui.ListItem(u'Be\xE1ll\xEDt\xE1sok')
    li.setArt({'icon': MediaDir + '\\Beallitasok.png'})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=False)

    url = build_url({'mode': 'viewmodes'})
    li = xbmcgui.ListItem(u'N\u00E9zet')
    li.setArt({'icon': MediaDir + '\\Beallitasok.png'})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    control.content(addon_handle, 'addons')
    control.directory(addon_handle, cacheToDisc=True)

def build_views_directory():
    try:
        control.idle()

        items = [(u'Tal\u00E1lati lista n\u00E9zet', 'results'), (u'Stream lista n\u00E9zet', 'streams')]

        select = control.selectDialog([i[0] for i in items], u'N\u00E9zet')

        if select == -1: return

        content = items[select][1]

        title = u"A N\u00C9ZET MENT\u00C9S\u00C9HEZ KATTINTS IDE"
        url = '%s?mode=addView&content=%s' % (base_url, content)

        poster = banner = 'DefaultVideo.png'
        fanart = control.addonFanart()

        item = control.item(label=title)
        item.setInfo(type='Video', infoLabels = {'title': title})
        item.setArt({'icon': poster, 'thumb': poster, 'poster': poster, 'banner': banner})
        item.setProperty('Fanart_Image', fanart)

        control.addItem(handle=addon_handle, url=url, listitem=item, isFolder=False)
        control.content(addon_handle, 'movies')
        control.directory(addon_handle, cacheToDisc=True)

        #from resources.lib.modules import cache
        #views.setView(content, {})
    except:
        return

def build_main_directory():
    if control.setting('dsearch')=='true':
        ssearch_icon = 'KeresesSimple.png'
        ssearch_label = u'Keres\xE9s szimpla'
        url = build_url({'mode': 'main_folder', 'foldername': 'Kereses', 'pagenum': '0', 'action' : 'Firstrun'})
        li = xbmcgui.ListItem(u'Keres\xE9s')
        li.setArt({'icon': MediaDir + '\\Kereses.png'})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)
    else:
        ssearch_icon = 'Kereses.png'
        ssearch_label = u'Keres\xE9s'

    url = build_url({'mode': 'main_folder', 'foldername': 'Kereses_szimpla', 'pagenum': '0', 'action' : 'none'})
    li = xbmcgui.ListItem(ssearch_label)
    li.setArt({'icon': MediaDir + '\\' + ssearch_icon})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    url = build_url({'mode': 'main_folder', 'foldername': 'Filmek', 'pagenum': '0', 'action' : 'none'})
    li = xbmcgui.ListItem(u'Filmek')
    li.setArt({'icon': MediaDir + '\\Filmek.png'})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    url = build_url({'mode': 'main_folder', 'foldername': 'Sorozatok', 'pagenum': '0', 'action' : 'none'})
    li = xbmcgui.ListItem(u'Sorozatok')
    li.setArt({'icon': MediaDir + '\\Sorozatok.png'})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    url = build_url({'mode': 'kategoriak', 'foldername': 'Kategoriak', 'pagenum': '0', 'action' : 'none'})
    li = xbmcgui.ListItem(u'Kateg\xF3ri\xE1k')
    li.setArt({'icon': MediaDir + '\\Kategoriak.png'})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    url = build_url({'mode': 'evek', 'foldername': 'Evek', 'pagenum': '0', 'action' : 'none'})
    li = xbmcgui.ListItem(u'\xC9vsz\xE1mok')
    li.setArt({'icon': MediaDir + '\\Evek.png'})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    url = build_url({'mode': 'main_folder', 'foldername': 'Kedvencek', 'pagenum': '0', 'action' : 'none'})
    li = xbmcgui.ListItem(u'Kedvencek')
    li.setArt({'icon': MediaDir + '\\Kedvencek.png'})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    url = build_url({'mode': 'openPlaylist'})
    li = xbmcgui.ListItem(u'Lej\xE1tsz\xE1si lista')
    li.setArt({'icon': MediaDir + '\\Playlist.png'})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    savefolder = py2_decode(control.setting('savefolder'))
    if not savefolder in ['Nincs megadva!', '']:
        url = savefolder
        li = xbmcgui.ListItem(u'Let\u00F6lt\u00E9sek')
        li.setArt({'icon': MediaDir + '\\Kategoriak.png'})
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                    listitem=li, isFolder=True)

    url = build_url({'mode': 'beallitasok', 'foldername': 'Beallitasok', 'pagenum': '0', 'action' : 'none'})
    li = xbmcgui.ListItem(u'Eszk\u00F6z\u00F6k')
    li.setArt({'icon': MediaDir + '\\Beallitasok.png'})
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                listitem=li, isFolder=True)

    try:
        os.remove(search_file)
    except:
        pass

    control.content(addon_handle, 'addons')
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

    return

def build_movie_directory(foldername, pagenum, action):
    try:
        the_file = open(search_file,'r')
        search_text = the_file.read().replace('\n', '')
        the_file.close()
    except:
        search_text = ''


    if foldername == 'Kereses' or foldername == 'Filmek' or foldername == 'Sorozatok' or foldername.isdigit():
        addon_settings = xbmcaddon.Addon(id='plugin.video.movieshark')
        movsort = addon_settings.getSetting('msort')
        if movsort == '0':
           msort = 'feltoltve'
        elif movsort == '1':
           msort = 'abc'
        elif movsort == '2':
           msort = 'nezettseg'
        else:
           msort = 'imdbrating'

        mquality = int(addon_settings.getSetting('mquality'))
        mlanguage = int(addon_settings.getSetting('mlanguage'))
        mcategory = int(addon_settings.getSetting('mcategory'))
        myear = addon_settings.getSetting('myear')
        mtype = addon_settings.getSetting('mtype')
        msearch = addon_settings.getSetting('msearch')

        if foldername.isdigit() and len(foldername) < 4:
            mcategory = int(foldername)


        if (action == 'Ujkereses' or action == 'Firstrun') and search_text == '':
                os.remove(settings_file)
                shutil.copyfile(settings_temp, settings_file)

                addon_settings = xbmcaddon.Addon(id='plugin.video.movieshark')
                addon_settings.setSetting('msearch', '')
                addon_settings.openSettings()

                msort = addon_settings.getSetting('msort')
                mquality = int(addon_settings.getSetting('mquality'))
                mlanguage = int(addon_settings.getSetting('mlanguage'))
                mcategory = int(addon_settings.getSetting('mcategory'))
                myear = addon_settings.getSetting('myear')
                mtype = addon_settings.getSetting('mtype')
                msearch = addon_settings.getSetting('msearch')
        if action == 'Firstrun':
                os.remove(settings_file)
                shutil.copyfile(settings_orig, settings_file)

        if action == 'none' and os.path.getsize(settings_file) == os.path.getsize(settings_temp):
                os.remove(settings_file)
                shutil.copyfile(settings_orig, settings_file)
                pagenum = '0'

        try:
                os.remove(search_file)
        except:
                pass

        if foldername == 'Filmek':
                mtype = '1'
                msearch = ''
        elif foldername == 'Sorozatok':
                mtype = '2'
                msearch = ''
        else:
            mtype = '0'

        if foldername.isdigit() and len(foldername) == 4:
            mfyear = int(foldername)
            mtype = '1'
        elif myear == 'true':
            try: mfyear = int(control.setting('mfyear'))
            except: mfyear = datetime.date.today().year
        else:
            mfyear = 0

        top_url = base_filmezz + '/kereses.php?p=' + pagenum + '&s=' + quote_plus(msearch) + '&w=0&o=' + msort + '&q=' + quality_set[mquality] + '&l=' + language_set[mlanguage] + '&e=' + str(mfyear) + '&c=' + category_set[mcategory][0] + '&t=' + str(mtype) + '&h=0'

        url_content = client.request(top_url)
        if not url_content:
            control.okDialog('Hiba', py2_decode(base_filmezz) + u' nem el\u00E9rhet\u0151. Pr\u00F3b\u00E1ld \u00FAjra k\u00E9s\u0151bb.')
            return
    
        result = client.parseDOM(url_content, 'ul', attrs={'class': 'row list-unstyled movie-list'})
        items = client.parseDOM(result, 'li', attrs={'class': 'col-md-2.+?'})
        for item in items:
            title = client.parseDOM(item, 'span', attrs={'class': 'title'})[0]
            title = py2_encode(client.replaceHTMLCodes(title))

            link = client.parseDOM(item, 'a', ret='href')[0]
            link = py2_encode(link)

            img = client.parseDOM(item, 'img', ret='src')[0]
            img = py2_encode(img)

            url = build_url({'mode': 'movie_folder', 'foldername': link, 'title': title, 'image': img})

            movie_info = client.parseDOM(item, 'ul', attrs={'class': 'list-inline cover-element movie-icons'})[0]
            lang = client.parseDOM(movie_info, 'li', ret='class')[0]
            qual = client.parseDOM(movie_info, 'li', ret='title')[1]
            movie_info = decode_movie_info(py2_encode(lang.strip()), py2_encode(qual.strip()))

            li = xbmcgui.ListItem(title + ' | ' + movie_info)
            li.setArt({'icon': img})
            file_data = link + '=spl=' + title + '=spl=' + movie_info
            if file_data in watched_file_data:
                li.setInfo( type='Video', infoLabels={ "Title": title + movie_info, 'playcount': 1, 'overlay': 7})
            if control.setting('TMDB')=='true' and control.setting('TMDBMain')=='true':
                meta = metacache.get(fanart.get, 720, title, link)
            else: meta = {}
            try: poster = meta['poster']
            except: poster = img
            li.setArt({'icon': poster, 'thumb': poster, 'poster': poster})
            if control.setting('fan_art') == 'true':
                if 'fanart' in meta and not meta['fanart'] == '0':
                    li.setProperty('fanart_image', meta['fanart'])
                else:
                    li.setProperty('fanart_image', poster)
            li.setInfo(type='Video', infoLabels = meta)
            url_conf1 = {'mode': 'main_folder', 'foldername': foldername, 'pagenum': '0', 'action': 'Ujkereses'}
            favourite_args1 = '?' + urlencode(url_conf1)

            url_conf = {'mode': 'favourite', 'foldername': link, 'title': title, 'info': movie_info, 'function': 'ADDF', 'pagenum' : pagenum}
            favourite_args = '?' + urlencode(url_conf)

            url_conf2 = {'mode': 'favourite', 'foldername': link, 'title': title, 'info': movie_info, 'function': 'ADDW', 'pagenum' : 'SEARCH'}
            favourite_args2 = '?' + urlencode(url_conf2)

            url_conf3 = {'mode': 'favourite', 'foldername': link, 'title': title, 'info': movie_info, 'function': 'REMOVEW', 'pagenum' : 'SEARCH'}
            favourite_args3 = '?' + urlencode(url_conf3)

            url_conf4 = {'mode': 'main_folder', 'foldername': 'Kereses_szimpla', 'pagenum': '0', 'action': 'none'}
            favourite_args4 = '?' + urlencode(url_conf4)

            if foldername == 'Kereses':
                li.addContextMenuItems([ (u'Hozz\xE1ad\xE1s a MovieShark kedvencekhez', 'XBMC.RunScript(' + download_script + ',' + str(addon_handle) + ',' + favourite_args + ')'),
				(u'Jel\xF6l\xE9s megtekintettk\xE9nt', 'XBMC.RunScript(' + download_script + ',' + str(addon_handle) + ',' + favourite_args2 + ')'),
				(u'Megtekintett jel\xF6l\xE9s t\xF6rl\xE9se', 'XBMC.RunScript(' + download_script + ',' + str(addon_handle) + ',' + favourite_args3 + ')')])
            else:
                li.addContextMenuItems([ (u'\xDAj keres\xE9s', 'XBMC.RunScript(' + download_script + ',' + str(addon_handle) + ',' + favourite_args1 + ')'),
				#(u'Szimpla keres\xE9s', 'XBMC.RunScript(' + download_script + ',' + str(addon_handle) + ',' + favourite_args4 + ')'),
				(u'Hozz\xE1ad\xE1s a MovieShark kedvencekhez', 'XBMC.RunScript(' + download_script + ',' + str(addon_handle) + ',' + favourite_args + ')'),
				(u'Jel\xF6l\xE9s megtekintettk\xE9nt', 'XBMC.RunScript(' + download_script + ',' + str(addon_handle) + ',' + favourite_args2 + ')'),
				(u'Megtekintett jel\xF6l\xE9s t\xF6rl\xE9se', 'XBMC.RunScript(' + download_script + ',' + str(addon_handle) + ',' + favourite_args3 + ')')])

            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                listitem=li, isFolder=True)

        if len(items) == 0:
                url = build_url({'mode': 'main_folder', 'foldername': foldername, 'pagenum': '0', 'action': 'Ujkereses'})
                li = xbmcgui.ListItem(u'[COLOR red]>> Nincs tal\xE1lat >>[/COLOR]')
                li.setArt({'icon': MediaDir + '\\Kereses.png'})
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                                        listitem=li, isFolder=False)

        if pagenum != '0':
                pagenum = int(pagenum)
                pagenum -= 1
                pagenum = str(pagenum)
                url = build_url({'mode': 'main_folder', 'foldername': foldername, 'pagenum': pagenum, 'action': 'none'})
                li = xbmcgui.ListItem(u'[COLOR blue]<< El\u0151z\u0151 oldal <<[/COLOR]')
                li.setArt({'icon': MediaDir + '\\Elozo.png'})
                poster = MediaDir + '\\Elozo.png'
                li.setArt({'icon': poster, 'thumb': poster, 'poster': poster})
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                                           listitem=li, isFolder=True)
                pagenum = int(pagenum)
                pagenum += 1
                pagenum = str(pagenum)

        if 'list-inline pagination' in url_content and 'telekkel nincs tal' not in url_content:
                pagenum = int(pagenum)
                pagenum += 1
                pagenum = str(pagenum)

                url = build_url({'mode': 'main_folder', 'foldername': foldername, 'pagenum': pagenum, 'action': 'none'})
                li = xbmcgui.ListItem(u'[COLOR green]>> K\xF6vetkez\u0151 oldal >>[/COLOR]')
                li.setArt({'icon': MediaDir + '\\Kovetkezo.png'})
                poster = MediaDir + '\\Kovetkezo.png'
                li.setArt({'icon': poster, 'thumb': poster, 'poster': poster})
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                   listitem=li, isFolder=True)

        control.content(addon_handle, 'movies')
        if args['pagenum'][0] != '0':
            xbmcplugin.endOfDirectory(addon_handle, updateListing = True)
        else:
            xbmcplugin.endOfDirectory(addon_handle, updateListing = False)
        if action == 'Ujkereses':
                xbmc.executebuiltin('XBMC.Container.Refresh()')


    elif foldername == 'Kereses_szimpla':
        msort = control.setting('msort')
        if search_text == '':
            search_text = open_search_panel()

        if search_text != '':
            top_url = base_filmezz + '/kereses.php?s=' + quote_plus(search_text) + '&o=' + str(msort)

            url_content = client.request(top_url)
            if not url_content:
                control.okDialog('Hiba', py2_decode(base_filmezz) + u' nem el\u00E9rhet\u0151. Pr\u00F3b\u00E1ld \u00FAjra k\u00E9s\u0151bb.')
                return

            result = client.parseDOM(url_content, 'ul', attrs={'class': 'row list-unstyled movie-list'})
            items = client.parseDOM(result, 'li', attrs={'class': 'col-md-2.+?'})

            for item in items:
                title = client.parseDOM(item, 'span', attrs={'class': 'title'})[0]
                title = py2_encode(client.replaceHTMLCodes(title))

                link = client.parseDOM(item, 'a', ret='href')[0]
                link = py2_encode(link)

                img = client.parseDOM(item, 'img', ret='src')[0]
                img = py2_encode(img)

                url = build_url({'mode': 'movie_folder', 'foldername': link, 'title': title, 'image': img})

                movie_info = client.parseDOM(item, 'ul', attrs={'class': 'list-inline cover-element movie-icons'})[0]
                lang = client.parseDOM(movie_info, 'li', ret='class')[0]
                qual = client.parseDOM(movie_info, 'li', ret='title')[1]
                movie_info = decode_movie_info(py2_encode(lang.strip()), py2_encode(qual.strip()))

                li = xbmcgui.ListItem(title + ' | ' + movie_info)
                li.setArt({'icon': img})
                file_data = link + '=spl=' + title + '=spl=' + movie_info
                if control.setting('TMDB') == 'true' and control.setting('TMDBMain')=='true':
                    meta = metacache.get(fanart.get, 720, title, link)
                else: meta = {}
                file_data = link + '=spl=' + title + '=spl=' + movie_info
                if file_data in watched_file_data:
                        meta.update=({ "Title": title + movie_info, 'playcount': 1, 'overlay': 7})
                try: poster = meta['poster']
                except: poster = img
                li.setArt({'icon': poster, 'thumb': poster, 'poster': poster})
                if control.setting('fan_art') == 'true':
                    if 'fanart' in meta and not meta['fanart'] == '0':
                        li.setProperty('fanart_image', meta['fanart'])
                    else:
                        li.setProperty('fanart_image', poster)
                li.setInfo(type='Video', infoLabels = meta)

                url_conf = {'mode': 'favourite', 'foldername': link, 'title': title, 'info': movie_info, 'function': 'ADDF', 'pagenum' : pagenum}
                favourite_args = '?' + urlencode(url_conf)

                url_conf2 = {'mode': 'favourite', 'foldername': link, 'title': title, 'info': movie_info, 'function': 'ADDW', 'pagenum' : search_text}
                favourite_args2 = '?' + urlencode(url_conf2)

                url_conf3 = {'mode': 'favourite', 'foldername': link, 'title': title, 'info': movie_info, 'function': 'REMOVEW', 'pagenum' : search_text}
                favourite_args3 = '?' + urlencode(url_conf3)
                li.addContextMenuItems([ (u'Hozz\xE1ad\xE1s a MovieShark kedvencekhez', 'XBMC.RunScript(' + download_script + ',' + str(addon_handle) + ',' + favourite_args + ')'),
				(u'Jel\xF6l\xE9s megtekintettk\xE9nt', 'XBMC.RunScript(' + download_script + ',' + str(addon_handle) + ',' + favourite_args2 + ')'),
				(u'Megtekintett jel\xF6l\xE9s t\xF6rl\xE9se', 'XBMC.RunScript(' + download_script + ',' + str(addon_handle) + ',' + favourite_args3 + ')')])

                xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                        listitem=li, isFolder=True)
            control.content(addon_handle, 'movies')
            xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)
        else:
            return

    elif foldername == 'Kedvencek':
        if os.path.isfile(favourite_file):
            the_file = open(favourite_file,'r')
            for line in the_file:
                movie_data = line.split('=spl=')
                img = base_filmezz + '/nagykep/' + movie_data[0].split('\/')[-1] + '.jpg'
                url = build_url({'mode': 'movie_folder', 'foldername': movie_data[0], 'title': movie_data[1], 'image': img})
                li = xbmcgui.ListItem(movie_data[1] + movie_data[2])
                li.setArt({'icon': img})
                file_data = movie_data[0] + '=spl=' + movie_data[1] + '=spl=' + movie_data[2].replace('\n', '')
                if control.setting('TMDB') == 'true' and control.setting('TMDBMain')=='true':
                    meta = metacache.get(fanart.get, 720, movie_data[1], movie_data[0])
                else: meta = {}
                file_data = movie_data[0] + '=spl=' + movie_data[1] + '=spl=' + movie_data[2].replace('\n', '')
                if file_data in watched_file_data:
                    meta.update=({ "Title": py2_decode(movie_data[1]) + movie_data[2], 'playcount': 1, 'overlay': 7})
                try: poster = meta['poster']
                except: poster = img
                li.setArt({'icon': poster, 'thumb': poster, 'poster': poster})
                if control.setting('fan_art') == 'true':
                    if 'fanart' in meta and not meta['fanart'] == '0':
                        li.setProperty('fanart_image', meta['fanart'])
                    else:
                        li.setProperty('fanart_image', poster)
                li.setInfo(type='Video', infoLabels = meta)
                url_conf = {'mode': 'favourite', 'foldername': movie_data[0], 'title': movie_data[1], 'info': movie_data[2], 'function': 'REMOVEF', 'pagenum' : '0'}
                favourite_args = '?' + urlencode(url_conf)

                url_conf2 = {'mode': 'favourite', 'foldername': movie_data[0], 'title': movie_data[1], 'info': movie_data[2].replace('\n', ''), 'function': 'ADDW', 'pagenum' : '0'}
                favourite_args2 = '?' + urlencode(url_conf2)

                url_conf3 = {'mode': 'favourite', 'foldername': movie_data[0], 'title': movie_data[1], 'info': movie_data[2].replace('\n', ''), 'function': 'REMOVEW', 'pagenum' : '0'}
                favourite_args3 = '?' + urlencode(url_conf3)
                li.addContextMenuItems([ (u'T\xF6rles a MovieShark kedvencekb\u0151l', 'XBMC.RunScript(' + download_script + ',' + str(addon_handle) + ',' + favourite_args + ')'),
                    (u'Jel\xF6l\xE9s megtekintettk\xE9nt', 'XBMC.RunScript(' + download_script + ',' + str(addon_handle) + ',' + favourite_args2 + ')'),
                    (u'Megtekintett jel\xF6l\xE9s t\xF6rl\xE9se', 'XBMC.RunScript(' + download_script + ',' + str(addon_handle) + ',' + favourite_args3 + ')')])

                xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                        listitem=li, isFolder=True)
            control.content(addon_handle, 'movies')
            xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=True)

            the_file.close()
        else:
            xbmcgui.Dialog().ok("Hiba", "Nincsenek kedvencek!")
  
    views.setView('results', {'skin.estuary': 55, 'skin.confluence': 500})

    try:
        os.remove(search_file)
    except:
        pass

    return

def find_videourl(foldername, foldertitle, folderimage, isdownload, meta, dname):
    if control.setting('savefolder') in ['', 'Nincs megadva!'] and isdownload == 'DOWNLOAD':
        xbmcgui.Dialog().ok(u'Let\xF6lt\xE9si hiba', u'Meg kell adnod egy let\xF6lt\xE9si k\xF6nyvt\xE1rat a be\xE1ll\xEDt\xE1sokban!')
        return

    f = u'Lej\u00E1tsz\u00E1s' if isdownload != 'DOWNLOAD' else u'Let\u00F6lt\u00E9s'

    try: meta = eval(meta)
    except: meta = {}
    try: year = meta['year']
    except: year = '0'

    u = client.request('{0}/link_to.php?{1}'.format(base_filmezz, foldername), output='geturl')
    log('MS HOST URL: {} '.format(py2_encode(u)))

    direct_url = None
    if dname != 'false':
        direct_url = debrid.resolver(u, dname)

    if not direct_url:
        hmf = urlresolver.HostedMediaFile(url=u, include_disabled=True, include_universal=False)
    
        if hmf.valid_url() == True:
            domain = hmf._domain
            try: direct_url = hmf.resolve()
            except Exception as e:
                control.infoDialog(domain, e.message)

    if not direct_url:
        return

    try: direct_url = py2_encode(direct_url)
    except: pass

    log('MS DIRECT URL: {} '.format(direct_url))

    if isdownload == 'DOWNLOAD':
        from resources.lib import downloader
        downloader.download(foldertitle, folderimage, direct_url)
        return

    else:
        item = control.item(path=direct_url)
        item.setArt({'icon': folderimage, 'thumb': folderimage, 'poster': folderimage, 'tvshow.poster': folderimage, 'season.poster': folderimage})
        item.setInfo(type='Video', infoLabels = meta)
        control.resolve(addon_handle, True, item)

        if control.setting('TRAKT') == 'true':
            control.window.setProperty('script.trakt.ids', json.dumps({'imdb': meta['imdb']}))

def build_movie_links(foldername, foldertitle, folderimage):
    top_url = urlparse.urljoin(base_filmezz, foldername)

    meta = metacache.get(fanart.get, 720, foldertitle, foldername)

    try: poster = meta['poster']
    except: poster = urlparse.urljoin(base_filmezz, folderimage)

    try: youtube_id = meta['youtube']
    except: youtube_id = '0'

    hostDict = getConstants()
    locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

    url_content = client.request(top_url)
    if not url_content:
        control.okDialog('Hiba', py2_decode(base_filmezz) + u' nem el\u00E9rhet\u0151. Pr\u00F3b\u00E1ld \u00FAjra k\u00E9s\u0151bb.')
        return

    vid_id = re.search('''\sfid\s*:\s*['"](\d+)''', url_content).group(1)

    parsedButtons = client.parseDOM(url_content, 'section', attrs={'class': 'content-box'})
    parsedButtons = client.parseDOM(parsedButtons, 'a', ret='href')
    query = [i for i in parsedButtons if '/index.php?id=' + vid_id in i][0]    

    r = client.request(query)
    items = client.parseDOM(r, 'li')

    filter = []
    for i in items:
        try:
            h = re.search('/ul>\n?([^<]+)', i)
            if h:
                host = py2_encode(h.group(1)).strip().split('.')[0].lower()
                host = [x[1] for x in locDict if host == x[0]]
                if not host: continue
                filter.append((host[0], py2_encode(i)))
        except:
            pass

    items = filter

    filter = []
    for d in debrid.debrid_resolvers:
        filter += [(d.name + ' | ' + i[0], i[1], d.name) for i in items if d.valid_url('', i[0]) == True]

    filter += [(i[0], i[1], 'false') for i in items if i[0] in hostDict]
    items = filter

    try:
        if not control.setting('trailer') == 'true': raise Exception()
        url = build_url({'mode': 'trailer', 'title': foldertitle, 'id': youtube_id})
        li = xbmcgui.ListItem('[COLOR orange]' + py2_decode(foldertitle) + u' EL\u0150ZETES[/COLOR]')
        li.setArt({'icon': base_filmezz + '/nagykep/' + folderimage + '.jpg'})
        li.setArt({'icon': poster, 'thumb': poster, 'poster': poster})
        li.setProperty('fanart_image', meta['fanart'])
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                        listitem=li, isFolder=False)
    except:
        pass

    foldertitle = re.sub('\s*\(\d{4}\)', '', foldertitle)

    for item in items:
        try:
            host = item[0]
            adurl = client.parseDOM(item[1], 'a', ret='href')[-1]
            try: adurl = py2_encode(unquote(adurl))
            except:
                log('Error unquote: {0}, URL: {1}'.format(e.message, py2_encode(adurl)))
            subs = adurl.find('http', 1)
            watch_id = adurl
            if subs > 1: watch_id = adurl[subs:]
            watch_id = urlparse.urlparse(watch_id).query
            try: serie_info = re.search('(\d+)\.?\s+epiz', py2_encode(item[1]).group(1))
            except: serie_info = '-1'
            if not serie_info == '-1':
                downloaded_name = foldertitle + ' ' + serie_info + '. epizod'
                try: tseason = str(int(foldername.rsplit('-', 2)[-2]))
                except: tseason = '1'
                meta.update({'tvshowtitle': meta['title'], 'type': 'episode', 'season': tseason, 'mediatype': 'episode', 'episode': serie_info})
            else:
                downloaded_name = foldertitle
            url_conf = {'mode': 'find_directurl', 'foldername': watch_id, 'title': downloaded_name, 'image': folderimage, 'isdownload' : ' ', 'meta' : meta, 'debrid': item[2]}
            url = build_url(url_conf)
            url_conf = {'mode': 'find_directurl', 'foldername': watch_id, 'title': downloaded_name, 'image': folderimage, 'isdownload' : 'DOWNLOAD', 'meta' : meta, 'debrid': item[2]}
            download_args = '?' + urlencode(url_conf)

            try:
                info = client.parseDOM(item[1], 'div', attrs={'class': 'col-sm-4 col-xs-12'})[0]
                info = client.replaceHTMLCodes(info)
                info = py2_encode(info.strip())
            except:
                info = ''

            lang = client.parseDOM(item[1], 'li', ret='class')[0]
            qual = client.parseDOM(item[1], 'li', ret='title')[1]
            movie_info = decode_movie_info(py2_encode(lang.strip()), py2_encode(qual.strip()))

            if not serie_info == '-1':
                content = 'episodes'
                li = xbmcgui.ListItem(serie_info + py2_encode(u'. epiz\xF3d') + movie_info + ' | ' + host.upper())
                li.setArt({'icon': folderimage})
            else:
                content = 'movies'
                li = xbmcgui.ListItem(movie_info + ' | ' + host.upper() + '[COLOR cyan] %s[/COLOR]' % info)
                li.setArt({'icon': folderimage})
            file_data = watch_id + '=spl=' + foldertitle + '=spl=' + folderimage
            if file_data in watched_file_data:
                meta.update({ "Title": foldertitle + folderimage, 'playcount': 1, 'overlay': 7})
            li.setArt({'icon': poster, 'thumb': poster, 'poster': poster})
            if control.setting('fan_art') == 'true':
                if 'fanart' in meta and not meta['fanart'] == '0':
                    li.setProperty('fanart_image', meta['fanart'])
                else:
                    li.setProperty('fanart_image', poster)
            li.setInfo(type='Video', infoLabels = meta)
            li.setProperty('IsPlayable', 'true')

            url_conf1 = {'mode': 'queueItem'}
            favourite_args1 = '?' + urlencode(url_conf1)

            url_conf2 = {'mode': 'favourite', 'foldername': watch_id, 'title': foldertitle, 'info': folderimage, 'function': 'ADDW', 'pagenum' : '0'}
            favourite_args2 = '?' + urlencode(url_conf2)

            url_conf3 = {'mode': 'favourite', 'foldername': watch_id, 'title': foldertitle, 'info': folderimage, 'function': 'REMOVEW', 'pagenum' : '0'}
            favourite_args3 = '?' + urlencode(url_conf3)

            li.addContextMenuItems([ (u'Vide\xF3 Let\xF6lt\xE9se', 'XBMC.RunScript(' + download_script + ',' + str(addon_handle) + ',' + download_args + ')'),
			(u'Hozz\xE1ad\xE1s a lej\xE1tsz\xE1si list\xE1hoz', 'XBMC.RunScript(' + download_script + ',' + str(addon_handle) + ',' + favourite_args1 + ')'),
			(u'Jel\xF6l\xE9s megtekintettk\xE9nt', 'XBMC.RunScript(' + download_script + ',' + str(addon_handle) + ',' + favourite_args2 + ')'),
			(u'Megtekintett jel\xF6l\xE9s t\xF6rl\xE9se', 'XBMC.RunScript(' + download_script + ',' + str(addon_handle) + ',' + favourite_args3 + ')'),
			(u'Lej\xE1tsz\xF3 kiv\xE1laszt\xE1sa','Action(SwitchPlayer)')])

            xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,
                                        listitem=li, isFolder=False)
            control.content(addon_handle, 'movies')
        except:
            pass

    xbmcplugin.endOfDirectory(addon_handle)
    views.setView('streams', {'skin.estuary': 55, 'skin.confluence': 50})

def getConstants():
    try:
        try: hosts = urlresolver.relevant_resolvers(order_matters=True)
        except: hosts = urlresolver.plugnplay.man.implementors(urlresolver.UrlResolver)
        hostDict = [i.domains for i in hosts if not '*' in i.domains]
        hostDict = [i.lower() for i in reduce(lambda x, y: x+y, hostDict)]
        hostDict = list(set(hostDict))
    except:
        hostDict = []
    return hostDict

def build_file(foldername, foldertitle, movieinfo, function, pagenum, traktid):

    if function == 'ADDF' or function == 'REMOVEF' or function == 'PURGEF':
        file = favourite_file
        tmpfile = favourite_tmp
    elif function == 'ADDW' or function == 'REMOVEW' or function == 'PURGEW':
        file = watched_file
        tmpfile = watched_tmp
    elif function == 'NEWSEARCH':
        file = search_file
    else:
        return

    file_data = foldername + '=spl=' + foldertitle + '=spl=' + movieinfo
    file_data = file_data.replace('\n','')

    if (function == 'ADDW' or function == 'REMOVEW') and pagenum != '0':
        the_file = open(search_file,'w+')
        the_file.write(pagenum + '\n')
        the_file.close()

    if ('ADDF' in function and file_data not in favourite_file_data) or ('ADDW' in function and file_data not in watched_file_data):
        the_file = open(file,'a+')
        the_file.write(file_data + '\n')
        the_file.close()
        the_tmp = open(tmpfile,'a+')
        the_tmp.write(file_data + '\n')
        the_tmp.close()
        if 'ADDW' in function:
            xbmc.executebuiltin("Container.Refresh")
    elif ('REMOVEF' in function and file_data in favourite_file_data) or ('REMOVEW' in function and file_data in watched_file_data):
        the_tmp = open(tmpfile,'r')
        the_file = open(file,'w')
        for line in the_tmp:
            if file_data not in line:
                the_file.write(line)
        the_file.close()
        the_tmp.close()

        os.remove(tmpfile)
        shutil.copyfile(file, tmpfile)

        xbmc.executebuiltin("Container.Refresh")
    elif function == 'NEWSEARCH' or function == 'PURGEP':
        try:
            os.remove(file)
            os.remove(tmpfile)
        except:
            the_file = open(file,'w')
            the_file.close()
            the_file = open(tmpfile,'w')
            the_file.close()
        xbmc.executebuiltin("Container.Refresh")

    return

args = urlparse.parse_qs(sys.argv[2][1:])

def build_url(query):
    return base_url + '?' + urlencode(query)

def log(msg, level=xbmc.LOGDEBUG):
    xbmc.log('### [%s] - %s' % (addonID, msg), level=level)

mode = args.get('mode', None)
meta = args.get('meta', 'NOTRAKT')

try:
    the_file = open(favourite_file,'r')
    favourite_file_data = the_file.read().replace('\n', '')
    the_file.close()
except:
    favourite_file_data = ''

try:
    the_file = open(watched_file,'r')
    watched_file_data = the_file.read().replace('\n', '')
    the_file.close()
except:
    watched_file_data = ''

if mode is None:

    build_main_directory()

elif mode[0] == 'main_folder':

    build_movie_directory(args['foldername'][0], args['pagenum'][0], args['action'][0])

elif mode[0] == 'beallitasok':

    build_settings_directory()

elif mode[0] == 'open_settings':

    if os.path.getsize(settings_file) == os.path.getsize(settings_temp):
        os.remove(settings_file)
        shutil.copyfile(settings_orig, settings_file)
    control.openSettings()

elif mode[0] == 'smrSettings':
    try: 
        urlresolver.display_settings()
    except: pass

elif mode[0] == 'viewmodes':

    build_views_directory()

elif mode[0] == 'addView':

    from resources.lib import views
    views.addView(args['content'][0])

elif mode[0] == 'kategoriak':

    build_kategoriak_directory(args['foldername'][0], args['pagenum'][0], args['action'][0])

elif mode[0] == 'evek':

    build_evek_directory(args['foldername'][0], args['pagenum'][0], args['action'][0])

elif mode[0] == 'movie_folder':

    build_movie_links(args['foldername'][0], args['title'][0], args['image'][0])

elif mode[0] == 'back_one_folder':

    xbmc.executebuiltin('Action(ParentDir)')

elif mode[0] == 'favourite':

    build_file(args['foldername'][0], args['title'][0], args['info'][0], args['function'][0], args['pagenum'][0], meta)

elif mode[0] == 'find_directurl':

    find_videourl(args['foldername'][0], args['title'][0], args['image'][0], args['isdownload'][0], args['meta'][0], args['debrid'][0])

elif mode[0] == 'trailer':

    get_trailer(args['title'][0], args['id'][0])

elif mode[0] == 'clear_meta':
    metacache.clear()

elif mode[0] == 'queueItem':
    control.queueItem()

elif mode[0] == 'openPlaylist':
    control.openPlaylist()
