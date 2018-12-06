# -*- coding: utf-8 -*-
"""
Created on Thu Oct 25 17:14:14 2018

@author: Administrator
"""

' url handlers '

import re, time, json, logging, hashlib, base64, asyncio
#import markdown2

from aiohttp import web
from coroweb import get, post
from apis import APIValueError, APIResourceNotFoundError, APIError,APIPermissionError,Page
from models import User, Comment, Robot
from config import configs

COOKIE_NAME = 'awesession'
_COOKIE_KEY = configs.session.secret

_re_email = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_re_sha1 = re.compile(r'^[0-9a-f]{40}$')

def check_admin(request):
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError()
        
def get_page_index(page_str):
    p=1
    try:
        p=int(page_str)
    except ValueError as e:
        pass
    if p<1:
        p=1
    return p

def text2html(text):
    lines = map(lambda s:'<p>%s</p>' % s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;'),filter(lambda s: s.strip()!='',text.split('\n')))
    return ''.join(lines)

def user2cookie(user, max_age):
    '''
    Generate cookie str by user.
    '''
    #build cookie string by: id-expires-sha1
    expires = str(int(time.time()+max_age))
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires,_COOKIE_KEY)
    return s

async def cookie2user(cookie_str):
    '''
    Parse cookie and load user if cookie is valid.
    '''
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L)!=4:
            return None
        uid,upasswd,expires,cookie_key = L
        if int(expires)<time.time():
            return None
        user = await User.find(uid)
        if user is None:
            return None
        if user.passwd != upasswd:
            logging.info('invalid password')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None

''' get '''

@get('/')
def index():
    return {
            '__template__' : 'home.html'
    }
    
@get('/console')
def ctrlP():
    return {
            '__template__' : 'ctrlP.html'
    }

@get('/registerUser')
def registerUser():
    return {
            '__template__' : 'register_user.html'        
    }
    
@get('/registerDevice')
def registerDevice():
    return {
            '__template__' : 'register_device.html'
    }
    
@get('/manage/users')
def manageUsers():
    return {
            '__template__' : 'manage_users.html'        
    }
    
@get('/manage/devices')
def manageDevices():
    return {
            '__template__' : 'manage_devices.html'
    }
    
@get('/signin')
def signin():
    return {
            '__template__' : 'signin.html'
    }

@get('/signout')
def signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound('/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logging.info('user signed out.')
    return r
    
''' get_api '''

@get('/api/users')
async def getUsers():
    users=await User.findAll()
    return dict(users=users)

@get('/api/devices')
async def getDevices():
    devices=await Robot.findAll()
    return dict(devices=devices)

''' post_api '''

@post('/api/users')
async def apiRegistUser(*,name,passwd):
    if not name or not name.strip():
        raise APIValueError('name','invalid name.')
    if not passwd or not name.strip():
        raise APIValueError('name','invalid password.')
    users = await User.findAll('name=?',[name])
    if len(users):
        raise APIError('register:failed', 'name', 'Name is already in use.')
    user=User(name=name.strip(),passwd=passwd)
    await user.save()
    # authenticate ok, set cookie:
    users = await User.findAll('name=?',[name])
    u=users[0]
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(u, 86400), max_age=86400, httponly=True)
    u.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(u, ensure_ascii=False).encode('utf-8')
    return r

@post('/api/devices')
async def apiRegistDevice(*,name,r_type,remarks):
    if not name or not name.strip():
        raise APIValueError('name','invalid name.')
    r = Robot(name=name,r_type=r_type,remarks=remarks,passwd='123456')
    await r.save()
    return r

@post('/api/authenticate')
async def userAuthenticate(*,name,passwd):
    if not name:
        raise APIValueError('name','invalid name.')
    if not passwd:
        raise APIValueError('passwd','invalid password.')
    users = await User.findAll('name=?',[name])
    if len(users)==0:
        raise APIValueError('name','Name not exist.')
    user=users[0]
    if user.passwd != passwd:
        raise APIValueError('passwd','Invalid password.')
    # authenticate ok, set cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r



'''  
@get('/')
def index(request):
    return {
        '__template__': '1.html'
    }
    
@get('/blog/{id}')
async def get_blog(id):
    blog = await Blog.find(id)
    comments = await Comment.findAll('blog_id=?',[id],orderBy='created_at desc')
    for c in comments:
        c.html_comment = text2html(c.content)
#    blog.html_content = markdown2.markdown(blog.content)
    return {
            '__template__': 'blog.html',
            'blog': blog,
            'comments': comments
            }
    
@get('/registerUser')
def registerUser():
    return {
            '__template__':'register-user.html'
            }
    
@get('/registerDevice')
def registerDevice():
    return {
            '__template__':'register-device.html'
            }
    
@get('/signin')
def signin():
    return {
 #           '__template__':'signin.html'
            '__template__':'3.html'
            }

@get('/root')
def root():
    return {
            '__template__':'__base__.html'
            }    
    
@get('/signout')
def signout(request):
    referer = request.headers.get('Referer')
    r=web.HTTPFound(referer or '/')
    r.set_cookie(COOKIRE_NAME,'-deleted-',max_age=0, httponly=True)
    logging.info('user signed out.')
    return r

@get('/api/users')
async def api_get_users():
    users = await User.findAll()
    for u in users:
        u.passwd = '******'
    return dict(users=users)

@get('/api/devices')
async def api_get_devices():
    robots = await Comment.findAll()
    for r in robots:
        r.passwd = '******'
    return dict(robots=robots)

@get('/manage/robots')
def manage_blogs(*, page='1'):
    return {
            '__template__': 'manage_blogs.html',
            'page_index': get_page_index(page)
            }

@get('/manage/blogs/create')
def manage_create_blog():
    return {
            '__template__': 'manage_blog_edit.html',
            'id': '',
            'action': '/api/blogs'
            }

@get('/blogs/{id}')
async def api_get_blog(*,id):
    blog = await Blog.find(id)
    return blog

@get('/api/blogs')
async def api_blogs(*,page='1'):
    page_index = get_page_index(page)
    num = await Blog.findNumber('count(id)')
    p = Page(num,page_index)
    if num ==0:
        return dict(page=p, blogs=0)
    blogs = await Blog.findAll(orderBy='created_at desc',limit=(p.offset,p.limit))
    return dict(page=p,blogs=blogs)

@post('/api/authenticate')
async def authenticate(*,email,passwd):
    if not email:
        raise APIValueError('email','Invalid email.')
    if not passwd:
        raise APIValueError('passwd','Invalid password.')
    users = await User.findAll('email=?',[email])
    if len(users) == 0:
        raise APIValueError('email','Email not exist.')
    user = users[0]
    #check passwd:
    sha1 = hashlib.sha1()
    sha1.update(user.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(passwd.encode('utf-8'))
    if user.passwd != sha1.hexdigest():
        raise APIValueError('passwd','Invalid password.')
    # authenticate ok, set cookie:
    r = web.Response()
    r.set_cookie(COOKIRE_NAME, user2cookie(user,86400),max_age=86400,httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user,ensure_ascii=False).encode('utf-8')
    print('234:',r)
    return r


@post('/api/users')
async def api_register_user(*,email, name, passwd):
    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not _re_email.match(email):
        raise APIValueError('email')
    if not passwd or not _re_sha1.match(passwd):
        raise APIValueError('passwd')
    users = await User.findAll('email=?',[email])
    if len(users)>0:
        raise APIError('register:failed','email','Email is already in use.')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid,passwd)
    user = User(id=uid, name=name.strip(),email=email,passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),image='/static/img/user.png')
    await user.save()
    #make session cookie:
    r = web.Response()
    r.set_cookie(COOKIRE_NAME,user2cookie(user,86400),max_age=86400,httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.bady = json.dumps(user,ensure_ascii=False).encode('utf-8')
    print('12345:',r)
    return r

@post('/api/blogs')
async def api_create_blog(request,*,name,summary,content):
    check_admin(request)
    if not name or not name.strip():
        raise APIValueError('name','name cannot be empty.')
    if not summary or not summary.strip():
        raise APIValueError('summary','summary cannot be empty.')
    if not content or not content.strip():
        raise APIValueError('content','content cannot be empty.')
    blog = Blog(user_id=request.__user__.id,user_name=request.__user__.name,user_image=request.__user__.image,name=name.strip(),summary=summary.strip(),content=content.strip())
    await blog.save()
    return blog


@get('/api/robot')
async def api_get_robot():
    users = await User.findAll()
    robots = await Robot.findAll()
    comments = await Comment.findAll()
    return dict(users=users),dict(robots=robots),dict(comments=comments)
        
'''
