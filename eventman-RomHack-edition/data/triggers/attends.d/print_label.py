#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""print_label.py - print a label with the name, the company and the seq_hex key (in a barcode) of an attendee

Copyright 2015-2017 Emiliano Mattioli <oloturia AT gmail.com>
                    Davide Alberani <da@erlug.linux.it>
                    RaspiBO <info@raspibo.org>

Licensed under the Apache License 2.0
"""

import os
import sys
import cups
import time
import tempfile
from PIL import Image, ImageFont, ImageDraw

KEEP_IMG = True
LABEL_WIDTH = 6744
LABEL_HEIGHT = 1872

#FONT_TEXT = 'CONCIBB_.TTF'
#FONT_TEXT = 'Ubuntu-C.ttf'
FONT_TEXT = 'DejaVuSansCondensed.ttf'
FONT_BARCODE = 'free3of9.ttf'

PRINTER_NAME = None
PRINTER_NAME = 'DYMO-LabelWriter-450'

# Dictionary of remote systems used to print labels.
# 'remote1' is the name used by that system to login on the web GUI.
# '192.168.99.129' is the IP of the remote host. If not set, the origin of the request is used.
# 'DYMO-LabelWriter-450' is the name of the printer on the remote system.
REMOTES = {
        'romhack01': {
            'printer': 'Printer-01'
        },
        'romhack02': {
            'printer': 'Printer-02'
        }
}


def debug(msg):
    print('%s: %s' % (time.time(), msg))


def _get_resource(filename):
    return os.path.join(os.path.dirname(sys.argv[0]), filename)


def build_label(w, h, barcode_text, line1, line2, font_text=FONT_TEXT, font_barcode=FONT_BARCODE):
    barcode_text = "*" + barcode_text + "*"
    #fontbar = ImageFont.truetype(_get_resource(font_barcode), 1000)
    fontcs = ImageFont.truetype(_get_resource(font_text), 1000)
    fontname = ImageFont.truetype(_get_resource(font_text), 520)
    fontjob = ImageFont.truetype(_get_resource(font_text), 360)
    image = Image.new('RGB', (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    #wbar, hbar = draw.textsize(barcode_text, font=fontbar)
    wnorm3, hnorm3 = draw.textsize("Cyber Saiyan", font=fontcs)
    wnorm1, hnorm1 = draw.textsize(line1, font=fontname)
    wnorm2, hnorm2 = draw.textsize(line2, font=fontjob)
    draw.text(((w-wnorm1)/2, -670+(h-hnorm1)/2), line1, (0, 0, 0), font=fontname)
    draw.text(((w-wnorm2)/2, -220+(h-hnorm2)/2), line2, (0, 0, 0), font=fontjob)
    #draw.text(((w-wbar)/2, 425+(h-hbar)/2), barcode_text, (0, 0, 0), font=fontbar)
    draw.text(((w-wnorm3)/2, 425+(h-hnorm3)/2), "Cyber Saiyan", (0, 0, 0), font=fontcs)
    if not KEEP_IMG:
        tmpfile = tempfile.NamedTemporaryFile(prefix='eventman_print_label_', suffix='.png')
    else:
        tmpfile = tempfile.mktemp(prefix='eventman_print_label_', suffix='.png')
        tmpfile = open(tmpfile, 'wb')
    image.save(tmpfile, dpi=[600, 300], format='png')
    debug('print_label label image saved to %s' % tmpfile.name)
    return tmpfile


def print_label(label_file, name):
    printerName = PRINTER_NAME
    if os.environ.get('WEB_USER') in REMOTES:
        settings = REMOTES[os.environ['WEB_USER']]
        if 'host' not in settings:
            settings['host'] = os.environ.get('WEB_REMOTE_IP')
        if settings['host'] == '::1':
            settings['host'] = '127.0.0.1'
        if 'username' in settings: cups.setUser(settings['username'])
        debug('connecting to remote cups %s' % settings['host'])
        cups.setServer(settings['host'])
        conn = cups.Connection(settings['host'])
        if 'printer' in settings:
            printerName = settings['printer']
    else:
        conn = cups.Connection()
    printer = printerName or conn.getDefault()
    debug('print_label connection done')
    conn.printFile(printer, label_file.name, name, {})
    debug('print_label print job sent')


def run():
    debug('print_label start')
    # Always consume stdin.
    sys.stdin.read()
    name = os.environb.get(b'NAME') or b''
    surname = os.environb.get(b'SURNAME') or b''
    fullname = name + b' ' + surname
    fullname = fullname.decode('utf-8')
    company = os.environb.get(b'COMPANY') or b''
    company = company.decode('utf-8')
    # Print the decimal value SEQ as an hex of at least 6 digits.
    seq = os.environ.get('SEQ_HEX', '0')
    label_file = build_label(LABEL_WIDTH, LABEL_HEIGHT, seq, fullname, company)
    print_label(label_file, fullname)
    debug('print_label completed')


if __name__ == '__main__':
    try:
        run()
    except Exception as e:
        sys.stderr.write('print_label.  Exception raised: %s\n' % str(e))

