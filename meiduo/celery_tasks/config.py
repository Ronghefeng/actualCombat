# celery 配置信息
import os
import logging.config

# 指定任务队列存放位置
broker_url = 'redis://127.0.0.1/9'
backend_url = 'redis://127.0.0.1/10'

# celery 日志
LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'datefmt':
            '%m-%d-%Y %H:%M:%S',
            'format':
            '%(asctime)s \"%(pathname)s：%(module)s:%(funcName)s:%(lineno)d\" [%(levelname)s]- %(message)s'
        }
    },
    'handlers': {
        'celery': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'simple',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': '/celery_tasks/logs/celery.log',
            'maxBytes': 30 * 1024 * 1024,
            'backupCount': 10,
            'when': 'midnight',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        'meiduo_celery': {
            'handlers': ['celery'],
            'level': 'INFO',
            'propagate': True,
        }
    }
}

logging.config.dictConfig(LOG_CONFIG)
