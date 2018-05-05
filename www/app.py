#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r'''
    # 由于我们的Web App建立在asyncio的基础上，因此用aiohttp写一个基本的app.py来测试Web框架的可用性

'''
__author__ = 'Cowry Golden'

# 导入依赖
import logging; logging.basicConfig(level=logging.INFO)

import asyncio, os, json, time
from datetime import datetime

from aiohttp import web

def index(request):
    return web.Response(body='<h1>Awesome</h1>'.encode('utf-8'), content_type='text/html')

@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', index)
    srv = yield from loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info('Server started at http://127.0.0.1:9000 ...')
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()