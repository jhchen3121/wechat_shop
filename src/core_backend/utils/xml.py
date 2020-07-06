#!/usr/bin/env python
# -*- coding: utf-8 -*-

#from __future__ import unicode_literals
from __future__ import absolute_import

from lxml import objectify

def xml2dict(xml_str):
    """ Convert xml to dict, using lxml v3.4.2 xml processing library, see http://lxml.de/ """
    def xml_to_dict_recursion(xml_object):
        if isinstance(xml_object, objectify.StringElement):
            return {xml_object.tag: xml_object.text}

        if isinstance(xml_object, objectify.ObjectifiedElement):
            return {xml_object.tag: [xml_to_dict_recursion(child) for child in xml_object.getchildren()]}

    xml_obj = objectify.fromstring(xml_str)

    return xml_to_dict_recursion(xml_obj)
