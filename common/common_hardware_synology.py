'''
  Copyright (C) 2015 Quinn D Granfor <spootdev@gmail.com>

  This program is free software; you can redistribute it and/or
  modify it under the terms of the GNU General Public License
  version 2, as published by the Free Software Foundation.

  This program is distributed in the hope that it will be useful, but
  WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
  General Public License version 2 for more details.

  You should have received a copy of the GNU General Public License
  version 2 along with this program; if not, write to the Free
  Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
  MA 02110-1301, USA.
'''

from __future__ import absolute_import, division, print_function, unicode_literals
import logging # pylint: disable=W0611
from synolopy import NasApi


class CommonSynology(object):
    """
    Class for interfacing with synology nas
    """
    def __init__(self):
        self.synology_nas = None


    def com_synology_connect(self, addr, user_name, user_password):
        """
        Connect to synology
        """
        logging.info("syn connect: %s", addr)
        self.synology_nas = NasApi('http://%s:5000/webapi/' % addr, user_name, user_password)


    def com_synology_info(self):
        """
        Get nas info
        """
        return self.synology_nas.downloadstation.info.request('getinfo')


    def com_synology_shares_list(self):
        """
        Get share list
        """
        return self.synology_nas.filestation.file_share.request('list_share',
                                                                additional='real_path')
