# Author: Yannick Croissant <yannick.croissant@gmail.com>
# URL: http://code.google.com/p/sickbeard/
#
# This file is part of Sick Beard.
#
# Sick Beard is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sick Beard is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sick Beard.  If not, see <http://www.gnu.org/licenses/>.

from bs4 import BeautifulSoup
from sickbeard import classes, show_name_helpers, logger
from sickbeard.common import Quality
import generic
import cookielib
import sickbeard
import urllib
import urllib2
import execjs
import json

class FTDBProvider(generic.TorrentProvider):

    def __init__(self):

        generic.TorrentProvider.__init__(self, "FTDB")

        self.supportsBacklog = True

        self.cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))

        self.url = "http://www.frenchtorrentdb.com"

        self.login_done = False

    def isEnabled(self):
        return sickbeard.FTDB

    def getSearchParams(self, searchString, audio_lang, subcat, french=None):
        if audio_lang == "en" and french==None:
            return urllib.urlencode( {
                'name': searchString,
                'exact' : 1,
                'group': subcat
            } ) + "&adv_cat%5Bs%5D%5B3%5D=101&adv_cat%5Bs%5D%5B4%5D=191&adv_cat%5Bs%5D%5B5%5D=197"
        elif audio_lang == "fr" or french:
            return urllib.urlencode( {
                'name': searchString,
                'exact' : 1,
                'group': subcat
            } ) + "&adv_cat%5Bs%5D%5B1%5D=95&adv_cat%5Bs%5D%5B2%5D=190"
        else:
            return urllib.urlencode( {
                'name': searchString,
                'exact' : 1,
                'group': subcat
            } ) + "&adv_cat%5Bs%5D%5B1%5D=95&adv_cat%5Bs%5D%5B2%5D=190&adv_cat%5Bs%5D%5B3%5D=101&adv_cat%5Bs%5D%5B4%5D=191&adv_cat%5Bs%5D%5B5%5D=197&adv_cat%5Bs%5D%5B7%5D=199&adv_cat%5Bs%5D%5B8%5D=201"

    def _get_season_search_strings(self, show, season):

        showNam = show_name_helpers.allPossibleShowNames(show)
        showNames = list(set(showNam))
        results = []
        for showName in showNames:
            results.append( self.getSearchParams(showName, show.audio_lang, 'series' ) + "&season=" + season)
        return results

    def _get_episode_search_strings(self, ep_obj, french=None):

        showNam = show_name_helpers.allPossibleShowNames(ep_obj.show)
        showNames = list(set(showNam))
        results = []
        for showName in showNames:
            results.append( self.getSearchParams( showName, ep_obj.show.audio_lang, 'series', french)+ "&" + urllib.urlencode({'episode': ep_obj.scene_episode, 'season': ep_obj.scene_season}))
            results.append( self.getSearchParams( "%s S%02dE%02d" % ( showName, ep_obj.scene_season, ep_obj.scene_episode), ep_obj.show.audio_lang, 'series', french ))
            results.append( self.getSearchParams( "%s %dx%02d" % ( showName, ep_obj.scene_season, ep_obj.scene_episode ), ep_obj.show.audio_lang, 'series', french ))
        return results

    def _get_title_and_url(self, item):
        return (item.title, item.url)

    def getQuality(self, item):
        return item.getQuality()

    def _doLogin(self, login, password):

        challenge = self.opener.open(self.url + '/?section=LOGIN&challenge=1')

        rawData = challenge.read()

        data = json.loads(rawData)

        # JavaScript code from the login page (needed to decrypt the challenge code)
        ctx = execjs.compile("""
            var a = '05f';
            function e(challenge){
                var s = ''
                for (var i in challenge){
                    s += '' + eval(challenge[i])
                }
                return s
            }
        """)

        data = urllib.urlencode({
            'username'    : login,
            'password'    : password,
            'secure_login': ctx.call('e', data['challenge']),
            'hash'        : data['hash']
        })

        self.opener.open(self.url + '/?section=LOGIN&ajax=1', data).read()

    def _doSearch(self, searchString, show=None, season=None, french=None):

        if not self.login_done:
            self._doLogin( sickbeard.FTDB_USERNAME, sickbeard.FTDB_PASSWORD )

        results = []
        searchUrl = self.url + '/?section=TORRENTS&' + searchString.replace('!','')
        logger.log(u"Search string: " + searchUrl, logger.DEBUG)

        r = self.opener.open( searchUrl )
        soup = BeautifulSoup( r, "html.parser" )
        resultsTable = soup.find("div", { "class" : "DataGrid" })
        if resultsTable:
            rows = resultsTable.findAll("ul")

            for row in rows:
                link = row.find("a", title=True)
                title = link['title']

                autogetURL = self.url + (row.find("li", { "class" : "torrents_name"}).find('a')['href'][1:]).replace('#FTD_MENU','&menu=4')
                r = self.opener.open( autogetURL , 'wb').read()
                soup = BeautifulSoup( r, "html.parser" )
                downloadURL = soup.find("div", { "class" : "autoget"}).find('a')['href']

                quality = Quality.nameQuality( title )
                if quality==Quality.UNKNOWN and title:
                    if '720p' not in title.lower() and '1080p' not in title.lower():
                        quality=Quality.SDTV
                if show and french==None:
                    results.append( FTDBSearchResult( self.opener, link['title'], downloadURL, quality, str(show.audio_lang) ) )
                elif show and french:
                    results.append( FTDBSearchResult( self.opener, link['title'], downloadURL, quality, 'fr' ) )
                else:
                    results.append( FTDBSearchResult( self.opener, link['title'], downloadURL, quality ) )

        return results

    def getResult(self, episodes):
        """
        Returns a result of the correct type for this provider
        """
        result = classes.TorrentSearchResult(episodes)
        result.provider = self

        return result

class FTDBSearchResult:

    def __init__(self, opener, title, url, quality, audio_langs=None):
        self.opener = opener
        self.title = title
        self.url = url
        self.quality = quality
        self.audio_langs=audio_langs

    def getQuality(self):
        return self.quality

provider = FTDBProvider()
