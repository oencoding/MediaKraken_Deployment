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


def db_media_book_list_count(self):
    """
    book list count
    """
    self.db_cursor.execute('select count(*) from mm_metadata_book, mm_media'
        ' where mm_media_metadata_guid = mm_metadata_book_guid')
    return self.db_cursor.fetchone()[0]


def db_media_book_list(self, offset=None, records=None):
    """
    book list
    """
    if offset is None:
        self.db_cursor.execute('select mm_metadata_book_guid,mm_metadata_book_name '
            'from mm_metadata_book, mm_media'
            ' where mm_media_metadata_guid = mm_metadata_book_guid order by mm_metadata_book_name')
    else:
        self.db_cursor.execute('select mm_metadata_book_guid,mm_metadata_book_name '
            'from mm_metadata_book, mm_media'
            ' where mm_media_metadata_guid = mm_metadata_book_guid order by mm_metadata_book_name '
            'offset %s limit %s', (offset, records))
    return self.db_cursor.fetchall()
