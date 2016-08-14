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
sys.path.append("./common")
sys.path.append("./server") # for db import
import database as database_base


class TestDatabaseUsers(object):


    @classmethod
    def setup_class(self):
        self.db_connection = database_base.MKServerDatabase()
        self.db_connection.srv_db_open('127.0.0.1', 5432, 'metamandb', 'metamanpg', 'metamanpg')


    @classmethod
    def teardown_class(self):
        self.db_connection.srv_db_close()


    def test_srv_db_user_list_name_count(self):
        """
        # return user count
        """
        self.db_connection.srv_db_user_list_name_count()
        self.db_connection.srv_db_rollback()


    @pytest.mark.parametrize(("offset", "records"), [
        (None, None),
        (100, 100),
        (100000000, 1000)])
    def test_srv_db_user_list_name(self, offset, records):
        """
        # return user list
        """
        self.db_connection.srv_db_user_list_name(offset, records)
        self.db_connection.srv_db_rollback()


    # return all data for specified user
    # def srv_db_user_detail(self, guid):
#        self.db_connection.srv_db_rollback()


    # remove user
    # def srv_db_user_delete(self, user_guid):
        #self.db_connection.srv_db_rollback()


    # verify user logon
    # def srv_db_user_login_kodi(self, user_data):
#        self.db_connection.srv_db_rollback()
