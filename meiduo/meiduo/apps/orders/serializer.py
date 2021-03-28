from decimal import Decimal

from django.utils.datetime_safe import datetime
from django.db import transaction
from django_redis import get_redis_connection
from rest_framework import serializers


from goods import models as goodsmodels
from cards import constents as cartsconst
from . import models


class OrderSKUSerializer(serializers.ModelSerializer):
    """自定义订单中商品序列化器"""

    # 自定义需要展示的非模型字段
    count = serializers.IntegerField(label='商品加购数')

    class Meta:
        model = goodsmodels.SKU
        fields = [
            'id',
            'name',
            'caption',
            'goods',
            'category',
            'price',
            'sales',
            'comments',
            'default_image_url',
            'count'
        ]


class OrderSerializer(serializers.Serializer):
    """自定义订单序列化器"""

    freight = serializers.DecimalField(label='运费', max_digits=10, decimal_places=2)
    skus = OrderSKUSerializer(many=True)


class CommitOrderSerializer(serializers.ModelSerializer):
    """定义订单提交序列化器"""

    class Meta:
        model = models.OrderInfo
        # 由于 OrderInfo 中，购物车信息从 redis 中获取，用户信息从 request 获取，
        # 因此只需要前端传入两个字段：address 和 pay_method
        fields = ['order_id', 'address', 'pay_method']
        # read_only_fields = ['order_id']
        extra_kwargs = {
            'address': {'write_only': True},
            'pay_method': {'write_only': True},
            'order_id': {'read_only': True}
        }

    def create(self, validated_data):
        """
        解决资源抢夺问题
        1、悲观锁
            当查询某条数据时，即让数据库加锁，让其他事务无法操作
            悲观锁容易类似于多线程资源竞争时的互斥锁，容易造成死锁，且降低数据库的并发性
            select * from sku where id = 1 for update
            SKU.objects.select_for_update().get(id=1)

        2、乐观锁
            乐观锁并不是真实存在的锁，而是在更新的时候，再次判断此时查询的数据与之前是否一致，如果一致，表示没有资源争夺问题，不一致
            则存在资源抢夺，无法执行更新操作
            乐观锁会导致出现脏读问题，所以需要修改数据库的事务隔离级别，将默认的（可重复度）修改为 读 已提交，可解决资源抢夺问题
            update sku set stock = 1 where id = 1 and stock = 3
            SKU.objects.filter(id=1, stock=3).update(stock=1)

        3、任务队列
            将下单的逻辑放到任务队列中，将并行转为串行，所有人排队下单，比如开启只有一个进程的 celery，一个订单一个订单的处理
        """

        # 1、获取当前保存订单所需要的信息
        #     1）获取请求的 user，由于继承了 GenericAPIView，在 GenericAPIView 的 get_serializer 中封装了 request
        user = self.context.get('request').user
        #     2）由于此处 order_id（主键）自己指定，因此需要手动生成。根据时间戳和 user_id 生成 order_id， strftime 将时间戳按照指定格式转成字符串
        order_id = datetime.now().strftime('%Y%m%d%H%M%S') + '%09d' % user.id
        #     3）从前端传入数据获取 address，前端传入 address 的 id，在序列化时已拿到其对象
        address = validated_data.get('address')
        # 先定义默认 total_count 和 total_amount，等拿到 sku 再修改
        #     6）sku.price 获取商品单价 price * total_count 得到 total_amount
        total_count = 0
        total_amount = Decimal(0.00)
        freight = Decimal(0.00)
        #     7）pay_method 从前端获取
        pay_method = validated_data.get('pay_method')
        #     8）根据 pay_method 选择订单状态，根据本次业务需求，如果支付方式为支付宝，则状态为待支付，如果支付方式为现金，则状态为待发货
        status = (models.OrderInfo.ORDER_STATUS_ENUM['UNPAID']
                  if pay_method == models.OrderInfo.PAY_METHODS_ENUM['ALIPAY']
                  else models.OrderInfo.ORDER_STATUS_ENUM['UNSEND'])

        # 为了保障在订单提交的时刻，对于 4 张表的修改可靠安全，手动开启事务
        with transaction.atomic():

            # 保存事务回滚点，一定要放在事务开启后
            save_point = transaction.savepoint()

            # 为了保障在整体过程中，一旦发生异常就进行回滚操作，保证数据一致性，使用 try catch
            try:
                # 2、保存订单基本信息 OrderInfo
                order_info = models.OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=total_count,
                    total_amount=total_amount,
                    freight=freight,
                    pay_method=pay_method,
                    status=status
                )
                # 3、从 redis 中读取购物车中被勾选的信息
                #     4）从 redis hash 中获取购物车中添加的 sku 商品信息，根据 redis set 找出选择的商品
                redis_conn = get_redis_connection('carts')

                #     5）redis hash 中获取所有 sku 的 count -> total_count
                carts_info_key = cartsconst.USER_CARTS_INFO_HASH_KEY + str(user.id)
                selected_info_key = cartsconst.USER_CARTS_INFO_SET_KEY + str(user.id)

                carts_info = redis_conn.hgetall(carts_info_key)
                selected_info = redis_conn.smembers(selected_info_key)
                # 4、遍历购物车中被勾选的信息
                # 此处不使用 goodsmodels.SKU.objects.filter(id__in=selected_info) 需要考虑到 queryset 的缓存特性，会影响下单购买时资源抢夺问题
                # 从 redis 中取出的字符串均为 bytes 类型，但在模型中使用时，会自动转换为其存入时类型，无需手动 decode
                #     4.1 获取 sku 对象
                for sku_id in selected_info:

                    for _ in range(3):
                        # 出现资源抢夺时，允许重新发起请求三次，用于用户可以购买到商品

                        sku = goodsmodels.SKU.objects.get(pk=sku_id)

                        #     4.2 判断库存，先查询商品库存
                        stock = sku.stock
                        buy_count = int(carts_info.get(sku_id))

                        if buy_count > stock:
                            raise serializers.ValidationError('商品 sku_id=%d 的库存不足' % sku.id)

                        #     4.3 减少 sku 库存，增加销量
                        # stock -= buy_count
                        # sku.stock = stock
                        # sku.sales += buy_count
                        # # 保存 sku 修改
                        # sku.save()

                        # 利用乐观锁实现修改库存和销量
                        new_stock = stock - buy_count
                        new_sales = sku.sales + buy_count
                        # update 返回更新的数据条数
                        result = goodsmodels.SKU.objects.filter(id=sku.id, stock=stock
                                                               ).update(stock=new_stock, sales=new_sales)

                        # 判断是否出现资源抢夺情况
                        if result == 0:
                            # result = 0 表示出现资源抢夺，更新失败
                            continue

                        #     4.4 修改 spu 销量
                        spu = sku.goods
                        spu.sales += buy_count
                        # 保存 spu 修改
                        spu.save()

                        # 修改 total_count, total_amount
                        total_count += buy_count
                        total_amount += buy_count * sku.price

                        #     4.5 保存订单商品信息 OrderGoods，一个 订单 对应多个 订单商品信息
                        #   设置除开有默认值的其他七钻
                        models.OrderGoods.objects.create(
                            order=order_info,
                            sku=sku,
                            count=buy_count,
                            price=total_amount
                        )
                        freight += Decimal(10.00)

                        # 如果提交订单成功则跳出 购买尝试 的循环
                        break

                #     4.6 累计计算总数量和总价
                # 5、最后加入邮费和保存订单信息
                order_info.total_count = total_count
                order_info.total_amount = total_amount + freight
                order_info.freight = freight
                order_info.save()

            except Exception:
                # 捕获异常则暴力回滚
                transaction.savepoint_rollback(save_point)
                raise serializers.ValidationError('订单异常')

            else:
                # 未发生异常，则提交事务
                transaction.savepoint_commit(save_point)

        # 6、清除购物车中已结算的商品
        pl = redis_conn.pipeline()

        pl.hdel(carts_info_key, *selected_info)
        # pl.delete(selected_info_key)
        pl.srem(selected_info_key, *selected_info)

        pl.execute()

        return order_info