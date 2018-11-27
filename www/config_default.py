# -*- coding: utf-8 -*-
"""
Created on Thu Oct 25 17:24:00 2018

@author: Administrator
"""

#config_default.py

configs = {
    'debug': True,
    'db': {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'www',
        'password': 'www',
        'db': 'robot'
    },
    'session': {
        'secret': 'robot'
    }
}