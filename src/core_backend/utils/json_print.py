#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

import json
from core_backend.utils.json import CustomerEncoder
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

def json_pretty_print(j_obj):
    json_str = json.dumps(j_obj, cls=CustomerEncoder, indent=4, ensure_ascii=False, encoding="utf8")
    print(highlight(json_str, JsonLexer(), TerminalFormatter()).encode("utf8"))
