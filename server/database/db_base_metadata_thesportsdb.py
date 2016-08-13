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
#import logging
import uuid


def srv_db_metathesportsdb_Select_By_Guid(self, guid):
    """
    # select
    """
    self.sql3_cursor.execute('select mm_metadata_sports_json from mm_metadata_sports'\
        ' where mm_metadata_sports_guid = %s', (guid,))
    try:
        return self.sql3_cursor.fetchone()['mm_metadata_sports_json']
    except:
        return None


def srv_db_metathesportsdb_Insert(self, series_id_json, event_name, show_detail,\
        image_json):
    """
    # insert
    """
    self.sql3_cursor.execute('insert into mm_metadata_sports (mm_metadata_sports_guid,'\
        ' mm_metadata_media_sports_id, mm_metadata_sports_name, mm_metadata_sports_json,'\
        ' mm_metadata_sports_image_json) values (%s,%s,%s,%s,%s)',\
        (str(uuid.uuid4()), series_id_json, event_name, show_detail, image_json))


def srv_db_metathesports_update(self, series_id_json, event_name, show_detail,
        sportsdb_id):
    """
    # updated
    """
    self.sql3_cursor.execute('update mm_metadata_sports set mm_metadata_media_sports_id = %s,'\
        ' mm_metadata_sports_name = %s, mm_metadata_sports_json = %s'\
        ' where mm_metadata_media_sports_id->\'thesportsdb\' ? %s',\
        (series_id_json, event_name, show_detail, sportsdb_id))
