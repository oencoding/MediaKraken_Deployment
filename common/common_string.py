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

import logging
import re
import passwordmeter
from socket import inet_ntoa


def common_string_repl_func(m):
    """process regular expression match groups for word upper-casing problem"""
    return m.group(1) + m.group(2).upper()


def common_string_title(title_string):
    """
    capitalize first letter of each word and handling quotes
    """
    return re.sub("(^|\s)(\S)", repl_func, title_string)


def common_string_bytes2human(n):
    """
    Readable numbers for bytes to G, T, etc
    """
    # http://code.activestate.com/recipes/578019
    if n == 0 or type(n) == str:
        return '0B'
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n


def common_string_password_test(password_text):
    """
    Test password strength
    """
    ratings = (
      'Infinitely weak',
      'Extremely weak',
      'Very weak',
      'Weak',
      'Moderately strong',
      'Strong',
      'Very strong',
    )
    strength, improvements = passwordmeter.test(password_text)
    logging.info('Password strength: {} ({})'.format(strength, (ratings[min(len(ratings) - 1,\
            int(strength * len(ratings)))])))
    return (strength, improvements)


def common_string_ip_ascii_to_int(ip):
    """
    Return int from ascii IP
    """
    octets = [int(octet) for octet in ip.split('.')]
    if len(octets) != 4:
        raise Exception("IP [%s] does not have four octets." % (ip))
    encoded = ("%02x%02x%02x%02x" % (octets[0], octets[1], octets[2], octets[3]))
    return int(encoded, 16)


def common_string_ip_int_to_ascii(ip_int):
    """
    Return ascii from IP integer
    """
    return inet_ntoa(hex(ip_int)[2:-1].zfill(8).decode('hex'))


def common_string_unc_to_addr_share_path(unc_path):
    """
    Break up unc to parts
    """
    return (unc_path.split('\\', 5)[2], unc_path.split('\\', 5)[3], '\\'.join(unc_path.split('\\', 5)[4:]))
