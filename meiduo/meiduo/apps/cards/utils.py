import pickle, base64

from django_redis import get_redis_connection
from . import constents


def merge_cookie_cart_into_redis(request, user, response):
    """
    登录时合并购物车信息
    request: 请求对象
    user：请求用户
    response： 返回响应
    """
    # 1、查询 request 中 cookie 的购物车信息
    # 2、如果 cookie 中有购物车数据，则合并到 redis 中
        # 合并规则：将 cookie 中 sku_id 增量添加到 redis hash 中；
        # cookie 和 redis 其中一个 selecte 为 True，则加入到 redis set 中
    # 3、清除 cookie

    carts = request.COOKIES.get('carts')

    if not carts:
        return

    carts = pickle.loads(base64.b64decode(carts.encode()))

    redis_conn = get_redis_connection('carts')
    pl = redis_conn.pipeline()

    carts_info_key = constents.USER_CARTS_INFO_HASH_KEY + str(user.id)
    selected_info_key = constents.USER_CARTS_INFO_SET_KEY + str(user.id)

    for sku_id in carts:
        pl.hincrby(carts_info_key, sku_id, carts[sku_id].get('count'))

        if carts[sku_id].get('selected'):
            pl.sadd(selected_info_key, sku_id)

    pl.execute()

    response.delete_cookie('carts')
