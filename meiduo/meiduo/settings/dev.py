# 开发环境系统配置
"""
Django settings for meiduo project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""
import os, sys
import datetime
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# 追加系统导包路径
# 1、注册自应用时写法可以简洁
# 2、修改 Django 认证的用户模型时，格式固定为：应用名.模型名，否则路径报错
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '*a1*&b!&nr^lglyv*52jbz2g_ku_uv9*bs4g+qf9(#h&)u^23z'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# 允许访问系统的域名
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# 配置文件上传路径，默认存储在本地，生产环境中一般自行搭建分布式文件存储系统，如 FastDFS、或者上传至第三方文件系统，如 又拍云
MEDIA_ROOT = os.path.join(BASE_DIR.parent, 'media/images')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',  # CORS 跨域资源共享
    'rest_framework',  # DRF
    'ckeditor',  # 富文本编辑器
    'ckeditor_uploader',  # 富文本编辑器上传图片模块
    'django_crontab',  # 定时器模块

    # 由于 django 默认 app 的路径是 项目目录/app，此处修改为 项目目录/apps/app，
    # 因此注册时需要安装原始注册方式：app.apps.AppConfig
    'users.apps.UsersConfig',  # 用户
    'oauth.apps.OauthConfig',  # 第三方授权
    'areas.apps.AreasConfig',  # 行政区划
    'contents.apps.ContentsConfig',  # 广告
    'goods.apps.GoodsConfig',  # 商品
    'cards.apps.CardsConfig',   # 购物车
    'orders.apps.OrdersConfig', # 订单
    'myapp',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # CORS 跨域资源共享中间件
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'meiduo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'Templates')],  # 模板文件路径
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

WSGI_APPLICATION = 'meiduo.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'localhost',
        'PORT': 3306,
        'USER': 'root',
        'PASSWORD': 'root',
        'NAME': 'meiduo'
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'zh-hans'

# TIME_ZONE = 'UTC'
TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

# 日志
LOGGING = {
    'version': 1,
    'disable_exiting_loggers': False,  # 是否禁用已存在的日志器
    # 日志信息显示的格式
    'formatters': {
        # 详细输出格式
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)s %(message)s'
        },
        # 简单输出格式
        'simple': {
            'format': '%(levelname)s %(module)s  %(message)s'
        }
    },
    # 对日志进行过滤
    'filters': {
        # django 在 debug 模式下才输出日志
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        }
    },
    # 日志处理方法
    'handlers': {
        # 向终端输出日志
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        # 向文件输出日志
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            # 日志文件位置
            'filename': os.path.join(os.path.dirname(BASE_DIR), 'logs/meiduo.log'),
            # 文件存储内容大小
            'maxBytes': 30 * 1024 * 1024,
            # 最多保存文件数目
            'backupCount': 10,
            'formatter': 'verbose'
        }
    },
    # 日志器
    'loggers': {
        # 定义一个名为 django 的日志器
        # 使用该日志器： logger('django')
        'django': {
            # 指定同时向终端和文件输出日志
            'handlers': ['console', 'file'],
            # 是否继续传递日志信息
            'propagate': True,
            'level': 'INFO'
        }
    }
}

# 配置 redis 作为缓存后端
CACHES = {
    # 缓存热点数据，如省市区的数据
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient'
        }
    },
    # 缓存 session
    'session': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient'
        }
    },
    # 缓存认证数据
    'verify_codes': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/2',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient'
        }
    },
    # 缓存用户浏览记录
    'browser_history': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/3',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient'
        }
    },
    # 缓存用户购物车数据
    'carts': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/4',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient'
        }
    },
}
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'session'

# DRF 配置
REST_FRAMEWORK = {
    # 异常捕获配置
    'EXCEPTION_HANDLER': 'meiduo.utils.exceptions.exception_handler',

    # 认证配置
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 默认使用 JWT 认证
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BaseAuthentication'
    ),
    # 分页，指定每页数据数目
    'PAGE_SIZE': 3,
    # 指定全局分页类
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination'
}

# 修改 Django 认证系统的用户模型类
AUTH_USER_MODEL = 'users.User'

# CORS 追加前端域名白名单，允许跨域访问的域名
CORS_ORGIN_WHITELIST = (
    '127.0.0.1:8080',
    'localhost:8080'
)
# CORS 允许携带 cookie
CORS_ALLOW_CREDENTIALS = True

# JWT 配置，https://jpadilla.github.io/django-rest-framework-jwt/
JWT_AUTH = {
    # 默认过期时间设置：'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=300),
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1),
    # 设置 restframework 中默认的 JWT 返回处理函数 jwt_response_payload_handler
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'users.utils.jwt_response_payload_handler',
}

# 修改 Django 默认后端认证实现类
# Django 默认全局变量配置：django -> conf -> global_settings.py
AUTHENTICATION_BACKENDS = ['users.utils.MutiAccountLoginBackend']

# QQ 第三方登录
QQ_CLIENT_ID = 'qwertyuiopsdfghjk'
QQ_CLIENT_SECRET = '2erfdiwertyuiosdfghjklxcvbnm,'
QQ_REDIRECT_URL = 'xxxx'

# 发送邮件配置
# from django.core.mail import send_mail  # Django 内置邮件发送模块
# 邮件发送客户端实现，django.conf.global_settings 中已配置
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# 当前测试使用网易邮箱作为邮箱服务器
EMAIL_HOST = 'smtp.163.com'

# 服务端口，默认 25，django.conf.global_settings 中已配置
# EMAIL_PORT = 25
EMAIL_USE_LOCALTIME = False

# 发件人邮箱指定
EMAIL_HOST_USER = '15757337126@163.com'
# 在网易邮箱设置的授权密码
EMAIL_HOST_PASSWORD = 'XCEDSIQICXULKUUJ'
# # 收件人邮箱
# EMAIL_FROM = '2427219623@163.com'

# 对于数据变化频率较低，且需要频繁获取的数据，可以通过缓存到 redis 中，减少对后端数据库的查询，提升性能
# drf 中提供了扩展模块：drf-extensions，用于对查询动作获取的数据进行缓存
# 使用方式：
#   1、装饰器：@cache_response(timeout=60*60, cache='default') 装饰在视图中的 get 函数
#   2、继承扩展类，修改全局变量：
#       继承：ListCacheResponseMixin、RetrieveCacheResponseMixin、CacheResponseMinxin
#       配置变量：REST_FRAMEWORK_EXTENSIONS
# drf-extensions 配置
REST_FRAMEWORK_EXTENSIONS = {
    # 缓存过期时间，单位秒
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 60 * 60,
    # 缓存数据存储位置，此处选择 Django 缓存配置的 CACHES 的 default 缓存数据库
    'DEFAULT_USER_CACHE': 'default',
}

# 富文本编辑器 ckeditor 配置
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',  # 工具条功能
        'height': 300,  # 编辑器高度
        # 'width': 300    # 编辑器宽
    }
}

CKEDITOR_UPLOAD_PATH = os.path.join(BASE_DIR.parent, 'media/images')  # 上传图片保存路径

# 静态化主页存储路径
# BASE_DIR = '/Users/rhf/PycharmProjects/actualCombat/meiduo/meiduo/apps'
GENERATED_STATIC_HTML_FILES_DIR = os.path.join(os.path.dirname(BASE_DIR), 'fromt_end_pc')

# 配置定时任务
# 由于定时任务同 Celery 任务一样，独立于 Django 系统，因此需要单独启动
# 命令
#   1、添加定时任务到系统中：python manage.py crontab add
#   2、显示已经激活的（添加至系统中）任务：python manage.py crontab show
#   3、移除定时任务：python manage.py crontab remove

CRONTAB_LOG_PATH = os.path.join(os.path.dirname(BASE_DIR), 'logs/crontab.log')

# 解决中文乱码问题
CRONTAB_COMMAND_PREFIX = 'LANG_ALL=zh_cn.UTF-8'

# CRONJOBS = [
#     # 当前业务场景，每 5 分钟就获取首页数据渲染 index.html
#     # (定时计划[分 时 日 月 周]， 任务， 日志输出路径)
#     ('*/1 * * * *', 'contents.crons.generate_static_index_html', '>> %s' % CRONTAB_LOG_PATH)
# ]

CRONJOBS = [
    # 每5分钟执行一次生成主页静态文件
    ('*/1 * * * *', 'contents.crons.generate_static_index_html', '>> %s' % CRONTAB_LOG_PATH),
]

