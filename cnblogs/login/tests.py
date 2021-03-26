from django.test import TestCase

# Create your tests here.

class A:

    def one(self):
        print('one')

    @classmethod
    def two(cls):
        print('two')
    
    @staticmethod
    def three():
        print('three')


if __name__ == '__main__':
    a = A()
    a.one()
    a.two()
    a.three()
    A.one(a)
    A.two()
    A.three()
