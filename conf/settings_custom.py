# -*- coding: utf-8 -*-
'''
@summary: 用户自定义全局常量设置
'''
import os

# ============================================================================
# 中间件和应用
# ============================================================================
# 自定义中间件
MIDDLEWARE_CLASSES_CUSTOM = (
    'gcloud.core.middlewares.NotAcceptableMiddleware',
    'gcloud.core.middlewares.UnauthorizedMiddleware',
    'gcloud.core.middlewares.GCloudPermissionMiddleware',
    'gcloud.core.middlewares.TimezoneMiddleware',
)
# 自定义APP

INSTALLED_APPS_CUSTOM = (
    # add your app here...
    # Note: 请注意在第一次syncdb时只加入south, 而不加自己的app，先syncdb初始化south的数据，
    # 然后再加入自己的app进行south操作!
    'guardian',
    'gcloud.core',
    'gcloud.config',
    'gcloud.tasktmpl3',
    'gcloud.taskflow3',
    'gcloud.webservice3',
    'gcloud.contrib.appmaker',
    'gcloud.contrib.function',
    'gcloud.contrib.audit',
    'gcloud.apigw',
    'pipeline',
    'pipeline.blueflow',
    'pipeline.component_framework',
    'pipeline.components',
    'pipeline.variables',
    'pipeline.engine',
    'django_signal_valve',
    # 'django_extensions'
    'custom_atoms'
)

# 静态资源文件(js,css等）在应用上线更新后, 由于浏览器有缓存, 可能会造成没更新的情况.
# 所以在引用静态资源的地方，都需要加上这个版本号，如：<script src="/a.js?v=${STATIC_VERSION}"></script>；
# 如果静态资源修改了以后，上线前修改这个版本号即可
STATIC_VERSION = '1.0.39'

# =============================================================================
# CELERY 配置
# =============================================================================
# APP是否使用celery
IS_USE_CELERY = True  # APP 中 使用 celery 时，将该字段设为 True
# TOCHANGE调用celery任务的文件路径, 即包含如下语句的文件： from celery import task
CELERY_IMPORTS = (
)

# =============================================================================
# 日志级别
# =============================================================================
# 本地开发环境日志级别
LOG_LEVEL_DEVELOP = 'INFO'
# 测试环境日志级别
LOG_LEVEL_TEST = 'INFO'
# 正式环境日志级别
LOG_LEVEL_PRODUCT = 'INFO'  # 'ERROR'

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
    },
}

# 通知公告域名
PUSH_URL = os.environ.get('BK_PUSH_URL', '')

# db cache
# create cache table by execute:
# python manage.py createcachetable django_cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache"
    },
    "dbcache": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache"
    },
    "dummy": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    },
}


# 创建默认模版的系统用户信息
SYSTEM_USERNAME = 'system_user'
SYSTEM_USER_CH = u"系统用户"

# 针对CC接口数据相关的缓存时间(单位s)
DEFAULT_CACHE_TIME_FOR_CC = 5

# 针对本地用户信息更新标志缓存的时间
DEFAULT_CACHE_TIME_FOR_USER_UPDATE = 5

# 针对平台用户接口缓存的时间
DEFAULT_CACHE_TIME_FOR_AUTH = 5

# CC系统名称
ESB_COMPONENT_CC = 'cc'

# cc、job域名
BK_CC_HOST = os.environ.get('BK_CC_HOST')
BK_JOB_HOST = os.environ.get('BK_JOB_HOST')

PIPELINE_TEMPLATE_CONTEXT = 'gcloud.tasktmpl3.utils.get_template_context'
PIPELINE_INSTANCE_CONTEXT = 'gcloud.taskflow3.utils.get_instance_context'

# ESB 默认版本配置 '' or 'v2'
DEFAULT_BK_API_VER = ''
