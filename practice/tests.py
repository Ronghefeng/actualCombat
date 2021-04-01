import grpc
from django.test import TestCase


# python manage.py test practice.tests.VideoServiceServicerTest
class GRPCServerImplemente(TestCase):
    server = 11

    @classmethod
    def add_to_server(cls):
        raise NotImplementedError('Method not implemented!')

    @staticmethod
    def start_server():

        print('start_server, self.server==%s' % GRPCServerImplemente.server)

    @staticmethod
    def stop_server():
        print('self.server.stop()')

    @classmethod
    def setUpClass(cls):
        print('测试开始')
        cls.add_to_server()
        cls.start_server()

    @classmethod
    def tearDownClass(cls):
        print('测试结束')
        cls.stop_server()


class VideoServiceServicerTest(GRPCServerImplemente, TestCase):
    def test_method1(self):
        print('test......test_method1, print server == %s' % self.server)

    def test_method2(self):
        print('test......test_method2')

    @classmethod
    def add_to_server(cls):
        print('add.... cls.server=%s' % cls.server)
