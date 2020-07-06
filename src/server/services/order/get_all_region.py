#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

from core_backend import context
from core_backend.service import handler
from core_backend.libs import token as tk
from core_backend.libs.exception import Error
from server.domain.models import WechatshopRegion

import logging
import settings

logger = logging.getLogger(__name__)

class Handler(handler.handler):
    """  """

    def dispatch(self, session):
        req_body = self.context.request.body
        resp_body = self.context.response.body

        a_data = session.query(WechatshopRegion).filter(WechatshopRegion.type == 1).all()
        b_data = session.query(WechatshopRegion).filter(WechatshopRegion.type == 2).all()
        c_data = session.query(WechatshopRegion).filter(WechatshopRegion.type == 3).all()

        a_data = [a.to_dict() for a in a_data]
        b_data = [b.to_dict() for b in b_data]
        c_data = [c.to_dict() for c in c_data]

        new_data = []
        for item in a_data:
            children = []
            for bitem in b_data:
                inner_children = []
                for citem in c_data:
                    if citem['parent_id'] == bitem['id']:
                        inner_children.append(dict(
                            value=citem['id'],
                            label=citem['name']
                        ))
                if bitem['parent_id'] == item['id']:
                    children.append(dict(
                        value=bitem['id'],
                        label=bitem['name'],
                        children=inner_children
                    ))
            new_data.append(dict(
                value=item['id'],
                label=item['name'],
                children=children
            ))

        resp_body.data = new_data

