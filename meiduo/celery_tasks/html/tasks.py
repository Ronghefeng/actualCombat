import os

from django.template import loader
from django.conf import settings

from goods import constants, utils
from celery_tasks.main import celery_app


@celery_app.task(name='generate_goods_list_html')
def generate_goods_list_html():
    """生成商品列表页的静态文件 list.html"""

    context = utils.get_categories()

    template = loader.get_template(constants.LIST_HTML_NAME)

    list_html = template.render(context)

    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, constants.LIST_HTML_NAME)

    with open(file_path, 'w') as f:
        f.write(list_html)