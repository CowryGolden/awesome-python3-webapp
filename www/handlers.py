#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r'''
    # url handlers：url处理器

'''
__author__ = 'Cowry Golden'

# 导入依赖
import re, time, json, logging, hashlib, base64, asyncio

from coroweb import get, post
from models import User, Blog, Comment, next_id

r'''
# 测试使用
@get('/')
async def index(request):
    users = await User.findAll()
    return {
        '__template__' : 'test.html',
        'users' : users
    }
'''  

# 测试构建的Blog前端首页模板
@get('/')
def index(request):
    summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
    blogs = [
        Blog(id='1', name='Test Blog', summary=summary, created_at=time.time()-120),
        Blog(id='2', name='Something New', summary=summary, created_at=time.time()-3600),
        Blog(id='3', name='Learn Swift', summary=summary, created_at=time.time()-7200)
    ]
    return {
        '__template__' : 'blogs.html',
        'blogs' : blogs
    }

