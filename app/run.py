#!/usr/bin/env python3
# encoding: utf-8

import sys
from QRCodeConverter import QRCodeConverter

def parseArgv():
    if len(sys.argv) < 3:
        print("Incorrect args, try:")
        print('./generate.py ./logo.png "http://github.com"')
        sys.exit(0)

    img_path = sys.argv[1]
    content = sys.argv[2]

    return {'img_path': img_path, 'content': content}

def handle():
    def successCallback(data):
        pass

    def failureCallback():
        pass

    parser = parseArgv()
    converter = QRCodeConverter()
    converter.set_inner_img_path(parser['img_path'])
    converter.set_qrcode_content(parser['content'])
    converter.process(successCallback, failureCallback)

if __name__ == '__main__':
    handle()
