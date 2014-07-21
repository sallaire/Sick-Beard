# Author: Olivier N. <raver2046@gmail.com>
# URL: https://github.com/sarakha63/Sick-Beard
#
# This file is based upon tvtorrents.py.
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
from xml.dom.minidom import parseString

import sickbeard
import generic

from sickbeard import helpers, logger, exceptions, tvcache
from lib.tvdb_api import tvdb_api, tvdb_exceptions
from sickbeard.name_parser.parser import NameParser, InvalidNameException


class thinkgeekProvider(generic.TorrentProvider):

    def __init__(self):
        generic.TorrentProvider.__init__(self, "thinkgeek")

        self.supportsBacklog = False
        self.cache = thinkgeekCache(self)
        self.url = 'http://think-geek.net/'

    def isEnabled(self):
        return sickbeard.thinkgeek

    def imageName(self):
        return 'thinkgeek.png'


class thinkgeekCache(tvcache.TVCache):

    def __init__(self, provider):
        tvcache.TVCache.__init__(self, provider)

        # only poll every 15 minutes
        self.minTime = 15

        
    def _getRSSData(self):
    
         if not sickbeard.thinkgeek_KEY:
            raise exceptions.AuthException("thinkgeek requires an API key to work correctly")

         url = 'https://think-geek.net/?p=rss&categories=33,34,61,62&pk=' + sickbeard.thinkgeek_KEY
 
         logger.log(self.provider.name + " cache update URL: " + url, logger.DEBUG)
 
         data = self.provider.getURL(url)
 
         parsedXML = parseString(data)
         channel = parsedXML.getElementsByTagName('channel')[0]
         description = channel.getElementsByTagName('description')[0]
 
         description_text = helpers.get_xml_text(description)
 
         if "Invalid Hash" in description_text:
             logger.log(u"Torrent invalid hash, check your config", logger.ERROR)
 
         return data
 
    def _parseItem(self, item):

        (title, url) = self.provider._get_title_and_url(item)

        if not title or not url:
            logger.log(u"The XML returned from the EZRSS RSS feed is incomplete, this result is unusable", logger.ERROR)
            return

        logger.log(u"Adding item from RSS to cache: "+title, logger.DEBUG)

        self._addCacheEntry(title, url)

provider = thinkgeekProvider()
