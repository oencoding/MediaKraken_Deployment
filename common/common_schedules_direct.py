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
import hashlib
import json
import requests


class CommonSchedulesDirect(object):
    """
    Class for interfacing with Schedules Direct
    """
    def __init__(self):
        self.headers = {'User-Agent': 'MediaKraken_0.1.6',
                        'Accept-Encoding': 'gzip, deflate'}
        self.BASE_API_URL = 'https://json.schedulesdirect.org/20141201'


    def com_schedules_direct_login(self, user_name, user_password):
        """
        Login to SD
        """
        resp = requests.post(self.BASE_API_URL + "/token", headers=self.headers,
            data=json.dumps({"password": hashlib.sha1(user_password.encode('utf-8')).hexdigest(),
            "username": user_name})).json()
        if resp['code'] != 3000:
            logging.info("SD login response: %s-%s", resp['code'], resp['token'])
            self.headers['token'] = resp['token']
        else:
            logging.error("SD Connection failed")


    def com_schedules_direct_status(self):
        """
        Get status of SD server
        """
        resp = requests.get(self.BASE_API_URL + "/status", headers=self.headers)
        logging.info("SD Status: %s-%s", resp.status_code, resp.json())
        return resp.json()


    def com_schedules_direct_client_version(self):
        """
        Get client version
        """
        resp = requests.get(self.BASE_API_URL + "/version/MediaKraken")
        logging.info("SD Version: %s-%s", resp.status_code, resp.json())
        return resp.json()


    def com_schedules_direct_available(self, countries=None):
        """
        Get available list by country
        """
        if countries is None:
            resp = requests.get(self.BASE_API_URL + "/available")
        else:
            resp = requests.get(self.BASE_API_URL + "/available/countries")
        logging.info("SD Available: %s-%s", resp.status_code, resp.json())
        return resp.json()


    def com_schedules_direct_headends(self, country_code, postal_code):
        """
        Get headends list
        """
        resp = requests.get(self.BASE_API_URL + "/headends?country=" + country_code
                            + "&postalcode=" + postal_code, headers=self.headers)
        logging.info("SD Headends: %s-%s", resp.status_code, resp.json())
        return resp.json()


    def com_schedules_direct_lineup_add(self, lineup_id):
        """
        Add lineup
        """
        resp = requests.put(self.BASE_API_URL + "/lineups/" + lineup_id, headers=self.headers)
        if resp.json()['response'] == 'INVALID_LINEUP':
            logging.error("SD Invalid lineup: %s", lineup_id)
        elif resp.json()['response'] == "DUPLICATE_LINEUP":
            logging.error("SD lineup duplicate: %s", lineup_id)
        else:
            logging.info("SD lineup added: %s", lineup_id)
        logging.info("SD Lineup Add: %s-%s", resp.status_code, resp.json())
        return resp.json()


    def com_schedules_direct_lineup_list(self):
        """
        Get user lineup list
        """
        resp = requests.get(self.BASE_API_URL + "/lineups", headers=self.headers)
        logging.info("SD Lineup: %s-%s", resp.status_code, resp.json())
        return resp.json()


    def com_schedules_direct_lineup_delete(self, lineup_id):
        """
        Delete lineup from user list
        """
        resp = requests.delete(self.BASE_API_URL + "/lineups/" + lineup_id, headers=self.headers)
        if resp.json()['response'] != 'OK':
            logging.error("SD Invalid lineup delete: %s", lineup_id)
        elif resp.json()['code'] == 2103:
            logging.error("SD lineup not in account: %s", lineup_id)
        else:
            logging.info("SD lineup deleted: %s", lineup_id)
        logging.info("SD Lineup Delete: %s-%s", resp.status_code, resp.json())
        return resp.json()


    def com_schedules_direct_lineup_channel_map(self, lineup_id):
        """
        Return channel map for lineup
        """
        resp = requests.get(self.BASE_API_URL + "/lineups/" + lineup_id, headers=self.headers)
        logging.info("SD Channel Map: %s-%s", resp.status_code, resp.json())
        return resp.json()

# TODO automap lineup


    def com_schedules_direct_program_info(self, program_ids):
        """
        Get program info
        """
        resp = requests.post(self.BASE_API_URL + "/programs", headers=self.headers,
                             data=program_ids)
        logging.info("Header: %s", resp.headers)
        logging.info("Text: %s", resp.text)
        logging.info("SD Program Info: %s", resp.status_code)
        return resp.json()


    def com_schedules_direct_program_desc(self, program_ids):
        """
        # this one is only for EP types, not MV
        """
        resp = requests.post(self.BASE_API_URL + "/metadata/description",
                             headers=self.headers, data=program_ids)
        logging.info("Header: %s", resp.headers)
        logging.info("Text: %s", resp.text)
        logging.info("SD Program Desc: %s-%s", resp.status_code, resp.json())
        return resp.json()


    def com_schedules_direct_schedules_by_stationid(self, station_ids):
        """
        Get info by station
        """
        resp = requests.post(self.BASE_API_URL + "/schedules", headers=self.headers,
                             data=station_ids)
        logging.info("SD Station: %s-%s", resp.status_code, resp.json())
        return resp.json()


    def com_schedules_direct_md5(self, station_ids):
        """
        Get md5 list for updates
        """
        resp = requests.post(self.BASE_API_URL + "/schedules/mkd5", headers=self.headers,
                             data=station_ids)
        logging.info("SD MD5: %s-%s", resp.status_code, resp.json())
        return resp.json()


    def com_schedules_still_running(self, program_id):
        """
        Check if program is still running (overtimes)
        """
        resp = requests.post(self.BASE_API_URL + ("/metadata/stillRunning/%s", program_id),
                             headers=self.headers)
        logging.info("SD Running: %s-%s", resp.status_code, resp.json())
        return resp.json()


    def com_schedules_program_metadata(self, program_ids):
        """
        Grab program metadata
        """
        resp = requests.post(self.BASE_API_URL + "/metadata/programs/", headers=self.headers,
                data=program_ids)
        logging.info("SD Program Meta: %s-%s", resp.status_code, resp.json())
        return resp.json()

# TODO retrieve image

# TODO retrieve celbrity image
