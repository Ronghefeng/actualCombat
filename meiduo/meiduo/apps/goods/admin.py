from django.contrib import admin
from django.contrib.admin import register
from . import models
from celery_tasks.html.tasks import generate_goods_list_html


"""
商品列表展示页（用户点击第三级分类，所展示的页面）
将数据变更频率不高的模块（例如 需要运营在 admin 站点上架的信息）做成静态化页面
区别于首页静态化模块，该页面的数据访问频率较低，不需要通过定时任务主动更新，可以采用监听机制，
在 admin 进行新政、修改、删除 等操作时，即触发生成静态化页面的操作
"""

class GoodsCategoryAdmin(admin.ModelAdmin):
    """
    GoodsCategory 站点管理
    站点的修改、新增等操作均会触发 ModelAdmin 中的 save_model 方法
    站点上的删除会触发 ModelAdmin 的 delete_model 方法
    这些操作均会引起数据的变更，因此需要重写，在该操作后重新生成静态化页面
    由于生成静态化页面是一个耗时，且无需立即反馈给操作用户的行为，因此采用异步任务方式执行
    """

    def save_model(self, request, obj, form, change):
        """
        运营人员在 admin 站点点击 保存 时，会执行本方法
        request：保存时本次请求的对象
        obj：本次要保存的模型对象
        form：admin 中表单
        change：是否修改，在保存时默认为 True，不会区校验内容是否有变更
        """
        obj.save()

        # 生成新的 list.html 文件，采用异步执行
        generate_goods_list_html.delay()

    def delete_model(self, request, obj):
        """
        运营人员在 admin 站点点击 删除 时，会执行本方法
        """
        obj.delete()

        # 生成新的 list.html 文件，采用异步执行
        generate_goods_list_html.delay()


@admin.register(models.GoodsChannel)
class GoodsChannelAdmin(admin.ModelAdmin):
    """
    GoodsCategory 站点管理
    站点的修改、新增等操作均会触发 ModelAdmin 中的 save_model 方法
    站点上的删除会触发 ModelAdmin 的 delete_model 方法
    这些操作均会引起数据的变更，因此需要重写，在该操作后重新生成静态化页面
    由于生成静态化页面是一个耗时，且无需立即反馈给操作用户的行为，因此采用异步任务方式执行
    """

    def save_model(self, request, obj, form, change):
        """
        运营人员在 admin 站点点击 保存 时，会执行本方法
        request：保存时本次请求的对象
        obj：本次要保存的模型对象
        form：admin 中表单
        change：是否修改，在保存时默认为 True，不会区校验内容是否有变更
        """
        obj.save()

        # 生成新的 list.html 文件，采用异步执行
        generate_goods_list_html.delay()

    def delete_model(self, request, obj):
        """
        运营人员在 admin 站点点击 删除 时，会执行本方法
        """
        obj.delete()

        # 生成新的 list.html 文件，采用异步执行
        generate_goods_list_html.delay()


admin.site.register(models.SKU)
admin.site.register(models.Brand)
admin.site.register(models.Goods)

# 将站点管理类绑定模型类
# admin.site.register(模型类, 站点管理模型类)
admin.site.register(models.GoodsCategory, GoodsCategoryAdmin)
# 使用装饰器注册模型，且绑定模型站点管理类
# admin.site.register(models.GoodsChannel, GoodsChannelAdmin)
admin.site.register(models.GoodsSpecification)
admin.site.register(models.SKUImage)
admin.site.register(models.SKUSpecification)
admin.site.register(models.SpecificationOption)
