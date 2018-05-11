#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r'''
    # url handlers：url处理器

'''
__author__ = 'Cowry Golden'

# 导入依赖
import re, time, json, logging, hashlib, base64, asyncio

import markdown2

from aiohttp import web
from coroweb import get, post
from apis import APIError, APIValueError, APIResourceNotFoundError
from models import User, Blog, Comment, next_id
from config import configs

# 定义cookie名和从配置中获取cookie_key
COOKIE_NAME = 'awesession'
_COOKIE_KEY = configs.session.secret

# 将用户信息转换为cookie对象
def user2cookie(user, max_age):
    '''
    Generate cookie str by user.
    '''
    # build cookie string by: user.id-expires-sha1（其中：sha1=SHA1(user.id-user.passwd-expires-SecretKey)）
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)

# 通过（有效的）cookie对象解析用户信息
async def cookie2user(cookie_str):
    '''
    Parse cookie and load user if cookie is valid.
    '''
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L    # 其中cookie由三部分组成cookie_str=user.id-expires-sha1
        if int(expires) < time.time():
            return None
        user = await User.findByPriKey(uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('Invalid sha1.')
            return None
        user.passwd = '******'    # 将用户口令脱敏返回
        return user
    except Exception as e:
        logging.exception(e)
        return None    



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

r'''
# 使用REST风格API获取用户信息（测试使用）
# 这里通过Web API获取json格式的用户信息数据，访问路径：http://127.0.0.1:9000/api/users
@get('/api/users')
async def api_get_users():
    users = await User.findAll(orderBy='created_at desc')
    for u in users:
        u.passwd = '******'
    return dict(users=users)    
'''

# 用户注册跳转页面
@get('/register')
def register():
    return {
        '__template__' : 'register.html'
    }

# 用户登录跳转页面
@get('/signin')
def signin():
    return {
        '__template__' : 'signin.html'
    }


# 用户登出处理
@get('/signout')
def signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)    # 将cookie删除，置为失效
    logging.info('User signed out.')
    return r

# 用户口令认证API（用户登录API）
@post('/api/authenticate')
async def authenticate(*, email, passwd):
    if not email:
        raise APIValueError('email', 'Invalid email.')
    if not passwd:
        raise APIValueError('passwd', 'Invalid password.')
    users = await User.findAll('email=?', [email])
    if len(users) == 0:
        raise APIValueError('email', 'Email not exist.')
    user = users[0]
    # check passwd:(密码sha1=SHA1(user.id:passwd))
    # sha1 = hashlib.sha1()
    # sha1.update(user.id.encode('utf-8'))
    # sha1.update(b':')
    # sha1.update(passwd.encode('utf-8'))
    # sha1_passwd = sha1.hexdigest()
    salt_passwd_str = '%s:%s' % (user.id, passwd)
    sha1_passwd = hashlib.sha1(salt_passwd_str.encode('utf-8')).hexdigest()
    if user.passwd != sha1_passwd:
        raise APIValueError('passwd', 'Invalid password.')
    # authenticate ok, set cookie:(登录认证成功，则将用户信息设置到cookie中返回给前端)
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r

# 定义email和sha1验证的正则表达式
_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')

# 注册用户信息API（用户注册API）
@post('/api/users')
async def api_register_user(*, email, name, passwd):
    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')
    if not passwd or not _RE_SHA1.match(passwd):
        raise APIValueError('passwd')
    users = await User.findAll('email=?', [email])
    if len(users) > 0:
        raise APIError('register:failed', 'email', 'Email is already in use.')
    uid = next_id()
    # sha1_passwd = '%s:%s' % (uid, passwd)
    # user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(), image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
    salt_passwd_str = '%s:%s' % (uid, passwd)
    sha1_passwd = hashlib.sha1(salt_passwd_str.encode('utf-8')).hexdigest()
    user = User(id=uid, name=name.strip(), email=email, passwd=sha1_passwd, image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
    await user.save()
    # make session cookie:(注册成功就将cookie组装好返回给前端)
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r

