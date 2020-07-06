#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

import logging
import logging.config
import settings
import os

logger_conf = os.path.join(settings.PROJ_DIR, 'etc', 'frontend_logger.conf')
logging.config.fileConfig(logger_conf)

from core_backend import server as Server
from core_backend import websocket
from core_backend.module import load_modules_hook
import  core_backend.http

import tornado.web

logger = logging.getLogger(__name__)

def _start_frontend():
    handlers = []
    hooks = load_modules_hook()

    for hook, pkg in hooks:
        handlers_hook = getattr(hook, 'handlers')

        if handlers_hook:
            handlers_list = handlers_hook()
            for hdl in handlers_list:
                logger.info("add url handler %s by [%s]", hdl[0], pkg) 
                handlers.append(hdl)

    handlers.extend([
        (r'/service/(.*)', Server.ServiceHandler),
        (r'/mp_service/(.*)', Server.MpServiceHandler),
        (r'/attachment', Server.AttachmentHandler),
        (r'/static_source/(.*)', Server.StaticSourceHandler),
        (r'/file_export', Server.FileExportHandler),
        (r'/bms', websocket.MessageHandler),
        # admin静态资源文件
        (r"/(.*)", core_backend.http.StaticFileHandler, {"path": "../web/dist/web", "default_filename": "index.html"})
        ])
    pika_client = Server.PikaClient()
    pika_consumer = websocket.PikaConsumer()
    # 上传至静态资源文件夹
    upload_path = settings.STATIC_SOURCE_DIR
    application = tornado.web.Application(handlers, 
                    pika_client = pika_client,
                    pika_consumer = pika_consumer,
                    upload_path = upload_path,
                    )

    port = settings.FRONT_SRV_PORT

    print "Tornado is serving on port {0}.".format(port)
    sockets = tornado.netutil.bind_sockets(port)
    server = tornado.httpserver.HTTPServer(application)
    server.add_sockets(sockets)

    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.spawn_callback(pika_client.connect)
    ioloop.spawn_callback(pika_consumer.connect)
    try:
        ioloop.start()
    except KeyboardInterrupt:
        print "Front Server Exit!"


if __name__ == "__main__":
    _start_frontend()
