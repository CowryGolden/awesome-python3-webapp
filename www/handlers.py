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
from apis import Page, APIError, APIValueError, APIPermissionError, APIResourceNotFoundError
from models import User, Blog, Comment, next_id
from config import configs


# 定义cookie名和从配置中获取cookie_key
COOKIE_NAME = 'awesession'
_COOKIE_KEY = configs.session.secret

# 检查用户是否为管理员用户
def check_admin(request):
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError('Non-admin, no permission.')

# 获取当前页的页号
def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p

# 将纯文本内容转为html格式
def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)

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
# @get('/')
# def index(request):
#     r""" 
#     #### 由于已经使用middleware功能找到cookie对应的user并放入request【具体参见：app.py，response_factory()方法中加入的：r['__user__'] = request.__user__ 等语句】
#     #### 因此不需要如下判断和获取了，仅需在返回内容中加入：'__user__' : request.__user__ 即可
#     # 增加对登录用户的判断
#     user = None
#     cookie_str = request.cookies.get(COOKIE_NAME)
#     if cookie_str:
#         if 'deleted' in cookie_str:    # 因为登出之后cookie变为了‘-delete-’,不加判断的话会调用cookie2user()函数，而这个函数里边有int(expires)，此时expires就是‘delete’,是一个非数字的字符串，会报错
#             user = None
#         else:
#             user = await cookie2user(cookie_str)
#     """
#     summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
#     blogs = [
#         Blog(id='1', name='Test Blog', summary=summary, created_at=time.time()-120),
#         Blog(id='2', name='Something New', summary=summary, created_at=time.time()-3600),
#         Blog(id='3', name='Learn Swift', summary=summary, created_at=time.time()-7200)
#     ]
#     return {
#         '__template__' : 'blogs.html',
#         'blogs' : blogs,
#         '__user__' : request.__user__    # 用户对登录用户的判断
#     }

# 构建Blog主页
@get('/')
async def index(request, *, page='1'):
    page_index = get_page_index(page)
    num = await Blog.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        blogs = []
    else:
        blogs = await Blog.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    return {
        '__template__' : 'blogs.html',
        'page' : p,
        'blogs' : blogs,
        '__user__' : request.__user__
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

# 后台管理入口，重定向处理
@get('/manage/')
def manage():
    return 'redirect:/manage/comments'


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

# Blog管理主页面跳转页
@get('/manage/blogs')
def manage_blogs(*, page='1'):
    return {
        '__template__' : 'manage_blogs.html',
        'page_index' : get_page_index(page)
    }

# 管理者创建blog跳转页
@get('/manage/blogs/create')
def manage_create_blog():
    return {
        '__template__' : 'manage_blog_edit.html',
        'id' : '',
        'action' : '/api/blogs'
    }

# 后台管理者进行blog编辑跳转页
@get('/manage/blogs/edit')
def manage_edit_blog(*, id):
    return {
        '__template__' : 'manage_blog_edit.html',
        'id' : id,
        'action' : '/api/blogs/%s' % id
    }

# 后台评论管理跳转页面
@get('/manage/comments')
def manage_comments(*, page='1'):
    return {
        '__template__' : 'manage_comments.html',
        'page_index' : get_page_index(page)
    }

# 后台用户管理跳转页
@get('/manage/users')
def manage_users(*, page='1'):
    return {
        '__template__' : 'manage_users.html',
        'page_index' : get_page_index(page)
    }


# 根据id获取Blog信息API
@get('/blog/{id}')
async def get_blog(id):
    blog = await Blog.findByPriKey(id)
    comments = await Comment.findAll('blog_id=?', [id], orderBy='created_at desc')
    for c in comments:
        c.html_content = text2html(c.content)        
    blog.html_content = markdown2.markdown(blog.content)
    return {
        '__template__' : 'blog.html',
        'blog' : blog,
        'comments' : comments
    }

# 获取Blog列表API
@get('/api/blogs')
async def api_blogs(*, page='1'):
    page_index = get_page_index(page)
    num = await Blog.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, blogs=())
    blogs = await Blog.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, blogs=blogs)

# 根据blog id获取blog的API
@get('/api/blogs/{id}')
async def api_get_blog(*, id):
    blog = await Blog.findByPriKey(id)
    return blog

# 创建blog的API
@post('/api/blogs')
async def api_create_blog(request, *, name, summary, content):
    check_admin(request)
    if not name or not name.strip():
        raise APIValueError('name', 'Name cannot be empty.')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'Summary cannot be empty.')
    if not content or not content.strip():
        raise APIValueError('content', 'Content cannot be empty.')        
    blog = Blog(user_id=request.__user__.id, user_name=request.__user__.name, user_image=request.__user__.image, name=name.strip(), summary=summary.strip(), content=content.strip())
    await blog.save()
    return blog

# 更新blog的API
@post('/api/blogs/{id}')
async def api_update_blog(id, request, *, name, summary, content):
    check_admin(request)
    blog = await Blog.findByPriKey(id)
    if not name or not name.strip():
        raise APIValueError('name', 'Name cannot be empty.')
    if not summary or not summary.strip():
        raise APIValueError('summary', 'Summary cannot be empty.')
    if not content or not content.strip():
        raise APIValueError('content', 'Content cannot be empty.')
    blog.name = name.strip()
    blog.summary = summary.strip()
    blog.content = content.strip()
    await blog.update()
    return blog

# 根据主键id删除Blog API
@post('/api/blogs/{id}/delete')
async def api_delete_blog(request, *, id):
    check_admin(request)
    blog = await Blog.findByPriKey(id)
    if blog:
        await blog.remove()
        logging.info('The blog is removed successfully.[id=%s] [blog=%s]' % (id, blog))
    else:
        logging.info('The blog is not exist.[id=%s]' % id)
    # return blog
    return dict(id=id)

# 查询所有评论API
@get('/api/comments')
async def api_comments(*, page='1'):
    page_index = get_page_index(page)
    num = await Comment.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, comments=())
    comments = await Comment.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, comments=comments)

# 发表（创建）评论API
@post('/api/blogs/{id}/comments')
async def api_create_comment(id, request, *, content):
    user = request.__user__
    if user is None:
        raise APIPermissionError('Please signin first.')
    if not content or not content.strip():
        raise APIValueError('content', 'Content cannot be empty.')
    blog = await Blog.findByPriKey(id)
    if blog is None:
        raise APIResourceNotFoundError('Blog', 'Blog is not found.')
    comment = Comment(blog_id=blog.id, user_id=user.id, user_name=user.name, user_image=user.image, content=content.strip())
    await comment.save()
    return comment

# 根据主键id删除评价API
@post('/api/comments/{id}/delete')
async def api_delete_comments(id, request):
    check_admin(request)
    c = await Comment.findByPriKey(id)
    if c is None:
        raise APIResourceNotFoundError('Comment', 'Comment is not found.')
    await c.remove()
    return dict(id=id)

# 获取所有用户信息API
@get('/api/users')
async def api_get_users(*, page='1'):
    page_index = get_page_index(page)
    num = await User.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, users=())
    users = await User.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    for u in users:
        u.passwd = '******'
    return dict(page=p, users=users)        





    