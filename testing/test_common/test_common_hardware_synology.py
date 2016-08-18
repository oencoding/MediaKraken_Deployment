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
sys.path.append('.')
from common import common_hardware_synology


class TestCommonSynology(object):


    @classmethod
    def setup_class(self):
        self.db_connection = com_Hardware_Synology.com_Synology_API()


    @classmethod
    def teardown_class(self):
        pass


# connect to synology    
# def com_Synology_Connect(self, addr, user_name, user_password):


    # get nas info
    def test_com_Synology_Info(self):
        """
        Test function
        """
        com_synology_info()


    # get share list
    def test_com_Synology_Shares_List(self):
        """
        Test function
        """
        com_synology_shares_list()
