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

# pull in the ini file config
import ConfigParser
Config = ConfigParser.ConfigParser()
Config.read("MediaKraken.ini")
from twisted.internet import ssl
from twisted.internet import reactor
from twisted.internet import protocol
from twisted.internet.protocol import Factory
import logging
import sys
sys.path.append("./network")
import network_base_string as network_base
sys.path.append("./") # for db import
import database as database_base
sys.path.append("../MediaKraken_Common")
import MK_Common_File
import MK_Common_Logging
from time import time
import time  # yes, use both otherwise some time code below breaks
import os
import signal


# create the file for pid
pid_file = './pid/' + str(os.getpid())
MK_Common_File.MK_Common_File_Save_Data(pid_file, 'Sub_Reactor_String', False, False, None)


def signal_receive(signum, frame):
    print 'CHILD Reactor String: Received USR1'
    # remove pid
    os.remove(pid_file)
    # cleanup db
    self.db.MK_Server_Database_Rollback()
    self.db.MK_Server_Database_Close()
    sys.stdout.flush()
    sys.exit(0)


class MediaKrakenServerApp(Factory):
    def __init__(self):
        # start logging
        MK_Common_Logging.MK_Common_Logging_Start('./log/MediaKraken_Subprogram_Reactor_String')
        # set other data
        self.server_start_time = time.mktime(time.gmtime())
        self.users = {} # maps user names to network instances
        # open the database
        self.db = database_base.MK_Server_Database()
        self.db.MK_Server_Database_Open(Config.get('DB Connections', 'PostDBHost').strip(), Config.get('DB Connections', 'PostDBPort').strip(), Config.get('DB Connections', 'PostDBName').strip(), Config.get('DB Connections', 'PostDBUser').strip(), Config.get('DB Connections', 'PostDBPass').strip())
        # preload some data from database
        self.genre_list = self.db.MK_Server_Database_Metadata_Genre_List()
        logging.info("Ready for connections!")


    def buildProtocol(self, addr):
        return network_base.Metaman_Network_Events(self.users, self.db, self.genre_list)


if __name__ == '__main__':
    if str.upper(sys.platform[0:3]) == 'WIN' or str.upper(sys.platform[0:3]) == 'CYG':
        signal.signal(signal.SIGBREAK, signal_receive)   # ctrl-c
    else:
        signal.signal(signal.SIGTSTP, signal_receive)   # ctrl-z
        signal.signal(signal.SIGUSR1, signal_receive)   # ctrl-c
    # setup for the ssl keys
    sslContext = ssl.DefaultOpenSSLContextFactory('key/privkey.pem', 'key/cacert.pem')
    reactor.listenSSL(int(Config.get('MediaKrakenServer', 'ListenPort').strip()), MediaKrakenServerApp(), sslContext)
    reactor.run()
    # remove pid
    os.remove(pid_file)
