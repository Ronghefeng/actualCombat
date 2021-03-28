# """
# 购物车处理
# """
# """
# 购物车数据存储数据 sku_id（sku 商品 id）、count（加购数量）、selected（是否选中）
# 处理分两种情况
# 1、用户已登录
#     1）数据存入 redis
#     2）redis hash 存储商品 sku_id 及对应加购数量：{sku_id: count}
#     3）redis set 存储 sku_id，set 不允许值重复，将选中的 sku_id 存入 set
# 2、用户未登录
#     将数据存入用户的 cookie 中
#     序列化 & 反序列化
#         json.dumps: python obj -> json
#         json.loads: json -> python obj
#
#         pickle.dumps: python obj -> bytes obj
#         pickle.loads: bytes obj -> python obj
#
#         base64encode: bytes obj -> bytes str
#         base64decode: bytes str -> bytes obj
#
#         pickle 效率要优于 json
# """