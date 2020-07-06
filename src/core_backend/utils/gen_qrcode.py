#!/usr/bin/env python
# -*- coding: utf-8 -*-

import qrcode

def gen_qrcode(data, filepath, size=5, box_size=16, border=2):
    '''
    @data:
    @filepath:
    @size: 1~40
    @box_size:
    @border:
    '''
    qr = qrcode.QRCode(
        version=size,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image()
    img.save(filepath)


if __name__ == '__main__':
    data = 'CRM2348723989'
    filepath = './test_qrcode.png'

    gen_qrcode(data, filepath)
