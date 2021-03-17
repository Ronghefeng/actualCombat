# celery 入口
from celery import Celery

# celery 运行在另外单独的进程，同当前程序进程独立

# 创建 celery 实例对象
celery_app = Celery('meiduo')

# 加载 celery 配置
celery_app.config_from_object('celery_tasks.config')

# 自动注册异步任务
celery_app.autodiscover_tasks(['celery_tasks.sms'])


# 启动任务命令，需要另外启动
# -l info：打印日志，level=info
# celery -A celery_tasks.main worker -l info