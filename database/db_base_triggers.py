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
import uuid
try:
    import cPickle as pickle
except: # pylint: disable=W0702
    import pickle


def db_trigger_insert(self, command_list, background=False):
    """
    # create/insert a trigger
    """
    new_guid = str(uuid.uuid4())
    self.db_cursor.execute('insert into mm_trigger (mm_trigger_guid,mm_trigger_command,'
        'mm_trigger_background) values (%s,%s,%s)', (new_guid, pickle.dumps(command_list),
        background))
    self.db_commit()
    return new_guid


def db_triggers_read(self):
    """
    # read the triggers
    """
    self.db_cursor.execute('select mm_trigger_guid,mm_trigger_command,'
        'mm_trigger_background from mm_trigger')
    return self.db_cursor.fetchall()


def db_triggers_delete(self, guid):
    """
    # remove trigger
    """
    self.db_cursor.execute('delete from mm_trigger where mm_trigger_guid = %s', (guid,))
    self.db_commit()
