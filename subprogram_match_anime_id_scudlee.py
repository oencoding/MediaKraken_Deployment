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
import logging
import ConfigParser
Config = ConfigParser.ConfigParser()
Config.read("MediaKraken.ini")
import sys
import signal
import os
sys.path.append("../MediaKraken_Common")
sys.path.append("../MediaKraken_Server")
import common_file
import common_logging
import MK_Common_Scudlee
import database as database_base

# create the file for pid
pid_file = '../pid/' + str(os.getpid())
common_file.common_file_Save_Data(pid_file, 'Sub_Anime_Match', False, False, None)

def signal_receive(signum, frame):
    print('CHILD Anime: Received USR1')
    # remove pid
    os.remove(pid_file)
    # cleanup db
    db.MK_Server_Database_Rollback()
    db.MK_Server_Database_Close()
    sys.stdout.flush()
    sys.exit(0)

# start logging
common_logging.common_logging_Start('./log/MediaKraken_Subprogram_Anime_Scudlee')

# open the database
db = database_base.MK_Server_Database()
db.MK_Server_Database_Open(Config.get('DB Connections', 'PostDBHost').strip(), Config.get('DB Connections', 'PostDBPort').strip(), Config.get('DB Connections', 'PostDBName').strip(), Config.get('DB Connections', 'PostDBUser').strip(), Config.get('DB Connections', 'PostDBPass').strip())

# log start
db.MK_Server_Database_Activity_Insert('MediaKraken_Server Anime Scudlee Start', None,\
    'System: Server Anime Scudlee Start', 'ServerAnimeScudleeStart', None, None, 'System')

if str.upper(sys.platform[0:3]) == 'WIN' or str.upper(sys.platform[0:3]) == 'CYG':
    signal.signal(signal.SIGBREAK, signal_receive)   # ctrl-c
else:
    signal.signal(signal.SIGTSTP, signal_receive)   # ctrl-z
    signal.signal(signal.SIGUSR1, signal_receive)   # ctrl-c

# same code in subprograb update create collections
def store_update_record(db, collection_name, guid_list):
    # store/update the record
    collection_guid = db.MK_Server_Database_Collection_By_Name(collection_name)
    if collection_guid is None:
        # insert
        db.MK_Server_Database_Collection_Insert(collection_name, guid_list)
    else:
        # update
        db.MK_Server_Database_Collection_Update(collection_guid, guid_list)

# check for new scudlee download
MK_Common_Scudlee.MK_Scudlee_Fetch_XML()
# begin the media match on NULL matches
for row_data in MK_Common_Scudlee.MK_Scudlee_Anime_List_Parse():
    logging.debug("row: %s", row_data)
    if row_data is not None:
        # skip media with "no" match...rowdata2 is imdbid
        if (row_data[1] == "OVA" or row_data[1] == "movie" or row_data[1] == "hentai" or row_data[1] == "web") and row_data[2] is None:
            pass
        else:
            # should be valid data, do the update
            db.MK_Server_Database_Metadata_Update_Media_ID_From_Scudlee(row_data[1], row_data[2], row_data[0])

# begin the collections match/create/update
for row_data in MK_Common_Scudlee.MK_Scudlee_Anime_Set_Parse():
    #db.MK_Server_Database_Metadata_Update_Collection_Media_ID_From_Scudlee(row_data[0],row_data[1])
    if row_data[1] == "music video":
        pass
    else:
        store_update_record(db, row_data[0], row_data[1])

# log end
db.MK_Server_Database_Activity_Insert('MediaKraken_Server Anime Scudlee Stop', None,\
    'System: Server Anime Scudlee Stop', 'ServerAnimeScudleeStop', None, None, 'System')
# commit all changes to db
db.MK_Server_Database_Commit()
# close the database
db.MK_Server_Database_Close()

# remove pid
os.remove(pid_file)
