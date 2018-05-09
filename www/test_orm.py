#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r'''
    # 编写数据访问代码，测试对象操作对象

'''
__author__ = 'Cowry Golden'

# 导入依赖
import orm
from models import User, Blog, Comment
import asyncio

# 比如，对于User对象
# @asyncio.coroutine
# def testUser():
#     yield from orm.create_pool(loop=loop, user='www-data', password='www-data', db='awesome')
#     u  = User(name='Test', email='test@example.com', passwd='1234567890', image='about:blank')
#     yield from u.save()
#     yield from orm.destory_pool()

async def testUser():
    await orm.create_pool(loop=loop, user='www-data', password='www-data', db='awesome')
    u  = User(name='Test', email='test@example.com', passwd='1234567890', image='about:blank')
    try:
        await u.save()
    except BaseException as e:
        pass
    for rs in await u.findAll():
        print(rs)
    await orm.destory_pool()

# 获取EventLoop:
loop = asyncio.get_event_loop()
#把协程丢到EventLoop中执行
loop.run_until_complete(testUser())
#关闭EventLoop
loop.close()

# for x in testUser():
#     pass
