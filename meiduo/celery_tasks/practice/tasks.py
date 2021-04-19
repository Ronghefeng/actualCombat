from celery_tasks.main import celery_app
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@celery_app.task(name='test1')
def test1(x, y):

    logger.info('test1 receive x=%s, y=%s', x, y)

    return x + y
