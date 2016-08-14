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


class TestDatabaseAudit(object):


    @classmethod
    def setup_class(self):
        self.db_connection.connection = database_base.MKServerDatabase()
        self.db_connection.srv_db_open('127.0.0.1', 5432, 'metamandb', 'metamanpg', 'metamanpg')


    @classmethod
    def teardown_class(self):
        self.db_connection.srv_db_close()


    ## read scan status
    def test_srv_db_audit_path_status(self):
        self.db_connection.srv_db_audit_path_status()
        self.db_connection.srv_db_rollback()


    ## update status
    #def srv_db_Audit_Path_Update_Status(self, lib_guid, status_json):
#        self.db_connection.srv_db_rollback()


    ## read the paths to audit
    def test_srv_db_audit_paths_count(self):
        self.db_connection.srv_db_audit_paths_count()
        self.db_connection.srv_db_rollback()


    ## update audit path
    #def srv_db_Audit_Path_Update_by_UUID(self, lib_path, class_guid, lib_guid):
#        self.db_connection.srv_db_rollback()


    ## remove media path
    #def srv_db_Audit_Path_Delete(self, lib_guid):
#        self.db_connection.srv_db_rollback()


    ## add media path
    #def srv_db_Audit_Path_Add(self, dir_path, class_guid):
#        self.db_connection.srv_db_rollback()


    ## lib path check (dupes)
    @pytest.mark.parametrize(("dir_path"), [
        ('/home/spoot'),
        ('/home/spoot/fakedirzz')])
    def test_srv_db_audit_path_check(self, dir_path):
        self.db_connection.srv_db_audit_path_check(dir_path)
        self.db_connection.srv_db_rollback()


    ## update the timestamp for directory scans
    #def srv_db_Audit_Directory_Timestamp_Update(self, file_path):
#        self.db_connection.srv_db_rollback()


    ## read the paths to audit
    @pytest.mark.parametrize(("offset", "records"), [
        (None, None),
        (100, 100),
        (100000000, 1000)])
    def test_srv_db_audit_paths(self, offset, records):
        self.db_connection.srv_db_audit_paths(offset, records)
        self.db_connection.srv_db_rollback()


    ## lib data per id
    #def srv_db_Audit_Path_by_UUID(self, dir_id):
#        self.db_connection.srv_db_rollback()
