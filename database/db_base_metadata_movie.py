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
import json


def db_meta_movie_image_random(self, return_image_type='Poster'): # poster, backdrop, etc
    """
    Find random movie image
    """
    self.db_cursor.execute('select mm_metadata_localimage_json->\'Images\'->\'themoviedb\'->>\''
        + return_image_type + '\' as image_json,mm_metadata_guid from mm_media,mm_metadata_movie'\
        ' where mm_media_metadata_guid = mm_metadata_guid'\
        ' and (mm_metadata_localimage_json->\'Images\'->\'themoviedb\'->>\''
        + return_image_type + '\'' + ')::text != \'null\' order by random() limit 1')
    try:
        # then if no results.....a None will except which will then pass None, None
        image_json, metadata_id = self.db_cursor.fetchone()
        return image_json, metadata_id
    except:
        return None, None


def db_meta_movie_update_castcrew(self, cast_crew_json, metadata_id):
    """
    Update the cast/crew for selected media
    """
    logging.info('upt castcrew: %s', metadata_id)
    self.db_cursor.execute('select mm_metadata_json from mm_metadata_movie'
        ' where mm_metadata_guid = %s', (metadata_id,))
    cast_crew_json_row = self.db_cursor.fetchone()[0]
    logging.info('castrow: %s', cast_crew_json_row)
    if 'cast' in cast_crew_json:
        cast_crew_json_row['Meta']['themoviedb'].update({'Cast': cast_crew_json['cast']})
    if 'crew' in cast_crew_json:
        cast_crew_json_row['Meta']['themoviedb'].update({'Crew': cast_crew_json['crew']})
    logging.info('upt: %s', cast_crew_json_row)
    self.db_cursor.execute('update mm_metadata_movie set mm_metadata_json = %s'
        ' where mm_metadata_guid = %s', (json.dumps(cast_crew_json_row), metadata_id))
    self.db_commit()


def db_meta_movie_status_update(self, metadata_guid, user_id, status_text):
    """
    # set status's for metadata
    """
    self.db_cursor.execute('SELECT mm_metadata_user_json from mm_metadata_movie'
                           ' where mm_metadata_guid = %s FOR UPDATE', (metadata_guid,))
    if status_text == 'watched' or status_text == 'requested':
        status_setting = True
    else:
        status_setting = status_text
        status_text = 'Rating'
    try:
        json_data = self.db_cursor.fetchone()['mm_metadata_user_json']
        if json_data is None or 'UserStats' not in json_data:
            json_data = {}
            json_data['UserStats'] = {}
        if user_id in json_data['UserStats']:
            json_data['UserStats'][user_id][status_text] = status_setting
        else:
            json_data['UserStats'][user_id] = {status_text: status_setting}
        self.db_meta_movie_json_update(metadata_guid, json.dumps(json_data))
        #self.db_commit() - since done in update below
    except:
        self.db_rollback()
        return None


def db_meta_movie_json_update(self, media_guid, metadatajson):
    """
    # update the metadata json
    """
    self.db_cursor.execute('update mm_metadata_movie set mm_metadata_user_json = %s'
                           ' where mm_metadata_guid = %s', (metadatajson, media_guid))
    self.db_commit()
