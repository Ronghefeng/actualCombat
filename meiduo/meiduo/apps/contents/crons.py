import os, logging
import time

from django.conf import settings
from django.template import loader

from goods.utils import get_categories
from . import constants


logger = logging.getLogger('django')

def generate_static_index_html():
    """
    生成静态的主页html文件
    调用方式
    def index(request):
        generate_static_index_html()
    注意：
        根据业务需求，使用定时器定时更新数据，
        由于是静态文件，因此，即使后台数据更新，如果用户不刷新页面，其渲染数据仍不会改变
    """

    # print 在 crontab 的日志中才会输出
    print('%s: generate_static_index_html' % time.ctime())
    # 只在配置的日志文件中输出
    logger.info('%s: generate_static_index_html', time.ctime())

    context = get_categories()

    # 加载模板文件
    # get_template 会从 setting 中找到 TEMPLATES 配置的模板文件存放路径
    template = loader.get_template(constants.INDEX_HTML_NAME)

    # 渲染模板
    html_text = template.render(context)

    # 指定渲染后的文件存放路径，当前测试环境下，放入 front_end_pc 目录下，生产环境一般指定为 Nginx 下的路径
    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, constants.INDEX_HTML_NAME)

    # encoding：防止定时器中文乱码问题
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_text)

