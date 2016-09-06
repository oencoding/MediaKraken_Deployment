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
import logging # pylint: disable=W0611
import sys
from common import common_config_ini
from common import common_logging
import signal
from concurrent import futures
import subprocess
from datetime import timedelta


def signal_receive(signum, frame): # pylint: disable=W0613
    """
    Handle signal interupt
    """
    print('CHILD Sync: Received USR1')
    # cleanup db
    db_connection.db_rollback()
    db_connection.db_close()
    sys.stdout.flush()
    sys.exit(0)


def worker(row_data):
    """
    Worker ffmpeg thread for each sync job
    """
    logging.debug("row: %s", row_data)
    # open the database
    config_handle, option_config_json, thread_db = common_config_ini.com_config_read()
    # row_data
    # 0 mm_sync_guid uuid NOT NULL, 1 mm_sync_path text, 2 mm_sync_path_to text,
    # 3 mm_sync_options_json jsonb
    ffmpeg_params = ['ffmpeg', '-i', thread_db.db_media_path_by_uuid(\
        row_data['mm_sync_options_json']['Media GUID'])[0].encode('utf8')]
    if row_data['mm_sync_options_json']['Options']['Size'] != "Clone":
        ffmpeg_params.extend(('-fs',\
            row_data['mm_sync_options_json']['Options']['Size'].encode('utf8')))
    if row_data['mm_sync_options_json']['Options']['VCodec'] != "Copy":
        ffmpeg_params.extend(('-vcodec', row_data['mm_sync_options_json']['Options']['VCodec']))
    if row_data['mm_sync_options_json']['Options']['AudioChannels'] != "Copy":
        ffmpeg_params.extend(('-ac',\
            row_data['mm_sync_options_json']['Options']['AudioChannels'].encode('utf8')))
    if row_data['mm_sync_options_json']['Options']['ACodec'] != "Copy":
        ffmpeg_params.extend(('-acodec',\
            row_data['mm_sync_options_json']['Options']['ACodec'].encode('utf8')))
    if row_data['mm_sync_options_json']['Options']['ASRate'] != 'Default':
        ffmpeg_params.extend(('-ar', row_data['mm_sync_options_json']['Options']['ASRate']))
    ffmpeg_params.append(row_data['mm_sync_path_to'].encode('utf8') + "."\
        + row_data['mm_sync_options_json']['Options']['VContainer'])
    logging.debug("ffmpeg: %s", ffmpeg_params)
    ffmpeg_pid = subprocess.Popen(ffmpeg_params, shell=False, stdout=subprocess.PIPE)
    # output after it gets started
    #  Duration: 01:31:10.10, start: 0.000000, bitrate: 4647 kb/s
    # frame= 1091 fps= 78 q=-1.0 Lsize=    3199kB time=00:00:36.48
    # bitrate= 718.4kbits/s dup=197 drop=0 speed= 2.6x
    media_duration = None
    while True:
        line = ffmpeg_pid.stdout.readline()
        if line != '':
            logging.debug('ffmpeg out: %' % line.rstrip())
            if line.find("Duration:") != -1:
                media_duration = timedelta(line.split(': ', 1)[1].split(',', 1)[0])
            elif line[0:5] == "frame":
                time_string = timedelta(line.split('=', 5)[5].split(' ', 1)[0])
                time_percent = time_string.total_seconds() / media_duration.total_seconds()
                thread_db.db_sync_progress_update(row_data['mm_sync_guid'],\
                    time_percent)
                thread_db.db_commit()
        else:
            break
    ffmpeg_pid.wait()
    thread_db.db_activity_insert('MediaKraken_Server Sync', None,\
        'System: Server Sync', 'ServerSync', None, None, 'System')
    thread_db.db_sync_delete(row_data[0]) # guid of sync record
    #thread_db.store record in activity table
    thread_db.db_commit()
    thread_db.db_close()
    return


# start logging
common_logging.com_logging_start('./log/MediaKraken_Subprogram_Sync')


# open the database
config_handle, option_config_json, db_connection = common_config_ini.com_config_read()


# log start
db_connection.db_activity_insert('MediaKraken_Server Sync Start', None,\
    'System: Server Sync Start', 'ServerSyncStart', None, None, 'System')


# grab some dirs to scan and thread out the scans
if str.upper(sys.platform[0:3]) == 'WIN' or str.upper(sys.platform[0:3]) == 'CYG':
    signal.signal(signal.SIGBREAK, signal_receive)   # ctrl-c # pylint: disable=E1101
else:
    signal.signal(signal.SIGTSTP, signal_receive)   # ctrl-z
    signal.signal(signal.SIGUSR1, signal_receive)   # ctrl-c


# switched to this since tracebacks work this method
sync_data = db_connection.db_sync_list()
with futures.ThreadPoolExecutor(len(sync_data)) as executor:
    futures = [executor.submit(worker, n) for n in sync_data]
    for future in futures:
        logging.debug(future.result())


# log end
db_connection.db_activity_insert('MediaKraken_Server Sync Stop', None,\
    'System: Server Sync Stop', 'ServerSyncStop', None, None, 'System')

# commit all changes
db_connection.db_commit()

# close the database
db_connection.db_close()
