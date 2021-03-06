"""
User view in webapp
"""
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from flask import Blueprint, render_template, g, request, current_app, jsonify,\
    redirect, url_for, abort
from flask_login import login_required
from flask_login import current_user
blueprint = Blueprint("user_movie_genre", __name__, url_prefix='/users', static_folder="../static")
#import locale
#locale.setlocale(locale.LC_ALL, '')
import logging # pylint: disable=W0611
import sys
sys.path.append('..')
sys.path.append('../..')
from common import common_config_ini
from common import common_internationalization
from common import common_pagination
import database as database_base


option_config_json, db_connection = common_config_ini.com_config_read()


@blueprint.route("/movie_genre")
@blueprint.route("/movie_genre/")
@login_required
def user_movie_genre_page():
    """
    Display movies split up by genre
    """
    media = []
    for row_data in g.db_connection.db_media_movie_count_by_genre(
            g.db_connection.db_media_uuid_by_class('Movie')):
        media.append((row_data['gen']['name'],
                      common_internationalization.com_inter_number_format(row_data[1]),
                      row_data[0]['name'] + ".png"))
    return render_template('users/user_movie_genre_page.html', media=sorted(media))


@blueprint.route("/movie/<genre>")
@blueprint.route("/movie/<genre>/")
@login_required
def user_movie_page(genre):
    """
    Display movie page
    """
    page, per_page, offset = common_pagination.get_page_items()
    media = []
    for row_data in g.db_connection.db_web_media_list(
            g.db_connection.db_media_uuid_by_class('Movie'),
            list_type='movie', list_genre=genre, list_limit=per_page, group_collection=False,
            offset=offset, include_remote=True):
        # 0- mm_media_name, 1- mm_media_guid, 2- mm_media_json,
        # 3 - mm_metadata_localimage_json
        logging.info("row2: %s", row_data['mm_media_json'])
        json_image = row_data['mm_metadata_localimage_json']
        # set watched
        try:
            watched_status\
                = row_data['mm_media_json']['UserStats'][current_user.get_id()]['watched']
        except:
            watched_status = False
        # set synced
        try:
            sync_status = row_data['mm_media_json']['UserStats'][current_user.get_id()]['sync']
        except:
            sync_status = False
        # set rating
        if 'UserStats' in row_data['mm_media_json']\
            and current_user.get_id() in row_data['mm_media_json']['UserStats']\
            and 'Rating' in row_data['mm_media_json']['UserStats'][current_user.get_id()]:
                rating_status = row_data['mm_media_json']['UserStats'][current_user.get_id()]['Rating']
                if rating_status == 'favorite':
                    rating_status = '/static/images/favorite-mark.png'
                elif rating_status == 'like':
                    rating_status = '/static/images/thumbs-up.png'
                elif rating_status == 'dislike':
                    rating_status = '/static/images/dislike-thumb.png'
                elif rating_status == 'poo':
                    rating_status = '/static/images/pile-of-dung.png'
        else:
            rating_status = None
        # set mismatch
        try:
            match_status = row_data['mismatch']
        except:
            match_status = False
        logging.info("status: %s %s %s %s", watched_status, sync_status, rating_status,
            match_status)
        if 'themoviedb' in json_image['Images'] and 'Poster' in json_image['Images']['themoviedb']\
                and json_image['Images']['themoviedb']['Poster'] is not None:
            media.append((row_data['mm_media_name'], row_data['mm_media_guid'],
                json_image['Images']['themoviedb']['Poster'],
                watched_status, sync_status, rating_status, match_status))
        else:
            media.append((row_data['mm_media_name'], row_data['mm_media_guid'], None,
                watched_status, sync_status, rating_status, match_status))
    total = g.db_connection.db_web_media_list_count(
        g.db_connection.db_media_uuid_by_class('Movie'), list_type='movie', list_genre=genre,
        group_collection=False, include_remote=True)
    pagination = common_pagination.get_pagination(page=page,
                                                  per_page=per_page,
                                                  total=total,
                                                  record_name='media',
                                                  format_total=True,
                                                  format_number=True,
                                                 )
    return render_template('users/user_movie_page.html', media=media,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                          )


@blueprint.before_request
def before_request():
    """
    Executes before each request
    """
    g.db_connection = database_base.MKServerDatabase()
    g.db_connection.db_open()


@blueprint.teardown_request
def teardown_request(exception): # pylint: disable=W0613
    """
    Executes after each request
    """
    g.db_connection.db_close()
