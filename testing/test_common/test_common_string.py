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
sys.path.append("./common")
import common_string


# def repl_func(m):


# def capitalize first letter of each word and handling quotes
# def common_string_Title(title_string):


@pytest.mark.parametrize(("n", "expected_result"), [
    (500, "500B"),
    (1500, "1.5K"),
    (1500000, "1.4M"),
    (1500000000, "1.4G"),
    (1500000000000, "1.4T"),
    (1500000000000000, "1.3P"),
    (1500000000000000000, "1.3E"),
    (1500000000000000000000, "1.3Z"),
    (1500000000000000000000000, "1.2Y")])
def test_bytes2human(n, expected_result):
    """
    # readable numbers for bytes to G, T, etc
    """
    assert bytes2human(n) == expected_result


@pytest.mark.parametrize(("password_text", "expected_result"), [
    ("password", "500B"),
    ("Password", "1.5K"),
    ("sRji#234", "1.4M"),
    ("jfioj23$29#DFWEWFWE454938", "1.2Y")])
def test_common_string_password_test(password_text, expected_result):
    """
    # test password
    """
    assert common_string_Password_Test(password_text) == expected_result


# def ip_ascii_to_int(ip):


# def ip_int_to_ascii(ip_int):


# break up unc to parts
# def UNC_To_Addr_Share_Path(unc_path):
