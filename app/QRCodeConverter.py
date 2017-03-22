#!/usr/bin/env python3
# encoding: utf-8

import cStringIO
import urllib
import qrcode
import random
from PIL import Image
from util import Util
from log import Logger

class QRCodeConverter:
    def __init__(self):
        self.util = Util()
        self.log = Logger()
        self.box_size = 10
        self.border = 4
        self.qrcode_img_name_prefix = "qrcode"
        self.qrcode_img_name_surffix = ".png"

    def set_inner_img_path(self, path):
       self.inner_img_path = path

    def set_qrcode_content(self, content):
       self.content = content

    def set_qrcode_size(self, size):
        self.size = size

    def get_qrcode_size(self):
        assert self.size
        assert isinstance(self.size, tuple)
        assert len(self.size) == 2
        assert self.size[0]
        assert self.size[1]

        res_val = max(self.size[0], self.size[1])
        return (res_val, res_val)

    def fetch_file(self, path):
        import os
        if path.startswith('http'):
            f = cStringIO.StringIO(urllib.urlopen(path).read())
        else:
            assert os.path.isfile(path)
            f = cStringIO.StringIO(path)
        return f

    def make_qrcode_img(self, content):
        qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=self.box_size,
                border=self.border,
        )
        qr.add_data(content)
        qr.make(fit=True)

        img = qr.make_image()
        return img

    def process(self):
        im = self.make_qrcode_img(self.content).convert('RGBA')
        outputname = self.qrcode_img_name_prefix + str(self.util.now()) + str(int(random.random()*100000)) + self.qrcode_img_name_surffix

        try:
            inner_img_file = self.fetch_file(self.inner_img_path)
            inner_img = Image.open(inner_img_file.read()).convert('RGBA')

            (width, height) = inner_img.size

            dim = height if width <= height else width

            xTrans = (im.size[0] - width) / 2.0
            yTrans = (im.size[1] - dim) / 2.0

            im.paste(inner_img, (int(xTrans), int(yTrans)), inner_img)

            try:
                (img_width, img_height) = self.get_qrcode_size()
                self.log.debug('Get width and height for qrcode image')
                self.log.debug('Set thumbnail for qrcode with size: (%d, %d)' % (img_width, img_height))
                im = im.resize(self.size)
            except Exception as resize_exception:
                self.log.debug('Cannot get suitable width and height for qrcode image, do nothing')
                self.log.warn(resize_exception)
        except Exception as e:
            self.log.warn('Cannot fetch inner image with path: %s' %(self.inner_img_path))
            self.log.warn(e)

        im.save(outputname)

        self.qrcode_path = outputname
        self.log.debug("success to process, generated qrcode file: " + outputname)
        return self.qrcode_path
