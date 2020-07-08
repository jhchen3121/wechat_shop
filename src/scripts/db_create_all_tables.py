#!/usr/bin/python
# -*- coding: utf-8 -*-

import settings
from server.domain.models import *
from core_backend.database import con, connect
from sqlalchemy import create_engine
from core_backend.database.base import DomainBase

if __name__ == "__main__":
    print settings.DB_URL
    engine = create_engine(settings.DB_URL)
    DomainBase.metadata.create_all(engine)
