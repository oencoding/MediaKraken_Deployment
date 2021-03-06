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
import json
import requests
from . import common_metadata
from . import common_network
import tmdbsimple as tmdb


class CommonMetadataTMDB(object):
    """
    Class for interfacing with TMDB
    """
    def __init__(self, option_config_json):
        tmdb.API_KEY = option_config_json['API']['themoviedb']
        self.API_KEY = option_config_json['API']['themoviedb']


    def com_tmdb_search(self, movie_title, movie_year=None, id_only=False):
        """
        # search for movie title and year
        """
        logging.info("tmdb search %s %s", movie_title, movie_year)
        search = tmdb.Search()
        response = search.movie(query=movie_title)
        for s in search.results:
            logging.info("result: %s %s %s", s['title'], s['id'],
                         s['release_date'].split('-', 1)[0])
            if movie_year is not None and (str(movie_year) == s['release_date'].split('-', 1)[0]
                    or str(int(movie_year) - 1) == s['release_date'].split('-', 1)[0]
                    or str(int(movie_year) + 1) == s['release_date'].split('-', 1)[0]):
                if not id_only:
                    return 'info', self.com_tmdb_meta_by_id(s['id'])
                else:
                    return 'idonly', s['id'] #, s['title']
        return 're', search.results


    def com_tmdb_metadata_by_id(self, tmdb_id):
        """
        Fetch all metadata by id to reduce calls
        """
        return requests.get('https://api.themoviedb.org/3/movie/%s'\
            '?api_key=%s&append_to_response=credits,reviews,release_dates,videos' %
            (tmdb_id, self.API_KEY))


    def com_tmdb_metadata_bio_by_id(self, tmdb_id):
        """
        Fetch all metadata bio by id to reduce calls
        """
        return requests.get('https://api.themoviedb.org/3/person/%s'\
            '?api_key=%s&append_to_response=combined_credits,external_ids,images' %
            (tmdb_id, self.API_KEY))


    def com_tmdb_meta_bio_image_build(self, thread_db, result_json):
        """
        # download info and set data to be ready for insert into database
        """
        logging.info('tmdb bio build: %s', result_json)
        # create file path for poster
        image_file_path = common_metadata.com_meta_image_file_path(result_json['name'],
            'person')
        logging.info('tmdb bio image path: %s', image_file_path)
        if 'profile_path' in result_json and result_json['profile_path'] is not None:
            if not os.path.isfile(image_file_path + result_json['profile_path']):
                thread_db.db_download_image_insert('themoviedb',
                    json.dumps({'url': 'https://image.tmdb.org/t/p/original'
                    + result_json['profile_path'],
                    'local': image_file_path + result_json['profile_path']}))
        # TODO loop through cast to store new movies to fetch
        # set local image json
        return ({'Images': {'themoviedb': image_file_path}})


    def com_tmdb_metadata_id_max(self):
        """
        Grab high metadata id
        """
        return json.loads(common_network.mk_network_fetch_from_url(
            'https://api.themoviedb.org/3/movie/latest'
            '?api_key=%s' % self.API_KEY))['id']


    def com_tmdb_metadata_bio_id_max(self):
        """
        Grab high bios metadata id (person)
        """
        return json.loads(common_network.mk_network_fetch_from_url(
            'https://api.themoviedb.org/3/person/latest'
            '?api_key=%s' % self.API_KEY))['id']


    def com_tmdb_metadata_tv_id_max(self):
        """
        Grab high tv metadata id
        """
        return json.loads(common_network.mk_network_fetch_from_url(
            'https://api.themoviedb.org/3/tv/latest'
            '?api_key=%s' % self.API_KEY))['id']


    def com_tmdb_meta_by_id(self, tmdb_id):
        """
        # movie info by tmdb
        """
        movie = tmdb.Movies(tmdb_id)
        try:
            metadata = movie.info()
        except Exception as err_code:
            logging.error("TMDB Fetch Error: %s", str(err_code))
            metadata = None
        return metadata


    def com_tmdb_meta_cast_by_id(self, tmdb_id):
        """
        # cast by tmdb
        """
        movie = tmdb.Movies(tmdb_id)
        try:
            metadata = movie.credits()
        except Exception as err_code:
            logging.error("TMDB Fetch Credits Error: %s", str(err_code))
            metadata = None
        return metadata


    def com_tmdb_meta_review_by_id(self, tmdb_id):
        """
        # review by tmdb
        """
        movie = tmdb.Movies(tmdb_id)
        try:
            metadata = movie.reviews()
        except Exception as err_code:
            logging.error("TMDB Fetch Review Error: %s", str(err_code))
            metadata = None
        return metadata


    def com_tmdb_meta_release_by_id(self, tmdb_id):
        """
        # release by tmdb
        """
        movie = tmdb.Movies(tmdb_id)
        try:
            metadata = movie.releases()
        except Exception as err_code:
            logging.error("TMDB Fetch Releases Error: %s", str(err_code))
            metadata = None
        return metadata


# TODO
#The supported external sources for each object are as follows:
#    Movies: imdb_id
#    People: imdb_id, freebase_mid, freebase_id, tvrage_id
#    TV Series: imdb_id, freebase_mid, freebase_id, tvdb_id, tvrage_id
#    TV Seasons: freebase_mid, freebase_id, tvdb_id, tvrage_id
#    TV Episodes: imdb_id, freebase_mid, freebase_id, tvdb_id, tvrage_id


    def com_tmdb_meta_by_imdb_id(self, imdb_id):
        """
        # search by imdb
        """
        movie = tmdb.Find(imdb_id)
        try:
            metadata = movie.info(external_source='imdb_id')
        except Exception as err_code:
            logging.error("TMDB Fetch imdb Error: %s", str(err_code))
            metadata = None
        return metadata


    def com_tmdb_meta_changes_movie(self):
        """
        # movie changes since date within 24 hours
        """
        changes = tmdb.Changes()
        movie_changes = changes.movie()
        return movie_changes


    def com_tmdb_meta_changes_tv(self):
        """
        # tv changes since date within 24 hours
        """
        changes = tmdb.Changes()
        tv_changes = changes.tv()
        return tv_changes


    def com_tmdb_meta_changes_person(self):
        """
        # person changes since date within 24 hours
        """
        changes = tmdb.Changes()
        person_changes = changes.person()
        return person_changes


    def com_tmdb_meta_collection_by_id(self, tmdb_id):
        """
        # collection info
        """
        movie_collection = tmdb.Collections(tmdb_id)
        try:
            metadata = movie_collection.info()
        except Exception as err_code:
            logging.error("TMDB Fetch Collection Error: %s", str(err_code))
            metadata = None
        return metadata


    def com_tmdb_meta_info_build(self, result_json):
        """
        # download info and set data to be ready for insert into database
        """
        logging.info('tmdb info build: %s', result_json)
        # create file path for poster
        image_file_path = common_metadata.com_meta_image_file_path(result_json['title'],
            'poster')
        logging.info('tmdb image path: %s', image_file_path)
        poster_file_path = None
        if result_json['poster_path'] is not None:
            image_file_path += result_json['poster_path']
            if not os.path.isfile(image_file_path):
                common_network.mk_network_fetch_from_url('https://image.tmdb.org/t/p/original'
                    + result_json['poster_path'], image_file_path)
            poster_file_path = image_file_path
        # create file path for backdrop
        image_file_path = common_metadata.com_meta_image_file_path(result_json['title'],
            'backdrop')
        backdrop_file_path = None
        if result_json['backdrop_path'] is not None:
            image_file_path += result_json['backdrop_path']
            if not os.path.isfile(image_file_path):
                common_network.mk_network_fetch_from_url('https://image.tmdb.org/t/p/original'
                    + result_json['backdrop_path'], image_file_path)
            backdrop_file_path = image_file_path
        # its a number so make it a string just in case
        series_id_json = json.dumps({'imdb': result_json['imdb_id'],
            'themoviedb': str(result_json['id'])})
        # set local image json
        image_json = ({'Images': {'themoviedb': {'Backdrop': backdrop_file_path,
            'Poster': poster_file_path}}})
   #result_json.update({'LocalImages':{'Backdrop':backdrop_file_path, 'Poster':poster_file_path}})
        return series_id_json, result_json, image_json
