#!/usr/bin/python
# -*- coding: utf-8 -*-

import settings
from domain.models import *
from core_backend.database import con, connect

if __name__ == "__main__":
    print settings.DB_URL
    connect(settings.DB_URL)
    print settings.DB_URL
    con.metadata.create_all()
