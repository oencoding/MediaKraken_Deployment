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
import os
from common import common_file
from common import common_logging
from common import common_signal

# set signal exit breaks
common_signal.com_signal_set_break()


# start logging
common_logging.com_logging_start('./log/MediaKraken_Subprogram_Subtitle_Downloader')


total_download_attempts = 0


# parse arguments
sub_lang = "en"
# search the directory for filter files
for media_row in common_file.com_file_dir_list('/nfsmount/TV_Shows_Misc/',
        ('avi', 'mkv', 'mp4', 'm4v'), True):
    # run the subliminal fetch for episode
    logging.info("title check: %s", media_row.rsplit('.', 1)[0] + "." + sub_lang + ".srt")
    # not os.path.exists(media_row.rsplit('.',1)[0] + ".en.srt")
    # and not os.path.exists(media_row.rsplit('.',1)[0] + ".eng.srt")
    if not os.path.exists(media_row.rsplit('.', 1)[0] + "." + sub_lang + ".srt"):
        # change working dir so srt is saved in the right spot
        total_download_attempts += 1
        os.chdir(media_row.rsplit('/', 1)[0])
        file_handle = os.popen("subliminal -l " + sub_lang + " -- \"" + media_row + "\"")
        cmd_output = file_handle.read()
        logging.info("Download Status: %s", cmd_output)


print('Total subtitle download attempts: %s' % total_download_attempts)
