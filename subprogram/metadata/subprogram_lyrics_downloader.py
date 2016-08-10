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

import sys
import logging
import os
import signal
sys.path.append("../MediaKraken_Common")
sys.path.append("./")  # for db import
import MK_Common_File
import MK_Common_Chart_Lyrics
improt MK_Common_Logging
import database as database_base
import locale
locale.setlocale(locale.LC_ALL, '')

# create the file for pid
pid_file = '../pid/' + str(os.getpid())
MK_Common_File.MK_Common_File_Save_Data(pid_file, 'Sub_Lyrics_Downloader', False, False, None)

def signal_receive(signum, frame):
    print 'CHILD Lyrics: Received USR1'
    # remove pid
    os.remove(pid_file)
    # cleanup db
    db.MK_Server_Database_Rollback()
    db.MK_Server_Database_Close()
    sys.stdout.flush()
    sys.exit(0)

if str.upper(sys.platform[0:3]) == 'WIN' or str.upper(sys.platform[0:3]) == 'CYG':
    signal.signal(signal.SIGBREAK, signal_receive)   # ctrl-c
else:
    signal.signal(signal.SIGTSTP, signal_receive)   # ctrl-z
    signal.signal(signal.SIGUSR1, signal_receive)   # ctrl-c


# start logging
MK_Common_Logging.MK_Common_Logging_Start('./log/MediaKraken_Subprogram_Lyrics_Download')


total_download_attempts = 0
# main code
def main(argv):
    global total_download_attempts
    # parse arguments
    sub_lang = "en"
    # search the directory for filter files
    for media_row in MK_Common_File.MK_Common_File_Dir_List():
        logging.debug(media_row)


if __name__ == "__main__":
    print 'Total lyrics download attempts:', total_download_attempts
    # send notications
    if total_download_attempts > 0:
        db.MK_Server_Database_Notification_Insert(locale.format('%d', total_download_attempts, True) + " lyric(s) downloaded.", True)
    # commit all changes
    db.MK_Server_Database_Commit()
    # close DB
    db.MK_Server_Database_Close()
    # remove pid
    os.remove(pid_file)
