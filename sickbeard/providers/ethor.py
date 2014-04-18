# Author: Julien Goret <jgoret@gmail.com>
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

import sickbeard
import generic

from sickbeard import helpers, logger, exceptions, tvcache
from lib.tvdb_api import tvdb_api, tvdb_exceptions
from sickbeard.name_parser.parser import NameParser, InvalidNameException


class EthorProvider(generic.TorrentProvider):

    def __init__(self):
        generic.TorrentProvider.__init__(self, "Ethor")

        self.supportsBacklog = False
        self.cache = EthorCache(self)
        self.url = 'http://ethor.net/'

    def isEnabled(self):
        return sickbeard.ETHOR

    def imageName(self):
        return 'ethor.png'


class EthorCache(tvcache.TVCache):

    def __init__(self, provider):
        tvcache.TVCache.__init__(self, provider)

        # only poll every 15 minutes
        self.minTime = 15

    def _getRSSData(self):

        if not sickbeard.ETHOR_KEY:
            raise exceptions.AuthException("Ethor requires an API key to work correctly")

        url = 'http://ethor.net/rss.php?feed=dl&cat=45,43,7&rsskey=' + sickbeard.ETHOR_KEY
        logger.log(u"Ethor cache update URL: " + url, logger.DEBUG)

        data = self.provider.getURL(url)

        return data

    def _parseItem(self, item):
        ltvdb_api_parms = sickbeard.TVDB_API_PARMS.copy()
        ltvdb_api_parms['search_all_languages'] = True

        (title, url) = self.provider._get_title_and_url(item)

        if not title or not url:
            logger.log(u"The XML returned from the Ethor RSS feed is incomplete, this result is unusable", logger.ERROR)
            return
            
        try:
            myParser = NameParser()
            parse_result = myParser.parse(title)
        except InvalidNameException:
            logger.log(u"Unable to parse the filename "+title+" into a valid episode", logger.DEBUG)
            return

        try:
            t = tvdb_api.Tvdb(**ltvdb_api_parms)
            showObj = t[parse_result.series_name]
        except tvdb_exceptions.tvdb_error:
            logger.log(u"TVDB timed out, unable to update episodes from TVDB", logger.ERROR)
            return

        logger.log(u"Adding item from RSS to cache: " + title, logger.DEBUG)

        self._addCacheEntry(name=title, url=url, tvdb_id=showObj['id'])

provider = EthorProvider()
