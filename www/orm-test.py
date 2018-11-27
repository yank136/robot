# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 16:10:11 2018

@author: Administrator
"""

import orm, asyncio
from models import User,Robot,Comment

async def init(loop):
    await orm.create_pool(loop=loop,user='www',password='www',db='robot')
    u=User(name='student',passwd='123456')
    await u.save()
 
loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()