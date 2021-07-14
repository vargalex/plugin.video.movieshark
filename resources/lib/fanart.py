# -*- coding: utf-8 -*-

import os,sys,re,json,base64

from resources.lib import client
from resources.lib import control

if sys.version_info[0] == 3:
    import urllib.parse as urlparse
else:
    import urlparse

base_filmezz = control.setting('base_filmezz')
fanart_tv_art_link = 'http://webservice.fanart.tv/v3/%s/%s'
fanart_tv_headers = {'api-key': base64.b64decode('YTVmNDlkYjM0ZWJlZmYxZTRmNTIwNjQxYmExYWRjYTU=')}
tvdb_by_imdb = 'http://thetvdb.com/api/GetSeriesByRemoteID.php?imdbid=%s'

def get(title, url):
    try:
        meta = {'fanart': control.addonFanart()}

        top_url = urlparse.urljoin(base_filmezz, url)

        result = client.request(top_url)
        result = result.replace('\n', '').replace('\r', '').replace('\t', '')

        try:
            year = re.search('\((\d{4})\)', title).group(1)
            year = year.encode('utf-8')
        except:
            year = '0'
        if not year == '0': meta.update({'year': year})
        
        title = re.sub('\s*\(?\d{4}\)?', '', title)
        
        #try:
        #    title = re.sub('\d+\.\s*.vad', '', title.decode('utf-8')).strip()
        #    title = client.replaceHTMLCodes(title)
        #    title = title.encode('utf-8')
        #except:
        #    pass
        
        meta.update({'title': title, 'label': title})

        try:
            imdb = re.search('/title/(tt\d{5,7})', result).group(1)
            imdb = imdb.encode('utf-8')
        except:
            imdb = '0'
        if not imdb == '0': meta.update({'imdb': imdb})

        try:
            director = client.parseDOM(result, 'ul', attrs = {'class': 'list-unstyled'})[-2]
            director = client.parseDOM(director, 'a')
            director = [i.encode('utf-8') for i in director]
        except:
            director = '0'
        if not director == '0': meta.update({'director': director})

        try:
            cast = client.parseDOM(result, 'ul', attrs = {'class': 'list-unstyled'})[-1]
            cast = client.parseDOM(cast, 'a')
            cast = [i.encode('utf-8') for i in cast]
        except:
            cast = '0'
        if not cast == '0': meta.update({'cast': cast})

        try:
            duration = 0
        except:
            duration = '0'

        try:
            genre = client.parseDOM(result, 'ul', attrs = {'class': 'list-inline category'})
            genre = client.parseDOM(genre, 'a')
            genre = [i.encode('utf-8') for i in genre]
        except:
            genre = '0'
        if not genre == '0': meta.update({'genre': genre})

        try:
            rate = client.parseDOM(result, 'div', attrs = {'class': 'sidebar-article details'})[0]
            
            try:
                rating = re.search('Filmezz pontsz.+?/span>([^<]+)', rate).group(1)
                rating = rating.encode('utf-8')
            except:
                rating = '0'
            if not rating == '0': meta.update({'rating': rating})
            
            try:
                votes = re.search('>\s*(\d+)\sszav\.<', rate).group(1)
                votes = votes.encode('utf-8')
            except:
                votes = '0'
            if not votes == '0': meta.update({'votes': votes})
        except:
            pass

        try:
            poster = client.parseDOM(result, 'img', ret = 'src')[0]
            poster = urlparse.urljoin(base_filmezz, poster)
            poster = poster.encode('utf-8')
        except:
            poster = '0'
        if not poster == '0': meta.update({'poster': poster})

        try:
            plot = result.split('film_ertekeles.php')[1].split('</section>')[0]
            plot = client.parseDOM(plot, 'div')[0]
            plot = plot.replace('<br>', '\n').strip()
            plot = client.replaceHTMLCodes(plot)
            plot = plot.encode('utf-8')
        except:
            plot = '0'
        if not plot == '0': meta.update({'plot': plot})

        try:
            youtube = re.search('youtu\.be\/([^"]+)', result).group(1)
            youtube = youtube.encode('utf-8')
        except:
            youtube = '0'
        if not youtube == '0': 
            meta.update({'youtube': youtube})

        try:
            if not control.setting('fan_art') == 'true' or imdb == '0': raise Exception()
            if 'tv-sorozat' in genre.lower():
                url = tvdb_by_imdb % imdb

                result = client.request(url, timeout='10')

                try: tvdb = client.parseDOM(result, 'seriesid')[0]
                except: tvdb = '0'

                try: name = client.parseDOM(result, 'SeriesName')[0]
                except: name = '0'
                dupe = re.findall('[***]Duplicate (\d*)[***]', name)
                if dupe: tvdb = str(dupe[0])

                if tvdb == '' or tvdb == '0': raise Exception()

                fanart_tv_link = fanart_tv_art_link % ('tv', tvdb)
            else: fanart_tv_link = fanart_tv_art_link % ('movies', imdb)
            art = client.request(fanart_tv_link, headers=fanart_tv_headers, timeout='10', error=True)
            art = json.loads(art)
        except:
            art = False

        try:
            if 'showbackground' in art: fanart = art['showbackground']
            elif 'moviebackground' in art: fanart = art['moviebackground']
            else: fanart = art['moviethumb']
            fanart = [x for x in fanart if x.get('lang') == 'en'][::-1] + [x for x in fanart if x.get('lang') == ''][::-1]
            fanart = fanart[0]['url'].encode('utf-8')
        except:
            fanart = '0'

        try:
            if 'tvbanner' in art: banner = art['tvbanner']
            else: banner = art['moviebanner']
            banner = [x for x in banner if x.get('lang') == 'en'][::-1] + [x for x in banner if x.get('lang') == ''][::-1]
            banner = banner[0]['url'].encode('utf-8')
        except:
            banner = '0'

        try:
            if 'hdtvlogo' in art: clearlogo = art['hdtvlogo']
            elif 'hdmovielogo' in art: clearlogo = art['hdmovielogo']
            else: clearlogo = art['clearlogo']
            clearlogo = [x for x in clearlogo if x.get('lang') == 'en'][::-1] + [x for x in clearlogo if x.get('lang') == ''][::-1]
            clearlogo = clearlogo[0]['url'].encode('utf-8')
        except:
            clearlogo = '0'

        try:
            if 'hdclearart' in art: clearart = art['hdclearart']
            elif 'hdmovieclearart' in art: clearart = art['hdmovieclearart']
            else: clearart = art['clearart']
            clearart = [x for x in clearart if x.get('lang') == 'en'][::-1] + [x for x in clearart if x.get('lang') == ''][::-1]
            clearart = clearart[0]['url'].encode('utf-8')
        except:
            clearart = '0'

        meta.update({'trailer': '%s?mode=trailer&title=%s&id=%s' % (sys.argv[0], title, youtube), 'fanart': fanart, 'banner': banner, 'clearlogo': clearlogo, 'clearart': clearart})

        return meta
    except:
        return meta
