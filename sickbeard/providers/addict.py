# -*- coding: latin-1 -*-
# Author: Raver2046 <raver2046@gmail.com>
# based on tpi.py
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
#  GNU General Public License for more details.
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
import re

class ADDICTProvider(generic.TorrentProvider):

    def __init__(self):
        
        generic.TorrentProvider.__init__(self, "ADDICT")

        self.supportsBacklog = True
        
        self.cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        
        self.url = "https://addict-to.net"
        
        self.login_done = False
        self.failed_login_logged = False
        self.successful_login_logged = False
        
    def isEnabled(self):
        return sickbeard.ADDICT
    
    def getSearchParams(self, searchString, audio_lang, french=None, fullSeason=False):
        results = []    
        if audio_lang == "en" and french==None:
            results.append( urllib.urlencode( {
                'search': searchString                            
            } ) + "&category=31%3B33%3B51" )
        elif audio_lang == "fr" or french:
            results.append( urllib.urlencode( {
                'search': searchString
            } ) + "&category=30%3B32%3B34")
        else:
            results.append( urllib.urlencode( {
                'search': searchString
            } ) + "&category=30%3B31%3B32%3B33%3B34%3B51%3B35")
        return results
        
    def _get_season_search_strings(self, show, season):

        showNam = show_name_helpers.allPossibleShowNames(show)
        showNames = list(set(showNam))
        results = []
        for showName in showNames:
            results.extend( self.getSearchParams(showName + " saison%d" % season, show.audio_lang, fullSeason=True))
            results.extend( self.getSearchParams(showName + " season%d" % season, show.audio_lang, fullSeason=True))
            results.extend( self.getSearchParams(showName + " saison %d" % season, show.audio_lang, fullSeason=True))
            results.extend( self.getSearchParams(showName + " season %d" % season, show.audio_lang, fullSeason=True))
            results.extend( self.getSearchParams(showName + " saison%02d" % season, show.audio_lang, fullSeason=True))
            results.extend( self.getSearchParams(showName + " season%02d" % season, show.audio_lang, fullSeason=True))
            results.extend( self.getSearchParams(showName + " saison %02d" % season, show.audio_lang, fullSeason=True))
            results.extend( self.getSearchParams(showName + " season %02d" % season, show.audio_lang, fullSeason=True))
            results.extend( self.getSearchParams(showName + ".S%02d." % season, show.audio_lang, fullSeason=True))
        return results

    def _get_episode_search_strings(self, ep_obj, french=None):

        showNam = show_name_helpers.allPossibleShowNames(ep_obj.show)
        showNames = list(set(showNam))
        results = []
        for showName in showNames:
            results.extend( self.getSearchParams( "%s S%02dE%02d" % ( showName, ep_obj.scene_season, ep_obj.scene_episode), ep_obj.show.audio_lang, french ))
            results.extend( self.getSearchParams( "%s %dx%02d" % ( showName, ep_obj.scene_season, ep_obj.scene_episode ), ep_obj.show.audio_lang, french ))
        return results
    
    def _get_title_and_url(self, item):
        return (item.title, item.url)
    
    def getQuality(self, item):
        return item.getQuality()
    
    def _doLogin(self, login, password):

                                       
        data = urllib.urlencode({'uid': login, 'pwd' :  password, 'submit' : 'Envoyer'})
        
     
        r = self.opener.open(self.url + '/index.php?page=login',data)
        
        for index, cookie in enumerate(self.cj):
            if (cookie.name == "xbtitFM"): self.login_done = True
                                
        if not self.login_done and not self.failed_login_logged:
            logger.log(u"Unable to login to ADDICT. Please check username and password.", logger.WARNING) 
            self.failed_login_logged = True
        
        if self.login_done and not self.successful_login_logged:
            logger.log(u"Login to ADDICT successful", logger.MESSAGE) 
            self.successful_login_logged = True        

    def _doSearch(self, searchString, show=None, season=None, french=None):

        
        if not self.login_done:
            self._doLogin( sickbeard.ADDICT_USERNAME, sickbeard.ADDICT_PASSWORD )

        results = []
        
        searchUrl = self.url + '/index.php?page=torrents&active=1&options=0&' + searchString.replace('!','')
 
        logger.log(u"Search string: " + searchUrl, logger.DEBUG)
        
        r = self.opener.open( searchUrl )

        soupfull = BeautifulSoup( r)
        delbegin=str(soupfull.prettify).split('<table width="100%">')[1]
        restable=delbegin[delbegin.find('<table'):delbegin.find('table>')+6]
        soup=BeautifulSoup(restable)
        resultsTable = soup.find("table")

        if resultsTable:

            rows = resultsTable.findAll("tr")
            x=0
            for row in rows:
                x=x+1
                if (x > 1): 
                #bypass first row because title only
                    if 'Liste des torrents' in str(row) :
                        continue                           
                 
                    link = row.findAll('td')[1].find("a",  href=re.compile("torrent-details")) 
                    if link:               
                        title = link.text
                        logger.log(u"ADDICT TITLE TEMP: " + title, logger.DEBUG)                   
                        downloadURL =  self.url + "/" + row.find("a",href=re.compile("\.torrent"))['href']              
                
                        quality = Quality.nameQuality( title )
                        if quality==Quality.UNKNOWN and title:
                            if '720p' not in title.lower() and '1080p' not in title.lower():
                                quality=Quality.SDTV
                        if show and french==None:
                            results.append( ADDICTSearchResult( self.opener, title, downloadURL, quality, str(show.audio_lang) ) )
                        elif show and french:
                            results.append( ADDICTSearchResult( self.opener, title, downloadURL, quality, 'fr' ) )
                        else:
                            results.append( ADDICTSearchResult( self.opener, title, downloadURL, quality ) )
        
        return results
    
    def getResult(self, episodes):
        """
        Returns a result of the correct type for this provider
        """
        result = classes.TorrentDataSearchResult(episodes)
        result.provider = self

        return result    
    
class ADDICTSearchResult:
    
    def __init__(self, opener, title, url, quality, audio_langs=None):
        self.opener = opener
        self.title = title
        self.url = url
        self.quality = quality
        self.audio_langs=audio_langs    

    def getNZB(self):
        return self.opener.open( self.url , 'wb').read()             

    def getQuality(self):
        return self.quality

provider = ADDICTProvider()
