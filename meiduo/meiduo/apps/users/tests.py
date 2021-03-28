from rest_framework import status
from rest_framework.test import APITestCase


class UserViewTests(APITestCase):
    # 初始数据加载，可使用manage.py dumpdata [app_label app_label app_label.Model]生成
    # xml/yaml/json格式的数据
    # 一般放在每个应用的fixtures目录下, 只需要填写json文件名即可，django会自动查找
    # 此测试类运行结束后，会自动从数据库里销毁这份数据
    # fixtures = ['user.json']
    # python manage.py test --keepdb 可以保持数据库，来避免每次执行单测时需要重建数据库的问题，提高执行速度
    # 运行命令：../../manage.py test users.tests.UserViewTests

    def setUp(self):
        # 在类里每个测试方法执行前会运行
        # 在此方法执行前，django会运行以下操作
        # 1. 重置数据库，数据库恢复到执行migrate后的状态
        # 2. 加载fixtures数据
        # 所以每个测试方法里对数据库的操作都是独立的，不会相互影响
        print('UserViewTests 单个方法测试开始')

    def tearDown(self):
        # 在类里每个方法结束执行后会运行
        print('UserViewTests 单个方法测试结束')

    @classmethod
    def setUpClass(cls):
        # 在类初始化时执行，必须调用super
        print('UserViewTests 测试开始')

    @classmethod
    def tearDownClass(cls):
        # 在整个测试类运行结束时执行，必须调用super
        print('UserViewTests 测试结束')

    def test_user_register_success(self):
        """APP用户登录接口成功情况"""
        # path使用硬编码，不要使用reverse反解析url，以便在修改url之后能及时发现接口地址变化，并通知接口使用人员
        url = '/users/'
        # 请求提交的数据，一般随机生成
        data = {
            'username': '15999999999',
            'password': '111111',
            'password2': '111111',
            'sms_codes': '123456',
            'allow': True
        }
        response = self.client.post(url, data)
        # response.data是字典对象
        # response.content是json字符串对象
        self.assertEquals(response.status_code,
                          status.HTTP_200_OK,
                          '登录接口返回状态码错误: 错误信息: {}'.format(response.content))
        self.assertIn('token', response.data, '登录成功后无token返回')