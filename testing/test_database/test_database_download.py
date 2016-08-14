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


class TestDatabaseDownload(object):


    @classmethod
    def setup_class(self):
        self.db = database_base.MKServerDatabase()
        self.db.srv_db_open('127.0.0.1', 5432, 'metamandb', 'metamanpg', 'metamanpg')


    @classmethod
    def teardown_class(self):
        self.db.srv_db_close()


    # create/insert a download
    # def srv_db_Download_Insert(self, provider, down_json):
#        self.db.srv_db_rollback()


#    ## read the download
# this no longer exists
#    def Test_srv_db_Download_Read(self):
#        self.db.srv_db_Download_Read()
#        self.db.srv_db_rollback()


    # read the downloads by provider
    @pytest.mark.parametrize(("provider_name"), [
        ('themoviedb'),
        ('fakeprovider')])
    def Test_srv_db_Download_Read_by_Provider(self, provider_name):
        self.db.srv_db_Download_Read_by_Provider(provider_name)
        self.db.srv_db_rollback()


    # remove download
    # def srv_db_Download_Delete(self, guid):
#        self.db.srv_db_rollback()


    # update provdier
    # def srv_db_download_update_Provider(self, provider_name, guid):
#        self.db.srv_db_rollback()


    # def srv_db_download_update(self, update_json, guid):
#        self.db.srv_db_rollback()
