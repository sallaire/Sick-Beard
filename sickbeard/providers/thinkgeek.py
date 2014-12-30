# -*- coding: latin-1 -*-
# Author: Raver2046 
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
import random
import urllib2
import re

class THINKGEEKProvider(generic.TorrentProvider):

    def __init__(self):
        
        generic.TorrentProvider.__init__(self, "THINKGEEK")

        self.supportsBacklog = True
        
        self.cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        
        self.url = "https://think-geek.net"
        
        self.login_done = False
        self.failed_login_logged = False
        self.successful_login_logged = False
        
    def isEnabled(self):
        return sickbeard.THINKGEEK
    
    def getSearchParams(self, searchString, audio_lang, french=None, fullSeason=False):
        results = []    
        if audio_lang == "en" and french==None:
            results.append( urllib.urlencode( {
                'keywords': searchString  ,                                                         
            } ) + "&cid=34,62&[PARAMSTR]=" + searchString )
        elif audio_lang == "fr" or french:
            results.append( urllib.urlencode( {
                'keywords': searchString
            } ) + "&cid=33,61&[PARAMSTR]=" + searchString)
        else:
            results.append( urllib.urlencode( {
                'keywords': searchString
            } ) + "&cid=34,62,33,61&[PARAMSTR]=" + searchString)
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
        return results
    
    def _get_title_and_url(self, item):
        return (item.title, item.url)
    
    def getQuality(self, item):
        return item.getQuality()
    
    def _doLogin(self, login, password):

        listeUserAgents = [ 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_5; fr-fr) AppleWebKit/525.18 (KHTML, like Gecko) Version/3.1.2 Safari/525.20.1',
                                                'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.186 Safari/535.1',
                                                'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.2.149.27 Safari/525.13',
                                                'Mozilla/5.0 (X11; U; Linux x86_64; en-us) AppleWebKit/528.5+ (KHTML, like Gecko, Safari/528.5+) midori',
                                                'Mozilla/5.0 (Windows NT 6.0) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.107 Safari/535.1',
                                                'Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en-us) AppleWebKit/312.1 (KHTML, like Gecko) Safari/312',
                                                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11',
                                                'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.8 (KHTML, like Gecko) Chrome/17.0.940.0 Safari/535.8' ]

        self.opener.addheaders = [('User-agent', random.choice(listeUserAgents))] 
                                              
        data = urllib.urlencode({'action':'login','loginbox_membername': login, 'loginbox_password' : password, 'loginbox_remember' : 'true'})
     
        r = self.opener.open(self.url + '/ajax/login.php',data)
        
        for index, cookie in enumerate(self.cj):
            if (cookie.name == "tsue_member"): self.login_done = True
                                
        if not self.login_done and not self.failed_login_logged:
            logger.log(u"Unable to login to THINKGEEK. Please check username and password.", logger.WARNING) 
            self.failed_login_logged = True
        
        if self.login_done and not self.successful_login_logged:
            logger.log(u"Login to THINKGEEK successful", logger.MESSAGE) 
            self.successful_login_logged = True        

    def _doSearch(self, searchString, show=None, season=None, french=None):

        
        if not self.login_done:
            self._doLogin( sickbeard.THINKGEEK_USERNAME, sickbeard.THINKGEEK_PASSWORD )

        results = []
        
        searchUrl = self.url + '?p=torrents&pid=10&search_type=name&' + searchString.replace('!','')
 
        logger.log(u"Search string: " + searchUrl, logger.DEBUG)
        
        r = self.opener.open( searchUrl )

        soup = BeautifulSoup( r)

        resultsTable = soup.find("div", { "id" : "content"  })
        if resultsTable:

            rows = resultsTable.findAll("div" , {"class" : "torrent-box"} )
           
            for row in rows:
            
                link = row.find("a",href=re.compile("action=details"))                                                       
                                  
                if link:               
                    title = link.text
                    recherched=searchUrl.split("&[PARAMSTR]=")[1]
                    recherched=recherched.replace(".","(.*)").replace(" ","(.*)").replace("'","(.*)")
                    logger.log(u"THINKGEEK TITLE : " + title, logger.DEBUG)  
                    logger.log(u"THINKGEEK CHECK MATCH : " + recherched, logger.DEBUG) 
                    if re.match(recherched,title , re.IGNORECASE):                 
                        downloadURL =  row.find("a",href=re.compile("action=download"))['href']
                    else:
                        continue            
                    logger.log(u"THINKGEEK DOWNLOAD URL : " + title, logger.DEBUG) 
                    quality = Quality.nameQuality( title )
                    if quality==Quality.UNKNOWN and title:
                        if '720p' not in title.lower() and '1080p' not in title.lower():
                            quality=Quality.SDTV
                    if show and french==None:
                        results.append( THINKGEEKSearchResult( self.opener, title, downloadURL, quality, str(show.audio_lang) ) )
                    elif show and french:
                        results.append( THINKGEEKSearchResult( self.opener, title, downloadURL, quality, 'fr' ) )
                    else:
                        results.append( THINKGEEKSearchResult( self.opener, title, downloadURL, quality ) )        
        return results
    
    def getResult(self, episodes):
        """
        Returns a result of the correct type for this provider
        """
        result = classes.TorrentDataSearchResult(episodes)
        result.provider = self

        return result    
    
class THINKGEEKSearchResult:
    
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

provider = THINKGEEKProvider()
