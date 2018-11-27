# -*- coding: utf-8 -*-
"""
Created on Tue Oct 23 17:06:52 2018

@author: Administrator
"""

import asyncio
import orm
import random
from models import User,Blog,Comment

async def test(loop):
    await orm.create_pool(loop,user='www',password='www',db='awesome')
    u =User(name='test',email='test%s@example.com' % random.randint(0,10000000),passwd='abc123456',image='about:blank')
    await u.save()
    b =Blog(user_id='1',user_name='test',name='first',user_image='about:blank',summary='this ia the first blog.',content='about:blank')
    await b.save()
    c =Comment(blog_id='20003',user_id='1',user_name='text',user_image='about:blank',content='about:blank')
    await c.save()
'''
#要运行协程，需要使用事件循环 
if __name__ == '__main__':
        loop = asyncio.get_event_loop()
        loop.run_until_complete(test(loop))
        print('Test finished.')
        loop.close()
        '''
        
import logging
logger = logging.getLogger(__name__)
logger.setLevel(level = logging.INFO)
handler = logging.FileHandler("log.txt")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.info("Start print log")
logger.debug("Do something")
logger.warning("Something maybe fail.")
logger.info("Finish")
while(1):
    pass