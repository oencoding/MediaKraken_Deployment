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
from . import common_file
import sys
from twisted.internet.protocol import ClientFactory
from twisted.internet import reactor, ssl
from twisted.protocols.basic import Int32StringReceiver


networkProtocol = None
metaapp = None


def signal_receive(signum, frame):
    global proc_ffserver
    print('CHILD Slave: Received USR1')
    sys.stdout.flush()
    sys.exit(0)


class TheaterClient(Int32StringReceiver):
    STARTED = 0
    CHECKING_PORT = 1
    CONNECTED = 2
    NOTSTARTED = 3
    PORTCLOSED = 4
    CLOSED = 5


    def __init__(self):
        self.MAX_LENGTH = 32000000
        self.connStatus = TheaterClient.STARTED


    def connectionMade(self):
        global networkProtocol
        self.connStatus = TheaterClient.CONNECTED
        networkProtocol = self


    def stringReceived(self, data):
        MediaKrakenApp.process_message(metaapp, data)


class TheaterFactory(ClientFactory):


    def __init__(self, app):
        self.app = app
        self.protocol = None


    def startedConnecting(self, connector):
        logging.info('Started to connect to %s', connector.getDestination())


    def clientConnectionLost(self, conn, reason):
        logging.info("Connection Lost")


    def clientConnectionFailed(self, conn, reason):
        logging.info("Connection Failed")


    def buildProtocol(self, addr):
        logging.info('Connected to %s', str(addr))
        self.protocol = TheaterClient()
        return self.protocol


class MediaKrakenApp():
    connection = None


    def exit_program(self):
        pass


    def build(self):
        global metaapp
        root = MediaKrakenApp()
        metaapp = self
        self.connect_to_server()
        return root


    def connect_to_server(self):
        """
        Connect to debug server
        """
        reactor.connectSSL(option_config_json['MediaKrakenServer']['Host'],\
            option_config_json['MediaKrakenServer']['Port'],\
            TheaterFactory(self), ssl.ClientContextFactory())
        reactor.run()


    def process_message(self, server_msg):
        """
        Process network message from server
        """
        messageWords = server_msg.split(' ', 1)
        logging.debug('message: %s', messageWords[0])
        logging.debug("len: %s", len(server_msg))
        logging.debug("chunks: %s", len(messageWords))
        msg = None
        if messageWords[0] == "IDENT":
            msg = "VALIDATE " + "slave" + " " + "password" + " " + platform.node()
        # user commands
        elif messageWords[0] == "PLAYMEDIA":
            self.proc_ffmpeg_stream = subprocess.Popen(pickle.loads(messageWords[1], shell=False))
        else:
            logging.debug("unknown message type")
        if msg is not None:
            logging.debug("should be sending data")
            networkProtocol.sendString(msg)


if __name__ == '__main__':
    MediaKrakenApp().build()
