#!/usr/bin/env python3
# encoding: utf-8

from io import StringIO
import urllib
import qrcode
import random
from PIL import Image
from app.util import Util
from app.log import Logger

class QRCodeConverter:
    def __init__(self):
        """
        Create QRCodeConverter instance which initial some kind of variable,
        such as: log/qrcode box size/qrcode border and also the output
        image name
        """
        self.util = Util()
        self.log = Logger()
        self.box_size = 10
        self.border = 4
        self.qrcode_img_name_prefix = "qrcode"
        self.qrcode_img_name_surffix = ".png"

    def set_inner_img_path(self, path):
        """
        Set inner image file path, it could be URL or locally file system path
        of the image file
        """
        self.inner_img_path = path

    def set_qrcode_content(self, content):
        """
        The text content for generate qrcode image
        """
        self.content = content

    def set_qrcode_size(self, size):
        """
        Restrict the size of the qrcode image, the parameter size should be
        a tuple: (width, height). This size will used in PIL.Image package
        """
        self.size = size

    def process(self):
        """
        Generate qrcode image by specific parameter, save it in
        currently folder.
        Function return a filename of qrcode image
        """
        im = self.__make_qrcode_img(self.content).convert('RGBA')

        try:
            inner_img_file = self.__fetch_file(self.inner_img_path)
            inner_img = Image.open(inner_img_file.getvalue()).convert('RGBA')

            box = self.__inner_img_position(im, inner_img)

            im.paste(inner_img, box, inner_img)

            try:
                size = self.__get_qrcode_size()
                self.log.debug('Get width and height for qrcode image')
                self.log.debug('Set thumbnail for qrcode with size: (%d, %d)'
                               % (size[0], size[1]))
                im = im.resize(size)
            except AssertionError as assert_error:
                self.log.warn('Cannot get width/height for resizing qrcode image')
        except Exception as e:
            self.log.warn('Cannot fetch inner image with path: %s'
                          % (self.inner_img_path))
            self.log.warn(e)

        outputname = self.__output_name()
        im.save(outputname)

        self.log.debug("success to process, generated qrcode file: "
                       + outputname)
        return outputname

    def __get_qrcode_size(self):
        """
        Return the size of the qrcode which was set in the function:
        set_qrcode_size
        """
        assert self.size
        assert isinstance(self.size, tuple)
        assert len(self.size) == 2
        assert self.size[0]
        assert self.size[1]

        res_val = max(self.size[0], self.size[1])
        return (res_val, res_val)

    def __fetch_file(self, path):
        """
        Load image file by parameter path, the path could be URL or
        locally file system path.
        This function will return a StringIO object
        """
        import os
        if path.startswith('http'):
            f = StringIO(urllib.urlopen(path).read())
        else:
            assert os.path.isfile(path)
            f = StringIO(path)
        return f

    def __make_qrcode_img(self, content):
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

    def __output_name(self):
        fname = self.qrcode_img_name_prefix
        fname += str(self.util.now())
        fname += str(int(random.random()*100000))
        fname += self.qrcode_img_name_surffix

        return fname

    def __inner_img_position(self, outer_img, inner_img):
        (width, height) = inner_img.size

        dim = height if width <= height else width

        x = (outer_img.size[0] - width) / 2.0
        y = (outer_img.size[1] - dim) / 2.0
        return (int(x), int(y))
