#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r'''
    # DEV-Default configurations.默认配置（开发环境）

'''
__author__ = 'Cowry Golden'

# 导入依赖
# import orm

configs = {
    'debug' : True,
    'db' : {
        'host' : '127.0.0.1',
        'port' : 3306,
        'user' : 'www-data',
        'password' : 'www-data',
        'db' : 'awesome'
    },
    'session' : {
        'secret' : 'Awesome'
    }
}

     