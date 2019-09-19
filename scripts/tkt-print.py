#!/usr/bin/env python3

import os
import sys
import cups
import time
import tempfile
from PIL import Image, ImageFont, ImageDraw

KEEP_IMG = True
LABEL_WIDTH = 6744
LABEL_HEIGHT = 1872

FONT_TEXT = 'IBMPlexMono-Medium.ttf'
PRINTER_NAME = 'DYMO-LabelWriter-450'

LINE1 = 'name'
LINE2 = 'nick'
LINE3 = 'Cyber Saiyan'

def _get_resource(filename):
    return os.path.join(os.path.dirname(sys.argv[0]), filename)

def build_label(w, h, line3, line1, line2, font_text=FONT_TEXT):
    fontcs = ImageFont.truetype(_get_resource(font_text), 800)
    fontname = ImageFont.truetype(_get_resource(font_text), 500)
    fontjob = ImageFont.truetype(_get_resource(font_text), 500)
    image = Image.new('RGB', (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    wnorm3, hnorm3 = draw.textsize(line3, font=fontcs)
    wnorm1, hnorm1 = draw.textsize(line1, font=fontname)
    wnorm2, hnorm2 = draw.textsize(line2, font=fontjob)
    draw.text(((w-wnorm1)/2, -670+(h-hnorm1)/2), line1, (0, 0, 0), font=fontname)
    draw.text(((w-wnorm2)/2, -220+(h-hnorm2)/2), line2, (0, 0, 0), font=fontjob)
    draw.text(((w-wnorm3)/2, 425+(h-hnorm3)/2), line3, (0, 0, 0), font=fontcs)
    if not KEEP_IMG:
        tmpfile = tempfile.NamedTemporaryFile(prefix='eventman_print_label_', suffix='.png')
    else:
        tmpfile = tempfile.mktemp(prefix='eventman_print_label_', suffix='.png')
        tmpfile = open(tmpfile, 'wb')
    image.save(tmpfile, dpi=[600, 300], format='png')
    print ('print_label label image saved to %s' % tmpfile.name)
    return tmpfile

def print_label(label_file, name):
    printerName = PRINTER_NAME
    conn = cups.Connection()
    printer = printerName or conn.getDefault()
    print ('print_label connection done')
    conn.printFile(printer, label_file.name, name, {})
    print ('print_label print job sent')

print ('Start printing...')
print ('Make label')
label_file = build_label(LABEL_WIDTH, LABEL_HEIGHT, LINE3, LINE1, LINE2)
print ('Print label')
print_label(label_file, LINE1)
print ('Done')
