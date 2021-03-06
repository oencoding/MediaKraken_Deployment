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
import zlib
import zipfile
import os
import struct
import sys
from . import common_hash_c_code

# import compression mods
import pylzma
if str.upper(sys.platform[0:3]) == 'WIN' or str.upper(sys.platform[0:3]) == 'CYG':
    from py7zlib import Archive7z


def com_hash_sha1_by_filename(file_name):
    """
    Generate sha1 has by filename
    """
    if file_name.endswith('zip'):
        zip_handle = zipfile.ZipFile(file_name, 'r')  # issues if u do RB
        hash_dict = {}
        for zippedfile in zip_handle.namelist():
            try:
                # calculate sha1 hash
                SHA1 = hashlib.sha1()  # "reset" the sha1 to blank
                SHA1.update(zip_handle.read(zippedfile))
                sha1_hash_data = SHA1.hexdigest()
                hash_dict[zippedfile] = sha1_hash_data
            except:
                Client_GlobalData.skipped_files.append(os.path.normpath(file_name)\
                                                       + "|Error on SHA1 of file")
        zip_handle.close()
        if len(hash_dict) > 0:
            if len(hash_dict) == 1:
                fileHASHListSingle.append(hash_dict.values()[0])
                fileHASHNameListSingle.append(os.path.normpath(file_name))
            else:
                fileHASHList.append(hash_dict)
            return hash_dict
        return None
    elif file_name.endswith('7z'):
        try:
            file_handle = open(file_name, 'rb')
            archive = Archive7z(file_handle)
            filenames = archive.getnames()
            hash_dict = {}
            for filename in filenames:
                cf = archive.getmember(filename)
                try:
                    # calculate sha1 hash
                    SHA1 = hashlib.sha1()  # "reset" the sha1 to blank
                    SHA1.update(cf.read())
                    sha1_hash_data = SHA1.hexdigest()
                    hash_dict[filename] = sha1_hash_data
                except:
                    Client_GlobalData.skipped_files.append(os.path.normpath(file_name)\
                                                           + "|Error on SHA1 of file")
            file_handle.close()
            if len(hash_dict) > 0:
                if len(hash_dict) == 1:
                    fileHASHListSingle.append(hash_dict.values()[0])
                    fileHASHNameListSingle.append(os.path.normpath(file_name))
                else:
                    fileHASHList.append(hash_dict)
                    fileHASHNameList.append(os.path.normpath(file_name))
                return hash_dict
        except:
            Client_GlobalData.skipped_files.append(os.path.normpath(file_name)
                                                   + "|Error reading 7z")
        return None
    else:
        sha1_hash_data = None
        file_pointer = open(file_name, 'rb')
        # read in chunks to lower memory requirement
        try:
            SHA1 = hashlib.sha1()  # "reset" the sha1 to blank
            for chunk in iter(lambda: file_pointer.read(128 * SHA1.block_size), ''):
                SHA1.update(chunk)
                sha1_hash_data = SHA1.hexdigest()
        except:
            logging.error("hash sha1 fail: %s", file_name)
        file_pointer.close()
        return sha1_hash_data


def com_hash_sha1_c(file_name):
    """
    c call for sha1 hash generation by file name
    """
    num = 0
    while 1:
        zip_handle = zipfile.ZipFile(file_name, 'r')  # issues if u do RB
        for zippedfile in zip_handle.namelist():
            # calculate sha1 hash
#            SHA1.update(zip_handle.read(zippedfile))
            zip_file_data = zip_handle.read(zippedfile)
            R = inline(common_hash_c_code.COM_C_CODE, ['zip_file_data'],
                support_code=common_hash_c_code.COM_SHA1_CODE)
        num += 1
        if num > 5:
            break


def com_hash_crc32(file_name):
    """
    Caclucate crc32 for file
    """
    file_pointer = open(file_name, 'rb')
    CRC = zlib.crc32(file_pointer.read(1024*1024))
    while True:
        data = file_pointer.read(1024*1024)
        if len(data) == 0:
            break #Finished reading file
        CRC = zlib.crc32(data, CRC)
    file_pointer.close()
    return CRC


# http://www.radicand.org/blog/orz/2010/2/21/edonkey2000-hash-in-python/
def com_hash_ed2k(filepath):
    """
    Returns the ed2k hash of a given file.
    """
    md4 = hashlib.new('md4').copy
    def gen(f):
        while True:
            x = f.read(9728000)
            if x:
                yield x
            else:
                return

    def md4_hash(data):
        """
        Calc hash
        """
        m_hash = md4()
        m_hash.update(data)
        return m_hash

    with open(filepath, 'rb') as file_handle:
        a = gen(file_handle)
        hashes = [md4_hash(data).digest() for data in a]
        if len(hashes) == 1:
            return hashes[0].encode("hex")
        else:
            return md4_hash(reduce(lambda a, d: a + d, hashes, "")).hexdigest()


def com_hash_thesubdb(file_name):
    """
    Hash for thesubdb
    """
    readsize = 64 * 1024
    with open(file_name, 'rb') as file_handle:
        # size = os.path.getsize(file_name)
        data = file_handle.read(readsize)
        file_handle.seek(-readsize, os.SEEK_END)
        data += file_handle.read(readsize)
    return hashlib.md5(data).hexdigest()


def com_hash_opensubtitles(file_name):
    """
    hash for opensubtiles.org
    folling routine is provided by opensubtitles.org website for api calls
    """
    try:
        longlongformat = '<q' # little-endian long long
        bytesize = struct.calcsize(longlongformat)
        file_handle = open(file_name, "rb")
        filesize = os.path.getsize(file_name)
        hash = filesize
        if filesize < 65536 * 2:
            return "SizeError"
        for ndx in range(65536 / bytesize): # pylint: disable=W0612
            buffer = file_handle.read(bytesize)
            (l_value,) = struct.unpack(longlongformat, buffer)
            hash += l_value
            hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number
        file_handle.seek(max(0, filesize - 65536), 0)
        for ndx in range(65536 / bytesize): # pylint: disable=W0612
            buffer = file_handle.read(bytesize)
            (l_value,) = struct.unpack(longlongformat, buffer)
            hash += l_value
            hash = hash & 0xFFFFFFFFFFFFFFFF
        file_handle.close()
        returnedhash = "%016x" % hash
        return returnedhash
    except IOError:
        return "IOError"
