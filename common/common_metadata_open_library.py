'''
  Copyright (C) 2016 Quinn D Granfor <spootdev@gmail.com>

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
from . import common_network


class CommonMetadataOpenLibrary(object):
    """
    Class for interfacing with OpenLibrary
    """
    def __init__(self, option_config_json):
        pass


    def com_meta_openlibrary_fetch_cover(self, isbn_id):
        common_network.mk_network_fetch_from_url('http://covers.openlibrary.org/b/isbn/'
                                                 + isbn_id + '-L.jpg', image_path)
