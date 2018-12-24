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

#存储下位机参数状态
robot={'state': 0,  #运行状态（8前/2后 4左/6右 5/停）
       'online':0,  #在线状态(0/1)
       'led':0,     #led状态(0/1)
       'alarm':0,   #蜂鸣器状态(0/1)
       'light':0,   #光照强度值（0~255）
       'tem':0,     #温度值(-30~100)
       'hum':0,     #相对湿度值(0~255)
       'pm2.5':0,   #pm2.5值(0~255)
       'position':'(0,0)',  #位置(x,y)
       }

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
    
@get('/manage/robots')
def manageRobots():
    return {
            '__template__' : 'manage_robots.html'
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

@get('/api/robots')
def getRobots():
    return dict(robot=robot)

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


''' test '''
@get('/test')
def test():
    return {
            '__template__' : 'test.html'
    }

@post('/api/test')
def postTest(*,state):
    robot['state']=state
    return robot

@get('/api/test')
def getTest():
    r=robot
    return r

@get('/ajax/api')
def ajaxApi():
    return {
            '__template__' : 'getapi.html'
    }

''' feedback status '''
'''
/api/status/online/{value}    #在线
/api/status/led/{value}       #led
/api/status/alarm/{value}     #蜂鸣器
/api/status/light/{value}     #光照强度
/api/status/tem/{value}       #温度
/api/status/hum/{value}       #相对湿度
/api/status/pm2.5/{value}     #pm2.5
/api/status/position/{(x,y)}  #位置
'''
@get('/api/status/{key}/{value}')
def rbStatus(*,key,value):
    robot[key]=value
    return robot
