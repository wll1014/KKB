"""
Django settings for ops project.

Generated by 'django-admin startproject' using Django 2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import sys, platform
from common.global_func import get_conf

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'voj%5%rcb8^(-nb8fmumw-685w-y)$mcwco80rlmxg-(z)6)+r'

# SECURITY WARNING: don't run with debug turned on in production!
if isinstance(get_conf('django', 'debug'), str) and get_conf('django', 'debug').lower() == 'true':
    DEBUG = True
else:
    DEBUG = False

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'hosts.apps.HostsConfig',
    'rest_framework',
    'corsheaders',
    'maintenance.apps.MaintenanceConfig',
    'faq.apps.FaqConfig',
    'sidebar.apps.SidebarConfig',
    'overview.apps.OverviewConfig',
    'ops_statistics.apps.StatisticsConfig',
    'warning.apps.WarningConfig',
    'oplog.apps.OplogConfig',
    'hosts_oper.apps.HostsOperConfig',
    'platmonitor.apps.PlatmonitorConfig',
    'diagnose.apps.DiagnoseConfig',
    'issue_tracking.apps.IssueTrackerConfig',
    'platreport.apps.PlatreportConfig',
    'version_control.apps.VersionControlConfig',
]

MIDDLEWARE = [
    # 'django.middleware.cache.UpdateCacheMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'middleware.authenticate.SSOAuthenticate',
    'middleware.operationlog.OperationLog'
    # 'django.middleware.cache.FetchFromCacheMiddleware',
]
# CACHE_MIDDLEWARE_SECONDS=5

# 允许携带cookie
CORS_ALLOW_CREDENTIALS = True

if DEBUG:
    # 允许所有跨域请求
    CORS_ORIGIN_ALLOW_ALL = True
else:
    # 允许跨域请求的白名单
    CORS_ORIGIN_WHITELIST = (
        '*',
    )

CORS_EXPOSE_HEADERS = ["Content-Disposition"]

ROOT_URLCONF = 'ops.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ops.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': get_conf("mysql", "database"),
        'USER': get_conf("mysql", "user"),
        'PASSWORD': get_conf("mysql", "password"),
        'HOST': get_conf("mysql", "host"),
        'PORT': get_conf("mysql", "port"),
    },
    'luban': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': get_conf("lubandb", "database"),
        'USER': get_conf("lubandb", "user"),
        'PASSWORD': get_conf("lubandb", "password"),
        'HOST': get_conf("lubandb", "host"),
        'PORT': get_conf("lubandb", "port"),
    },
    'movision': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': get_conf("movision", "database"),
        'USER': get_conf("movision", "user"),
        'PASSWORD': get_conf("movision", "password"),
        'HOST': get_conf("movision", "host"),
        'PORT': get_conf("movision", "port"),
    },
    'meeting': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': get_conf("meeting", "database"),
        'USER': get_conf("meeting", "user"),
        'PASSWORD': get_conf("meeting", "password"),
        'HOST': get_conf("meeting", "host"),
        'PORT': get_conf("meeting", "port"),
    },
    'nms_db': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'nms_db',
        'USER': get_conf("movision", "user"),
        'PASSWORD': get_conf("movision", "password"),
        'HOST': get_conf("movision", "host"),
        'PORT': get_conf("movision", "port"),
    }
}

DATABASE_APPS_MAPPING = {
    # 'overview':'luban'
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# 禁止自动重定向末尾加/
APPEND_SLASH = False

# 解决多个django应用都使用sessionid时，名称冲突导致的服务器异常问题
SESSION_COOKIE_NAME = "ops_sessionid"
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
if sys.platform == 'linux':
    MEDIA_ROOT = get_conf("media", "path")
else:
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

if not os.path.exists(MEDIA_ROOT):
    os.makedirs(MEDIA_ROOT, exist_ok=True)

MEDIA_URL = '/api/v1/ops/media/'

# 版本控制相关
REST_FRAMEWORK = {
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning',
    'DEFAULT_VERSION': 'v1',  # 默认版本(从request对象里取不到，显示的默认值)
    'ALLOWED_VERSIONS': ['v1', ],  # 允许的版本
    'VERSION_PARAM': 'version',  # URL中获取值的key
    'EXCEPTION_HANDLER': 'common.my_exception.ops_exception_handler',    # 错误处理模块
}

# 版本管理相关
VERSION_CONTROL_TYPE = ['platform', 'terminal', 'os']
for type_ in VERSION_CONTROL_TYPE:
    if not os.path.exists(os.path.join(MEDIA_ROOT, "version_control", type_)):
        os.makedirs(os.path.join(MEDIA_ROOT, "version_control", type_), exist_ok=True)
FTP_PORT = get_conf("ftp", "port")

# 序列化文件存储
PKS_ROOT = os.path.join(MEDIA_ROOT, 'pks')
if not os.path.exists(PKS_ROOT):
    os.makedirs(PKS_ROOT, exist_ok=True)

# 日志相关
if sys.platform == 'linux':
    LOG_PATH = get_conf("log", "path")
else:
    LOG_PATH = os.path.join(BASE_DIR, 'log')

if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(levelname)s %(asctime)s %(pathname)s %(funcName)s %(lineno)s %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(message)s'
        }
    },
    'filters': {
    },
    'handlers': {
        'file': {
            'level': str(get_conf("log", "level")),
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_PATH, 'ops.log'),
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
        'info_file': {
            'level': str(get_conf("log", "level")),
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_PATH, 'ops_info.log'),
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
        'console': {
            'level': str(get_conf("log", "level")),
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        }
    },
    'loggers': {
        'ops': {
            'handlers': ['file'],
            'level': str(get_conf("log", "level")),
            'propagate': False
        },
        'ops_info': {
            'handlers': ['info_file'],
            'level': str(get_conf("log", "level")),
            'propagate': False
        },
    }
}

# 缓存相关
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://172.16.186.208:6379/10',
        'TIMEOUT': None,  # 缓存超时时间（默认300s，None表示永不过期，0表示立即过期）
        'OPTIONS': {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": "KedaRedis16",
            'MAX_ENTRIES': 300,  # 最大缓存个数（默认300）
            'CULL_FREQUENCY': 3,  # 缓存到达最大个数之后，剔除缓存个数的比例，即1/CULL_FREQUENCY（默认3）
        },
    }
}

# 自定义配置
# 无详情页面主机类型列表
NO_DETAIL_DEV_TYPES = get_conf('no_detail_hosts', 'devtype').split(',')

# ansible相关
ANSIBLE_PORT = get_conf('ansible', 'port')

# 定制项
CUSTOM = get_conf('custom')
