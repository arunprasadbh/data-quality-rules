# -*- coding: utf-8 -*-

# THIS SCRIPT MIGHT TAKE A WHILE
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv

import zipfile
import os
from os.path import isfile, join, exists
from datetime import datetime, timedelta
from urllib.request import urlopen
import requests
import io
import shutil
from pathlib import Path
from tqdm import tqdm
from sys import platform as _platform
import re

# variables
url = 'https://www.dnb.nl/binaries/'

path_zipfiles = join('downloaded files')

name_zipfile_taxo = join('FTK Taxonomy 2.1.0_tcm46-386386.zip')
path_zipfile_taxo = join('taxonomy', 'arelle', 'cache', 'http')
extension_taxo = join('Taxonomy')

name_zipfile_inst = join('FTK Sample Intances 2.1.0_tcm46-386385.zip')
path_zipfile_inst = join('.', 'instances')

def main():
    logger = logging.getLogger(__name__)

    logger.info("Platform %s", str(_platform))

    logger.info("Extracting example instance files from %s", url)
    extract(url, name_zipfile_inst, path_zipfiles)

    logger.info("Moving example instance files to %s", path_zipfile_inst)
    move_files(path_zipfiles, path_zipfile_inst, '\.XBRL')

    logger.info("Extracting taxonomy from %s", url)
    extract(url, name_zipfile_taxo, path_zipfiles)

    logger.info("Moving taxonomy files to %s", path_zipfile_taxo)
    move_files(join(path_zipfiles, extension_taxo), path_zipfile_taxo)

    logger.info("Cleaning up files in %s", path_zipfiles)
    shutil.rmtree(winapi_path(join(path_zipfiles, 'Taxonomy')))

    logger.info("Thank you for waiting!")

# Needed for long paths
class ZipfileLongPaths(zipfile.ZipFile):
    def _extract_member(self, member, targetpath, pwd):
        targetpath = winapi_path(targetpath)
        return zipfile.ZipFile._extract_member(self, member, targetpath, pwd)

# Needed for long paths
def winapi_path(dos_path, encoding=None):
    if (_platform == 'win32') or (_platform == 'win64'):
        path = os.path.abspath(dos_path)
        if path.startswith("\\\\"):
            path = "\\\\?\\UNC\\" + path[2:]
        else:
            path = "\\\\?\\" + path
        return path
    else:
        return dos_path

def make_path(path_zipfile):
    logger = logging.getLogger(__name__)
    if not os.path.exists(path_zipfile):
        logger.info('Making directory %s' % path_zipfile)
        os.makedirs(path_zipfile)

# Extract files
def extract(url_inst, name_zipfile, path_zipfile):
    logger = logging.getLogger(__name__)
    if os.path.isfile(join(path_zipfile, name_zipfile)):
        logger.info('Zip file %s exists, using this one' % str(name_zipfile))
        z = ZipfileLongPaths(join(path_zipfile, name_zipfile))
    else:
        logger.info('Zip file %s does not exists, downloading from Internet' % str(name_zipfile))
        r = requests.get(url_inst + name_zipfile)
        output = open(join(path_zipfile, name_zipfile), "wb")
        output.write(r.content)
        output.close()
        z = ZipfileLongPaths(io.BytesIO(r.content))
    for file in tqdm(iterable=z.namelist(), total=len(z.namelist())):
        try:
            z.extract(member=file, path=path_zipfile)
        except:
            logger.info('Cannot extract %s' % str(file))
    z.close()

# Move files examples
def move_files(source, dest1, file_ext = None):
    files = os.listdir(source)
    for f in files:
        if file_ext:
            if not re.search(file_ext,f):
                continue
        if not os.path.exists(join(dest1, f)):
            shutil.move(join(source, f), dest1)

if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()