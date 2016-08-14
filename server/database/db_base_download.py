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
import logging
import uuid


def srv_db_download_insert(self, provider, down_json):
    """
    Create/insert a download into the que
    """
    self.sql3_cursor.execute('insert into mm_download_que (mdq_id,mdq_provider,mdq_download_json)'\
        ' values (%s,%s,%s)', (str(uuid.uuid4()), provider, down_json))
    self.srv_db_commit()


## read the download
#def srv_db_Download_Read(self):
#    self.sql3_cursor.execute('select mdq_id,mdq_provider,mdq_download_json from mm_download_que')
#    return self.sql3_cursor.fetchall()


def srv_db_download_read_by_provider(self, provider_name):
    """
    Read the downloads by provider
    """
    self.sql3_cursor.execute('select mdq_id,mdq_download_json from mm_download_que'\
        ' where mdq_provider = %s', (provider_name,))
    return self.sql3_cursor.fetchall()


def srv_db_download_delete(self, guid):
    """
    Remove download
    """
    self.sql3_cursor.execute('delete from mm_download_que where mdq_id = %s', (guid,))
    self.srv_db_commit()


def srv_db_download_update_provider(self, provider_name, guid):
    """
    Update provider
    """
    logging.debug('download update provider: %s %s', provider_name, guid)
    self.sql3_cursor.execute('update mm_download_que set mdq_provider = %s where mdq_id = %s',\
        (provider_name, guid))
    self.srv_db_commit()


def srv_db_download_update(self, update_json, guid):
    """
    Update download que record
    """
    logging.debug('download update: %s %s', update_json, guid)
    self.sql3_cursor.execute('update mm_download_que set mdq_download_json = %s where mdq_id = %s',\
        (update_json, guid))
    self.srv_db_commit()
