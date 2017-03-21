#!/usr/bin/env python3
# encoding: utf-8

import pyqrcode
from lxml import etree
import math
import sys
import cairosvg

from util import Util
from log import Logger

class QRCodeConverter:
    def __init__(self):
        self.util = Util()
        self.log = Logger()
        self.block_size = 8
        self.circle_radius = self.block_size * 5
        self.qrcode_img_name_prefix = "qrcode"
        self.qrcode_img_name_surffix = ".png"

    def set_inner_img_path(self, path):
       self.inner_img_path = path

    def set_qrcode_content(self, content):
       self.content = content

    def get_size_of_img(self, fname):
        '''Determine the image type of fhandle and return its size.
        from draco'''
        import struct
        import imghdr

        with open(fname, 'rb') as fhandle:
            head = fhandle.read(24)
            if len(head) != 24:
                return
            if imghdr.what(fname) == 'png':
                check = struct.unpack('>i', head[4:8])[0]
                if check != 0x0d0a1a0a:
                    return
                width, height = struct.unpack('>ii', head[16:24])
            elif imghdr.what(fname) == 'gif':
                width, height = struct.unpack('<HH', head[6:10])
            elif imghdr.what(fname) == 'jpeg':
                try:
                    fhandle.seek(0) # Read 0xff next
                    size = 2
                    ftype = 0
                    while not 0xc0 <= ftype <= 0xcf:
                        fhandle.seek(size, 1)
                        byte = fhandle.read(1)
                        while ord(byte) == 0xff:
                            byte = fhandle.read(1)
                        ftype = ord(byte)
                        size = struct.unpack('>H', fhandle.read(2))[0] - 2
                    # We are at a SOFn block
                    fhandle.seek(1, 1)  # Skip `precision' byte.
                    height, width = struct.unpack('>HH', fhandle.read(4))
                except Exception: #IGNORE:W0703
                    return
            else:
                return
            return width, height

    def render_to_png(self, svgnode=None, pngfilename=None, dpi=72, **kwargs):
        import cairosvg
        return cairosvg.svg2png(bytestring=svgnode, write_to=pngfilename, dpi=dpi)

    def process(self, successCallback, failureCallback):
        im = self.generateQRImageFromContent(self.content)
        imageSize = str(im.size[0] * self.block_size)

        # create an SVG XML element (see the SVG specification for attribute details)
        doc = etree.Element('svg', width=imageSize, height=imageSize, version='1.1', xmlns='http://www.w3.org/2000/svg')
        pix = im.load()
        center = im.size[0] * self.block_size / 2

        for xPos in range(0,im.size[0]):
            for yPos in range(0, im.size[1]):
                color = pix[xPos, yPos]
                if color == (0,0,0,255):
                    withinBounds = not self.touchesBounds(center, xPos, yPos, self.circle_radius, self.block_size)
                    if (withinBounds):
                        etree.SubElement(doc, 'rect', x=str(xPos*self.block_size), y=str(yPos*self.block_size), width='10', height='10', fill='black')

        inner_img = self.inner_img_path
        (width, height) = self.get_size_of_img(self.inner_img_path)

        import pdb
        pdb.set_trace()
        dim = height
        if (width > dim):
            dim = width
        scale = self.circle_radius * 2.0 / width

        xTrans = ((im.size[0] * self.block_size) - (width * scale)) / 2.0
        yTrans = ((im.size[1] * self.block_size) - (height * scale)) / 2.0

        img_node_attr = {
            'x': str(xTrans),
            'y': str(yTrans),
            'width': str(width),
            'height': str(dim),
            'href': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg=='
        }
        inner_img_scale_container = etree.SubElement(doc, 'image',  attrib=img_node_attr)

        # ElementTree 1.2 doesn't write the SVG file header errata, so do that manually
        svg_node = """<?xml version=\"1.0\" standalone=\"no\"?>\n
        <!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\"\n
        \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">\n
        """
        svg_node += etree.tostring(doc).decode('utf-8')

        outputname = self.qrcode_img_name_prefix + str(self.util.now()) + self.qrcode_img_name_surffix
        self.render_to_png(svg_node, outputname)

        f = open('out.svg', 'w')
        f.write(svg_node)
        f.close()
        
        self.log.info("success to process, now call successCallback, qrcode file: " + outputname)
        successCallback(self)

    def distance(self, p0, p1):
        return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

    def generateQRImageFromContent(self, content):
        qr_image = pyqrcode.MakeQRImage(content, errorCorrectLevel = pyqrcode.QRErrorCorrectLevel.H, block_in_pixels = 1, border_in_blocks=0)
        return qr_image

    def getSVGFileContent(self, filename):
        '''
        root may be the svg element itself, so search from tree

        solution for multiple (or no) namespaces from
        http://stackoverflow.com/a/14552559/493161
        '''
        document = etree.parse(filename)
        self.log.debug('document: %s' %document)
        svg = document.xpath('//*[local-name()="svg"]')[0]
        self.log.debug('svg: %s' %svg)
        return svg

    def touchesBounds(self, center, x, y, radius, block_size):
        scaled_center = center / block_size
        dis = self.distance((scaled_center , scaled_center), (x, y))
        rad = radius / block_size
        return dis <= rad + 1	

