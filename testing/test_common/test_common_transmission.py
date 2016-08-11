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
import pytest
import sys
sys.path.append("../common")
from common_transmission import *


class Test_common_transmission_API:


    @classmethod
    def setup_class(self):
        self.db = common_transmission.common_transmission_API()


    @classmethod
    def teardown_class(self):
        pass


    def test_common_transmission_Get_Torrent_List(self):
        common_transmission_Get_Torrent_List()


#    def common_transmission_Add_Torrent(self, torrent_path):


#    def common_transmission_Remove_Torrent(self, torrent_hash):


#    def MK_Common_Trnasmission_Name(self, torrent_no):


#    def common_transmission_Torrent_Detail(self, torrent_no):


#    def common_transmission_Torrent_Start(self, torrent_no):


#    def common_transmission_Torrent_Stop(self, torrent_no):
