# Author: Nic Wolfe <nic@wolfeden.ca>
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


import sickbeard

from sickbeard import logger


class ShowRefresher():


    def run(self):
        logger.log(u"Refreshing snatched episodes", logger.MESSAGE);
        for curShow in sickbeard.showList:
            if curShow.hasSnatchedEpisodes():
                logger.log(u"Refreshing episodes status for show "+curShow.name+" because at least one episode is marked as SNATCHED", logger.MESSAGE);
                sickbeard.showQueueScheduler.action.refreshShow(curShow, False) #@UndefinedVariable
        logger.log(u"Snatched episodes refreshed", logger.MESSAGE);
