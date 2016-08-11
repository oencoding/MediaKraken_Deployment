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
import ConfigParser
Config = ConfigParser.ConfigParser()
Config.read("MediaKraken.ini")
import os
import uuid
import signal
import json
import sys
sys.path.append("../MediaKraken_Server")
sys.path.append("../MediaKraken_Common")
import common_file
import common_logging
import MK_Common_Metadata
import common_network
import database as database_base
import locale
locale.setlocale(locale.LC_ALL, '')


# create the file for pid
pid_file = '../pid/' + str(os.getpid())
common_file.common_file_Save_Data(pid_file, 'TVDB_Images_Known', False, False, None)


def signal_receive(signum, frame):
    print('CHILD theTVDB Images: Received USR1')
    # remove pid
    os.remove(pid_file)
    # cleanup db
    db.MK_Server_Database_Rollback()
    db.MK_Server_Database_Close()
    sys.stdout.flush()
    sys.exit(0)


# start logging
common_logging.common_logging_Start('./log/MediaKraken_Subprogram_theTVDB_Images')


# open the database
db = database_base.MK_Server_Database()
db.MK_Server_Database_Open(Config.get('DB Connections', 'PostDBHost').strip(), Config.get('DB Connections', 'PostDBPort').strip(), Config.get('DB Connections', 'PostDBName').strip(), Config.get('DB Connections', 'PostDBUser').strip(), Config.get('DB Connections', 'PostDBPass').strip())


# log start
db.MK_Server_Database_Activity_Insert('MediaKraken_Server theTVDB Images Start', None,\
    'System: Server TVMaze Images Start', 'ServerTVDBImagesStart', None, None, 'System')


if str.upper(sys.platform[0:3]) == 'WIN' or str.upper(sys.platform[0:3]) == 'CYG':
    signal.signal(signal.SIGBREAK, signal_receive)   # ctrl-c
else:
    signal.signal(signal.SIGTSTP, signal_receive)   # ctrl-z
    signal.signal(signal.SIGUSR1, signal_receive)   # ctrl-c


# prep totals
total_cast_images = 0
total_episode_images = 0


# grab ones without image data
for row_data in db.MK_Server_Database_Metadata_TVShow_Images_To_Update('theTVDB'):
    logging.debug("json: %s", row_data['mm_metadata_tvshow_json']['Meta']['Series'])
    # this is "removed" via the query ['Meta']['theTVDB']

    # grab poster
    poster_image_local = None
    if 'poster' in row_data['mm_metadata_tvshow_json']['Meta']['Series'] and row_data['mm_metadata_tvshow_json']['Meta']['Series']['poster'] is not None:
        poster_image_local = os.path.join(MK_Common_Metadata.MK_Common_Metadata_Image_File_Path(row_data['mm_metadata_tvshow_json']['Meta']['Series']['SeriesName'], 'poster'), (str(uuid.uuid4()) + '.' + row_data['mm_metadata_tvshow_json']['Meta']['Series']['poster'].rsplit('.', 1)[1]))
        common_network.MK_Network_Fetch_From_URL("https://thetvdb.com/banners/" + row_data['mm_metadata_tvshow_json']['Meta']['Series']['poster'], poster_image_local)

    # grab banner
    banner_image_local = None
    if 'banner' in row_data['mm_metadata_tvshow_json']['Meta']['Series'] and row_data['mm_metadata_tvshow_json']['Meta']['Series']['banner'] is not None:
        banner_image_local = os.path.join(MK_Common_Metadata.MK_Common_Metadata_Image_File_Path(row_data['mm_metadata_tvshow_json']['Meta']['Series']['SeriesName'], 'banner'), (str(uuid.uuid4()) + '.' + row_data['mm_metadata_tvshow_json']['Meta']['Series']['banner'].rsplit('.', 1)[1]))
        common_network.MK_Network_Fetch_From_URL("https://thetvdb.com/banners/" + row_data['mm_metadata_tvshow_json']['Meta']['Series']['banner'], banner_image_local)

    # grab fanart
    fanart_image_local = None
    if 'fanart' in row_data['mm_metadata_tvshow_json']['Meta']['Series'] and row_data['mm_metadata_tvshow_json']['Meta']['Series']['fanart'] is not None:
        fanart_image_local = os.path.join(MK_Common_Metadata.MK_Common_Metadata_Image_File_Path(row_data['mm_metadata_tvshow_json']['Meta']['Series']['SeriesName'], 'fanart'), (str(uuid.uuid4()) + '.' + row_data['mm_metadata_tvshow_json']['Meta']['Series']['fanart'].rsplit('.', 1)[1]))
        common_network.MK_Network_Fetch_From_URL("https://thetvdb.com/banners/" + row_data['mm_metadata_tvshow_json']['Meta']['Series']['fanart'], fanart_image_local)

    # generate image json
    json_image_data = {'Images': {'theTVDB': {'Banner': banner_image_local, 'Fanart': fanart_image_local, 'Poster': poster_image_local, 'Cast': {}, 'Characters': {}, 'Episodes': {}, "Redo": False}}}
    logging.debug("image: %s", json_image_data)

    # process person and character data
    if 'Cast' in row_data['mm_metadata_tvshow_json'] and row_data['mm_metadata_tvshow_json']['Cast'] is not None:
        logging.debug("huh?: %s", row_data['mm_metadata_tvshow_json']['Cast'])
        if 'Actor' in row_data['mm_metadata_tvshow_json']['Cast']:
            for cast_member in row_data['mm_metadata_tvshow_json']['Cast']['Actor']:
                logging.debug("wha: %s", cast_member)
                if cast_member['Image'] is not None:
                    # determine path and fetch image/save
                    cast_image_local = os.path.join(MK_Common_Metadata.MK_Common_Metadata_Image_File_Path(cast_member['Name'],\
                        'person'), (str(uuid.uuid4()) + '.' + cast_member['Image'].rsplit('.', 1)[1]))
                    logging.debug("one: %s", cast_image_local)
                    common_network.MK_Network_Fetch_From_URL("https://thetvdb.com/banners/" + cast_member['Image'], cast_image_local)
                    json_image_data['Images']['theTVDB']['Cast'][cast_member['id']] = cast_image_local
                    total_cast_images += 1
            logging.debug("cast: %s", json_image_data)

    # process episode data
    if 'Episode' in row_data['mm_metadata_tvshow_json']['Meta']:
        for episode_info in row_data['mm_metadata_tvshow_json']['Meta']['Episode']:
            logging.debug("episode: %s", episode_info)
            if episode_info['filename'] is not None:
                eps_image_local = os.path.join(MK_Common_Metadata.MK_Common_Metadata_Image_File_Path(episode_info['EpisodeName'],\
                'backdrop'), (str(uuid.uuid4()) + '.' + episode_info['filename'].rsplit('.', 1)[1]))
                logging.debug("eps: %s", eps_image_local)
                common_network.MK_Network_Fetch_From_URL("https://thetvdb.com/banners/"\
                    + episode_info['filename'], eps_image_local)
                json_image_data['Images']['theTVDB']['Episodes'][episode_info['id']] = eps_image_local
                total_episode_images += 1
    db.MK_Server_Database_Metadata_TVShow_Update_Image(json.dumps(json_image_data), row_data[1])
    # commit
    db.MK_Server_Database_Commit()


# send notifications
if total_cast_images > 0:
    db.MK_Server_Database_Notification_Insert(locale.format('%d', total_cast_images, True)\
        + " new TV cast image(s) added.", True)
if total_episode_images > 0:
    db.MK_Server_Database_Notification_Insert(locale.format('%d', total_episode_images, True)\
        + " new TV episode image(s) added.", True)

# log end
db.MK_Server_Database_Activity_Insert('MediaKraken_Server theTVDB Images Stop', None,\
    'System: Server theTVDB Images Stop', 'ServerTVDBImagesStop', None, None, 'System')

# commit all changes
db.MK_Server_Database_Commit()

# close the database
db.MK_Server_Database_Close()
