# -*- coding: utf-8 -*-
"""
Created on Tue Oct 23 16:18:21 2018

@author: Administrator
"""

import time

from orm import Model, StringField, BooleanField, FloatField, TextField,IntegerField

class User(Model):
    __table__ = 'users'
    
    id = IntegerField(primary_key=True,default=False)
    passwd = StringField(ddl='varchar(50)')
    admin = BooleanField()
    name = StringField(ddl='varchar(50)')
    
class Robot(Model):
    __table__ = 'robots'
    
    id = IntegerField(primary_key=True,default=False)
    name = StringField(ddl='varchar(50)')
    passwd = StringField(ddl='varchar(50)')
    r_type = StringField(ddl='varchar(50)')
    remarks = StringField(ddl='tinytext')

    
class Comment(Model):
    __table__ = 'comments'

    id = IntegerField(primary_key=True,default=False)
    robot_id = StringField(ddl='varchar(50)')
    robot_name = StringField(ddl='varchar(50)')
    robot_name = StringField(ddl='varchar(50)')
    r_image = StringField(ddl='varchar(500)')
    r_time = FloatField(default=time.time)
    r_position = StringField(ddl='varchar(50)')
    
