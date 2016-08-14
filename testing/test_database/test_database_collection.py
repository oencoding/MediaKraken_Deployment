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


class TestDatabaseCollection(object):


    @classmethod
    def setup_class(self):
        self.db = database_base.MKServerDatabase()
        self.db.srv_db_open('127.0.0.1', 5432, 'metamandb', 'metamanpg', 'metamanpg')


    @classmethod
    def teardown_class(self):
        self.db.srv_db_close()


    # find all known media
    @pytest.mark.parametrize(("offset", "records"), [
        (None, None),
        (100, 100),
        (100000000, 1000)])
    def Test_srv_db_collection_list(self, offset, records):
        self.db.srv_db_collection_list(offset, records)
        self.db.srv_db_rollback()


    # read collection data from json metadata
    def Test_srv_db_media_collection_scan(self):
        self.db.srv_db_media_collection_scan()
        self.db.srv_db_rollback()


    # find guid of collection name
    @pytest.mark.parametrize(("collection_name"), [
        ('Darko Collection'),
        ('fakecollectionstuff')])
    def Test_srv_db_collection_guid_by_name(self, collection_name):
        self.db.srv_db_collection_guid_by_name(collection_name)
        self.db.srv_db_rollback()


    # find guid of collection name
    # def srv_db_collection_by_tmdb(self, tmdb_id):
#        self.db.srv_db_rollback()


    # insert collection
    # def srv_db_collection_insert(self, collection_name, guid_json, metadata_json, localimage_json):
#        self.db.srv_db_rollback()


    # update collection ids
    # def srv_db_collection_update(self, collection_guid, guid_json):
#        self.db.srv_db_rollback()


    # pull in colleciton info
    # def srv_db_collection_read_by_guid(self, media_uuid):
#        self.db.srv_db_rollback()
