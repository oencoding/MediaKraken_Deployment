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
import pytest
import sys
sys.path.append("../common")
from common_network_Twitch import *


class TestCommonTwitch(object):


    @classmethod
    def setup_class(self):
        self.db = common_network_Twitch.com_Twitch_API()


    @classmethod
    def teardown_class(self):
        pass


    @pytest.mark.parametrize(("stream_limit"), [
        (0),
        (5)])
    def test_com_Twitch_Get_All_Streams(self, stream_limit):
        self.db.com_Twitch_Get_All_Streams(stream_limit)


    def test_com_Twitch_Get_Featured_Streams(self):
        self.db.com_Twitch_Get_Featured_Streams()


    def test_com_Twitch_Get_Summary(self):
        self.db.com_Twitch_Get_Summary()


    def test_com_Twitch_Get_Summary_Viewers(self):
        self.db.com_Twitch_Get_Summary_Viewers()


#    def com_Twitch_Channel_by_User(self, user_name):


#    def com_Twitch_by_Name(self, user_name):


#    def com_Twitch_Channel_by_Name(self, channel_name):


#    def com_Twitch_Get_Videos_by_Channel(self, channel_name, stream_limit):


#    def com_Twitch_Channel_Teams_by_Name(self, channel_name):


#    def com_Twitch_Search_Channel_by_Name(self, channel_name):


#    def com_Twitch_Search_Streams_by_Name(self, stream_game):


#    def com_Twitch_Search_Games_by_Name(self, game_name):
