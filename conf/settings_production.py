# -*- coding: utf-8 -*-
"""
用于正式环境的全局配置
"""
import os


# ===============================================================================
# 数据库设置, 正式环境数据库设置
# ===============================================================================
from conf.default import APP_ID

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 默认用mysql
        'NAME': APP_ID,                        # 数据库名 (默认与APP_ID相同)
        'USER': 'root',                            # 你的数据库user
        'PASSWORD': '@86Dj3Y(it',                        # 你的数据库password
        'HOST': '192.168.102.226',                   		   # 数据库HOST
        'PORT': '3306',
    },
}
