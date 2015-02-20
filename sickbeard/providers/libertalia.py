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
import urllib2
import random
import re
class LIBERTALIAProvider(generic.TorrentProvider):

    def __init__(self):
        
        generic.TorrentProvider.__init__(self, "LIBERTALIA")

        self.supportsBacklog = True
        
        self.cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        
        self.url = "https://libertalia.me"
        
        self.login_done = False
        self.failed_login_logged = False
        self.successful_login_logged = False
        
    def isEnabled(self):
        return sickbeard.LIBERTALIA
    
    def getSearchParams(self, searchString, audio_lang, french=None, fullSeason=False):
        results = []
        if fullSeason:
            cat='9.2'
        else:
            cat='9'
        if audio_lang == "en" and french==None:
            results.append( urllib.urlencode( {
                'name': searchString                            
            } ) + "*VO*&cat%5B%5D="+cat+"&[PARAMSTR]=" + searchString +" VO" )
        elif audio_lang == "en" and french==None:
            results.append( urllib.urlencode( {
                'name': searchString                            
            } ) + "*VO*&cat%5B%5D="+cat+"&[PARAMSTR]=" + searchString +" VO" )
        elif audio_lang == "fr" or french:
            results.append( urllib.urlencode( {
                'name': searchString
            } ) + "*FRENCH*&cat%5B%5D="+cat+"&[PARAMSTR]=" + searchString +" FRENCH")
        else:
            results.append( urllib.urlencode( {
                'name': searchString
            } ) + "&cat%5B%5D=9&[PARAMSTR]=" + searchString )
        return results
        
    def _get_season_search_strings(self, show, season):

        showNam = show_name_helpers.allPossibleShowNames(show)
        showNames = list(set(showNam))
        results = []
        for showName in showNames:
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
                                       
        data = urllib.urlencode({'username': login, 'password' :  password, 'submit' : 'login'})
        
     
        r = self.opener.open(self.url + '/login.php',data)
        
        for index, cookie in enumerate(self.cj):
            if (cookie.name == "session"): self.login_done = True
                                
        if not self.login_done and not self.failed_login_logged:
            logger.log(u"Unable to login to LIBERTALIA. Please check username and password.", logger.WARNING) 
            self.failed_login_logged = True
        
        if self.login_done and not self.successful_login_logged:
            logger.log(u"Login to LIBERTALIA successful", logger.MESSAGE) 
            self.successful_login_logged = True        

    def _doSearch(self, searchString, show=None, season=None, french=None):

        
        if not self.login_done:
            self._doLogin( sickbeard.LIBERTALIA_USERNAME, sickbeard.LIBERTALIA_PASSWORD )

        results = []
        
        searchUrl = self.url + '/torrents.php?' + searchString.replace('!','')
 
        logger.log(u"Search string: " + searchUrl, logger.DEBUG)
        
        r = self.opener.open( searchUrl )
        soup = BeautifulSoup( r)

        resultsTable = soup.find("table", { "class" : "torrent_table"  })
        if resultsTable:
            logger.log(u"LIBERTALIA found resulttable ! " , logger.DEBUG)  
            rows = resultsTable.findAll("tr" ,  {"class" : "torrent_row  new  "}  )  # torrent_row new
            
            for row in rows:
                           
                #bypass first row because title only  
                columns = row.find('td', {"class" : "torrent_name"} )                            
                logger.log(u"LIBERTALIA found rows ! " , logger.DEBUG) 
                isvfclass = row.find('td', {"class" : "sprite-vf"} )
                isvostfrclass = row.find('td', {"class" : "sprite-vostfr"} ) 
                link = columns.find("a",  href=re.compile("torrents"))  
                if link: 
                  if isvostfrclass and str(show.audio_lang)=='fr':
                    logger.log(u"LIBERTALIA found VOSTFR et demande *"+str(show.audio_lang)+"* je skip ! " + link.text , logger.DEBUG)
                    link = columns.find("a",  href=re.compile("nepastrouver"))                     
                if link:     
                  if isvfclass  and  str(show.audio_lang)!='fr'  :                     
                    logger.log(u"LIBERTALIA found VF et demande *"+str(show.audio_lang)+"* je skip ! " + link.text , logger.DEBUG)
                    link = columns.find("a",  href=re.compile("nepastrouver"))     
                if link:               
                    title = link.text
                    recherched=searchUrl.split("&[PARAMSTR]=")[1]
                    recherched=recherched.replace(".","(.*)").replace(" ","(.*)").replace("'","(.*)")
                    logger.log(u"LIBERTALIA TITLE : " + title, logger.DEBUG)  
                    logger.log(u"LIBERTALIA CHECK MATCH : " + recherched, logger.DEBUG)                                        
                    #downloadURL =  self.url + "/" + row.find("a",href=re.compile("torrent_pass"))['href']
                    if re.match(recherched,title , re.IGNORECASE):              
                        downloadURL =  row.find("a",href=re.compile("torrent_pass"))['href']                
                        quality = Quality.nameQuality( title )
                        if quality==Quality.UNKNOWN and title:
                            if '720p' not in title.lower() and '1080p' not in title.lower():
                                quality=Quality.SDTV
                        if show and french==None:
                            results.append( LIBERTALIASearchResult( self.opener, title, downloadURL, quality, str(show.audio_lang) ) )
                        elif show and french:
                            results.append( LIBERTALIASearchResult( self.opener, title, downloadURL, quality, 'fr' ) )
                        else:
                            results.append( LIBERTALIASearchResult( self.opener, title, downloadURL, quality ) )
        else:
            logger.log(u"Pas de table trouvée ! je délogue", logger.DEBUG)
            self.login_done = False             
        return results
    
    def getResult(self, episodes):
        """
        Returns a result of the correct type for this provider
        """
        result = classes.TorrentDataSearchResult(episodes)
        result.provider = self

        return result    
    
class LIBERTALIASearchResult:
    
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

provider = LIBERTALIAProvider()
