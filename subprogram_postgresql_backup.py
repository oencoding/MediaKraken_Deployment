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
import time
import sys
import os
sys.path.append("../MediaKraken_Server")
sys.path.append("../MediaKraken_Common")
import common_cloud
import common_logging
import database as database_base

# start logging
common_logging.common_logging_Start('./log/MediaKraken_Subprogram_Postgresql_Backup')

# open the database
db = database_base.MK_Server_Database()
db.MK_Server_Database_Open(Config.get('DB Connections', 'PostDBHost').strip(),\
    Config.get('DB Connections', 'PostDBPort').strip(),\
    Config.get('DB Connections', 'PostDBName').strip(),\
    Config.get('DB Connections', 'PostDBUser').strip(),\
    Config.get('DB Connections', 'PostDBPass').strip())


# log start
db.MK_Server_Database_Activity_Insert('MediaKraken_Server Postgresql Backup Start', None,\
    'System: Server DB Backup Start', 'ServerBackupStart', None, None, 'System')

# popen appears to be trying to execute pgpassword
#proc_back = subprocess.Popen(['PGPASSWORD=' + Config.get('DB Connections','PostDBPass').strip(), 'pg_dump', '-U', Config.get('DB Connections','PostDBUser').strip(), Config.get('DB Connections','PostDBName').strip(), '-F', 'c', '-f', Config.get('MediaKrakenServer','BackupLocal').strip() + '/MediaKraken_Backup_' + time.strftime("%Y%m%d%H%M%S") + '.dump'], shell=False)
#proc_back.pid.wait()

# generate dump file
backup_file_name = 'MediaKraken_Backup_' + time.strftime("%Y%m%d%H%M%S") + '.dump'
os.system('PGPASSWORD=' + Config.get('DB Connections', 'PostDBPass').strip() + ' pg_dump -U '\
    + Config.get('DB Connections', 'PostDBUser').strip() + ' '\
    + Config.get('DB Connections', 'PostDBName').strip() + ' -F c -f '\
    + Config.get('MediaKrakenServer', 'BackupLocal').strip() + '/' + backup_file_name)

# grab settings and options
option_json = db.MK_Server_Database_Option_Status_Read()['mm_options_json']
if option_json['Backup']['BackupType'] != 'local':
    common_cloud.common_cloud_File_Store(option_json['Backup']['BackupType'],\
    Config.get('MediaKrakenServer', 'BackupLocal').strip() + '/'\
    + backup_file_name, backup_file_name, True)

# log end
db.MK_Server_Database_Activity_Insert('MediaKraken_Server Postgresql Backup Stop', None,\
    'System: Server DB Backup Stop', 'ServerBackupStop', None, None, 'System')

# commit records
db.MK_Server_Database_Commit()

# close the database
db.MK_Server_Database_Close()
