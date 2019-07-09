#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""romhack_checkin

Based on the original file qrcode_reader.py
https://github.com/raspibo/eventman/blob/master/tools/qrcode_reader.py

Modified by Giovanni merlos Mellini for RomHack www.romhack.io

Copyright 2017 Davide Alberani <da@erlug.linux.it>
               RaspiBO <info@raspibo.org>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import io
import sys
import time
import json
import urllib
import logging
import argparse
import datetime
import requests
import configparser
from requests.packages.urllib3.exceptions import InsecureRequestWarning

TIMEOUT = 3

logger = logging.getLogger('romhack_checkin')
logging.basicConfig(level=logging.INFO)
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def convert_obj(obj):
    try:
        return int(obj)
    except:
        pass
    if isinstance(obj, str):
        obj_l = obj.lower()
        if obj_l in ['true', 'on', 'yes']:
            return True
        elif obj_l in ['false', 'off', 'no']:
            return False
        elif obj == '%NOW%':
            return str(datetime.datetime.utcnow())
    return obj


def convert(seq):
    if isinstance(seq, dict):
        d = {}
        for key, item in seq.items():
            d[key] = convert(item)
        return d
    if isinstance(seq, (list, tuple)):
        return [convert(x) for x in seq]
    return convert_obj(seq)


class ImprovedEncoder(json.JSONEncoder):
    """Enhance the default JSON encoder to serialize datetime instances."""
    def default(self, o):
        if isinstance(o, (datetime.datetime, datetime.date,
                datetime.time, datetime.timedelta)):
            try:
                return str(o)
            except Exception:
                pass
        elif isinstance(o, set):
            return list(o)
        return json.JSONEncoder.default(self, o)

# Inject our class as the default encoder.
json._default_encoder = ImprovedEncoder()


class Connector():
    def __init__(self, cfg):
        self.cfg = cfg
        self.session = None
        self.url = cfg['eventman']['url']
        self.login_url = urllib.parse.urljoin(self.url, '/v1.0/login')
        self.checkin_url = urllib.parse.urljoin(self.url, os.path.join('/v1.0/events/',
                                                cfg['event']['id'], 'tickets/'))
        self.login()

    def login(self):
        logger.debug('connecting to eventman at %s' % self.login_url)
        self.session = requests.Session()
        self.session.verify = False
        ca = cfg['eventman'].get('ca')
        if ca and os.path.isfile(ca):
            self.session.verify = ca
        username = cfg['eventman'].get('username')
        password = cfg['eventman'].get('password')
        params = {}
        if username:
            params['username'] = username
        if password:
            params['password'] = password
        req = self.session.post(self.login_url, json=params, timeout=TIMEOUT)
        req.raise_for_status()
        req.connection.close()
        logger.info('connection to eventman at %s established' % self.login_url)

    def checkin(self, code):
        msg = 'scanning code %s: ' % code
        limit_field = None
        try:
            limit_field = self.cfg['event'].getint('limit_field')
        except:
            pass
        if limit_field:
            code = code[:limit_field]
        _searchFor = '%s:%s' % (cfg['event']['field'], code)
        params = {cfg['event']['field']: code, '_errorMessage': 'code: %s' % code, '_searchFor': _searchFor}
        checkin_url = self.checkin_url + '?' + urllib.parse.urlencode(params)
        json = convert(dict(self.cfg['actions']))
        req = self.session.put(checkin_url, json=json, timeout=TIMEOUT)
        error = False
        try:
            req.raise_for_status()
            msg += 'ok'
        except requests.exceptions.HTTPError:
            error = True
            msg += 'error: %s' % req.json().get('message')
        if not error:
            logger.info(msg)
        else:
            logger.warning(msg)
        req.connection.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--code', help='specify a single code', action='store')
    parser.add_argument('--config', help='user a different configuration file (default: romhack_checkin.ini)',
                        action='store', default='romhack_checkin.ini')
    args = parser.parse_args()

    cfg = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    cfg.read(args.config)
    if cfg['romhack_checkin'].getboolean('debug'):
        logger.setLevel(logging.DEBUG)
    try:
        connector = Connector(cfg)
    except Exception as ex:
        logger.error('unable to connect to %s: %s' % (cfg['eventman']['url'], ex))
        sys.exit(1)
    if args.code:
        connector.checkin(args.code)
    else:
        while True:
            try:
                qrcode = input("\nInput QR code: ")
                connector.checkin(qrcode)
            except:
                logger.error('Cannot loop to read QR codes')
                sys.exit(1)
