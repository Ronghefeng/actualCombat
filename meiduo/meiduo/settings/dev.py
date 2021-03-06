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


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',  # CORS 跨域资源共享
    'rest_framework', # DRF
    'users.apps.UsersConfig',   # 用户模块
    'oauth.apps.OauthConfig',   # QQ 用户模块
    # 'oauth',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',    # CORS 跨域资源共享中间件
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
        'DIRS': [],
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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'

# 日志
LOGGING = {
    'version': 1,
    'disable_exiting_loggers': False,   # 是否禁用已存在的日志器
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
    # 缓存热点数据
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
}
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'session'

# DRF 配置
REST_FRAMEWORK = {
    # 异常捕获配置
    'EXCEPTION_HANDLER': 'meiduo.utils.exceptions.exception_handler'
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
