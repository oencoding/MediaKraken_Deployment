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


class TestDatabaseTuner(object):


    @classmethod
    def setup_class(self):
        self.db_connection = database_base.MKServerDatabase()
        self.db_connection.srv_db_open('127.0.0.1', 5432, 'metamandb', 'metamanpg', 'metamanpg')


    @classmethod
    def teardown_class(self):
        self.db_connection.srv_db_close()


    # count tuners
    def test_srv_db_tuner_count(self):
        self.db_connection.srv_db_tuner_count()
        self.db_connection.srv_db_rollback()


    # read tuners
    @pytest.mark.parametrize(("offset", "records"), [
        (None, None),
        (100, 100),
        (100000000, 1000)])
    def test_srv_db_tuner_list(self, offset, records):
        self.db_connection.srv_db_tuner_list(offset, records)
        self.db_connection.srv_db_rollback()


    # insert record
    # def srv_db_tuner_insert(self, tuner_json):
#        self.db_connection.srv_db_rollback()


    # update record
    # def srv_db_tuner_update(self, guid, tuner_json):
#        self.db_connection.srv_db_rollback()


    # delete record
    # def srv_db_tuner_delete(self, guid):
#        self.db_connection.srv_db_rollback()


    # find detials by hardware id (serial)
    # def srv_db_tuner_by_serial(self, serial_no):
#         self.db_connection.srv_db_rollback()
