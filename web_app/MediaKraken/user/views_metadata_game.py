"""
User view in webapp
"""
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
from flask import Blueprint, render_template, g, request, current_app, jsonify,\
    redirect, url_for, abort
from flask_login import login_required
from flask_login import current_user
from fractions import Fraction
blueprint = Blueprint("user_metadata_game", __name__, url_prefix='/users', static_folder="../static")
#import locale
#locale.setlocale(locale.LC_ALL, '')
import logging # pylint: disable=W0611
import subprocess
import natsort
import sys
sys.path.append('..')
sys.path.append('../..')
from common import common_config_ini
from common import common_internationalization
from common import common_pagination
from common import common_string
import database as database_base


option_config_json, db_connection = common_config_ini.com_config_read()


@blueprint.route('/meta_game_detail/<guid>/')
@blueprint.route('/meta_game_detail/<guid>')
@login_required
def metadata_game_detail(guid):
    """
    Display metadata game detail
    """
    return render_template('users/metadata/meta_game_detail.html',
                          )


@blueprint.route('/meta_game_list')
@blueprint.route('/meta_game_list/')
@login_required
def metadata_game_list():
    """
    Display list of game metadata
    """
    return render_template('users/metadata/meta_game_list.html',
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
