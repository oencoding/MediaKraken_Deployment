'''
  Copyright (C) 2017 Quinn D Granfor <spootdev@gmail.com>

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
from sys import version_info

py3 = version_info[0] > 2 #creates boolean value for test that Python major version > 2

compose_text = "version: '2'\n"\
    "# MediaKraken\n"\
    "# Volumes are HOST directory and then CONTAINER directory\n\n"\
    "services:\n"
env_text = ""

if py3:
  response = input("Please enter your PostgreSQL instance IP/Hostname (None for builtin database - default builtin): ")
else:
  response = raw_input("Please enter your PostgreSQL instance IP/Hostname (None for builtin database - default builtin): ")
if response == 'None' or len(response) == 0:
    # builtin
    compose_text += "\n\n  # Postgresql server\n"\
        "  database:\n"\
        "    image: mediakraken/mkdatabase:latest\n"\
        "    environment:\n"\
        "      - POSTGRES_DB =${DBDATABASE}\n"\
        "      - POSTGRES_USER =${DBUSER}\n"\
        "      - POSTGRES_PASSWORD =${DBPASS}:\n"\
        "    container_name: mkdatabase\n"\
        "    volumes:\n"\
        "      - /var/lib/postgresql: /var/lib/postgresql\n"\
        "    networks:\n"\
        "      - mediakraken_dbnetwork\n"\
        "    restart: unless - stopped\n"

if py3:
  response = input("Host MusicBrainz Mirror? (If yes, enter Brainzcode - default no): ")
else:
  response = raw_input("Host MusicBrainz Mirror? (If yes, enter Brainzcode - default no): ")

if py3:
  response = input("Please enter your Transmission instance IP/Hostname (None for builtin server - default builtin: ")
else:
  response = raw_input("Please enter your Transmission instance IP/Hostname (None for builtin server - default builtin: ")
if response == 'None' or len(response) == 0:
    # builtin
    pass

# setup the server
compose_text += "\n\n  # Main app server which controls the show\n"\
    "  appserver:\n"\
    "    image: mediakraken/mkserver:latest\n"\
    "    environment:\n"\
    "      - POSTGRES_DB_HOST=${DBHOST}\n"\
    "      - POSTGRES_DB=${DBDATABASE}\n"\
    "      - POSTGRES_USER=${DBUSER}\n"\
    "      - POSTGRES_PASSWORD=${DBPASS}\n"\
    "      - SWARMIP=${SWARMIP}\n"\
    "    container_name: mkserver\n"\
    "    depends_on:\n"\
    "      - pgbounce\n"\
    "      - rabbit\n"\
    "    entrypoint: ./wait-for-it-ash.sh -h pgbounce -p 6432 -t 30 -- python main_server.py\n"\
    "    ports:\n"\
    "      - \"8903:8903\"\n"\
    "    volumes:\n"\
    "      - /var/log/mediakraken:/mediakraken/log\n"\
    "      - /var/opt/mediakraken/devices:/mediakraken/devices\n"\
    "      - /var/opt/mediakraken/certs:/mediakraken/key\n"\
    "      - /var/opt/mediakraken/backup:/mediakraken/backup\n"\
    "      - /home/mediakraken:/mediakraken/mnt\n"\
    "      - /var/run/docker.sock:/var/run/docker.sock\n"\
    "      - /var/opt/mediakraken/images:/mediakraken/web_app/MediaKraken/static/meta/images\n"\
    "    networks:\n"\
    "      - mediakraken_network\n"\
    "      - mediakraken_dbnetwork\n"\
    "    restart: unless-stopped\n"\
    "    # to allow mount nfs/cifs\n"\
    "    cap_add:\n"\
    "      - SYS_ADMIN\n"\
    "      - DAC_READ_SEARCH\n"

# the main webservice
compose_text += "\n\n  # Runs the web service for the main server application\n"\
    "  webserver:\n"\
    "    image: mediakraken/mkwebapp:latest\n"\
    "    environment:\n"\
    "      - POSTGRES_DB=${DBDATABASE}\n"\
    "      - POSTGRES_USER=${DBUSER}\n"\
    "      - POSTGRES_PASSWORD=${DBPASS}\n"\
    "    container_name: mkwebapp\n"\
    "    depends_on:\n"\
    "      - pgbounce\n"\
    "      - rabbit\n"\
    "      - redis\n"\
    "    entrypoint: ./wait-for-it-ash.sh -h pgbounce -p 6432 -t 30 -- uwsgi --socket 0.0.0.0:8080 --protocol http --chdir=./web_app --ini ./web_app/mediakraken_uwsgi_alpine.ini\n"\
    "    volumes:\n"\
    "      - /var/log/mediakraken:/mediakraken/log\n"\
    "      - /home/mediakraken:/mediakraken/mnt\n"\
    "      - /var/opt/mediakraken/images:/mediakraken/web_app/MediaKraken/static/meta/images\n"\
    "      - /var/run/docker.sock:/var/run/docker.sock\n"\
    "    networks:\n"\
    "      - mediakraken_network\n"\
    "      - mediakraken_dbnetwork\n"\
    "    restart: unless-stopped\n"

# setup the metadata fetcher
compose_text += "\n\n  # runs the server to fetch/process all metadata\n"\
    "  metadata:\n"\
    "    image: mediakraken/mkmetadata:latest\n"\
    "    environment:\n"\
    "      - POSTGRES_DB=${DBDATABASE}\n"\
    "      - POSTGRES_USER=${DBUSER}\n"\
    "      - POSTGRES_PASSWORD=${DBPASS}\n"\
    "    container_name: mkmetadata\n"\
    "    depends_on:\n"\
    "      - pgbounce\n"\
    "    entrypoint: ./wait-for-it-ash.sh -h pgbounce -p 6432 -t 30 -- python main_server_metadata_api.py\n"\
    "    volumes:\n"\
    "      - /var/log/mediakraken:/mediakraken/log\n"\
    "      - /home/mediakraken:/mediakraken/mnt\n"\
    "      - /var/opt/mediakraken/images:/mediakraken/web_app/MediaKraken/static/meta/images\n"\
    "    networks:\n"\
    "      - mediakraken_network\n"\
    "      - mediakraken_dbnetwork\n"\
    "    restart: unless-stopped\n"

# pgbouncer for connection pooling
compose_text += "\n\n  # pgbouncer\n"\
    "  pgbounce:\n"\
    "    image: mediakraken/mkpgbounce:latest\n"\
    "    environment:\n"\
    "      - DB_HOST=${DBHOST}\n"\
    "      - DB_USER=${DBUSER}\n"\
    "      - DB_PASSWORD=${DBPASS}\n"\
    "      - POOL_MODE=transaction\n"\
    "      - MAX_CLIENT_CONN=500\n"\
    "      - DEFAULT_POOL_SIZE=85\n"\
    "      - SERVER_RESET_QUERY=DISCARD ALL\n"\
    "    container_name: mkpgbounce\n"\
    "    depends_on:\n"\
    "      - database\n"\
    "    entrypoint: ./wait-for-it-ash.sh -h database -p 5432 -t 30 -- ./entrypoint.sh\n"\
    "    networks:\n"\
    "      - mediakraken_dbnetwork\n"\
    "    restart: unless-stopped\n"

# setup the nginx proxy server
compose_text += "\n\n  # runs the nginx proxy service\n"\
    "  nginx:\n"\
    "    image: mediakraken/mknginx:latest\n"\
    "    container_name: mknginx\n"\
    "    entrypoint: /usr/bin/wait-for-it-ash.sh -h webserver -p 8080 -t 30 -- nginx\n"\
    "    volumes:\n"\
    "      - /var/log/mediakraken/nginx:/var/log/mediakraken/nginx\n"\
    "      - /var/opt/mediakraken/certs:/etc/nginx/certs\n"\
    "    ports:\n"\
    "      - \"8900:8900\"\n"\
    "    networks:\n"\
    "      - mediakraken_network\n"\
    "    restart: unless-stopped\n"

# setup the redis server
compose_text += "\n\n  # runs the redis service for flask\n"\
    "  redis:\n"\
    "    image: mediakraken/mkredis:latest\n"\
    "    container_name: mkredis\n"\
    "    ports:\n"\
    "      - \"6379:6379\"\n"\
    "    networks:\n"\
    "      - mediakraken_network\n"\
    "    restart: unless-stopped\n"

# setup the broadcast server
compose_text += "\n\n  # start broadcast server (so clients can find server)\n"\
    "  broadcast:\n"\
    "    image: mediakraken/mkbroadcast:latest\n"\
    "    container_name: mkbroadcast\n"\
    "    entrypoint: python subprogram_broadcast.py\n"\
    "    ports:\n"\
    "      - \"9101:9101\"\n"\
    "    volumes:\n"\
    "      - /var/run/docker.sock:/var/run/docker.sock\n"\
    "    network_mode: host\n"\
    "    restart: unless-stopped\n"

# setup the device scanner
compose_text += "\n\n  # scan for new hardware devices\n"\
    "  devicescan:\n"\
    "    image: mediakraken/mkdevicescan:latest\n"\
    "    container_name: mkdevicescan\n"\
    "    entrypoint: python main_hardware_discover.py\n"\
    "    volumes:\n"\
    "      - /var/log/mediakraken:/mediakraken/log\n"\
    "      - /var/opt/mediakraken/devices:/mediakraken/devices\n"\
    "    network_mode: host\n"

# setup the rabbit
compose_text += "\n\n  # rabbit\n"\
    "  # https://github.com/maryvilledev/alpine-rmq\n"\
    "  rabbit:\n"\
    "    image: mediakraken/mkrabbitmq:latest\n"\
    "    container_name: mkrabbitmq\n"\
    "    ports:\n"\
    "      - \"5672:5672\"\n"\
    "    restart: unless-stopped\n"\
    "    networks:\n"\
    "      - mediakraken_network\n"

# runs portainer
compose_text += "\n\n  dockmanage:\n" \
    "    image: portainer / portainer:latest\n"\
    "      container_name: mkportainer\n"\
    "      ports:\n"\
    "        - \"9000:9000\"\n"\
    "      volumes:\n"\
    "        - /var/run/docker.sock:/var/run/docker.sock\n"\
    "        - /var/opt/mediakraken/data:/data\n"\
    "      restart: unless - stopped\n"

# add networking info
compose_text += "\n\nnetworks:\n"\
    "  # Twisted and AMQP communications network\n"\
    "  mediakraken_network:\n"\
    "    driver: bridge\n"\
    "  # Database communications network\n"\
    "  mediakraken_dbnetwork:\n"\
    "    driver: bridge\n"

# write the config file
file_handle = open('docker-compose.yml', 'w+')
file_handle.write(compose_text)
file_handle.close()

# write the env file
file_handle = open('.env', 'w+')
file_handle.write(env_text)
file_handle.close()

print("MediaKraken setup has been completed. Run ./mediakraken_start.sh' in Linux or 'docker-compose up -d' to start the application.")