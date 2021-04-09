from ..grpc_libs import helloworld_pb2
from ..grpc_libs import helloworld_pb2_grpc
# from extra_apps.grpc_libs import helloworld_pb2, helloworld_pb2_grpc

import time


def grpc_hook(server):
    helloworld_pb2_grpc.add_GreeterServicer_to_server(
        helloworld_pb2_grpc.GreeterServicer(), server)


class HelloWorldServicer(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        print('sayhello')
        # 一元模式(在一次调用中, 客户端只能向服务器传输一次请求数据, 服务器也只能返回一次响应)
        # unary-unary(In a single call, the client can only send request once, and the server can
        # only respond once.)
        response = helloworld_pb2.HelloReply(message="Hello " + request.name)
        return response

    def SayHelloClientStreaming(self, request_iterator, context):
        # 客户端流模式（在一次调用中, 客户端可以多次向服务器传输数据, 但是服务器只能返回一次响应）
        # stream-unary (In a single call, the client can transfer data to the server several times,
        # but the server can only return a response once.)
        names = ""
        for request in request_iterator:
            names += request.name + ","

        response = helloworld_pb2.HelloReply(message="Hello " + names[:-1])
        return response

    def SayHelloServerStreaming(self, request, context):
        # 服务端流模式（在一次调用中, 客户端只能一次向服务器传输数据, 但是服务器可以多次返回响应）
        # unary-stream (In a single call, the client can only transmit data to the server at one time,
        # but the server can return the response many times.)
        def response_messages():
            for i in range(5):
                response = helloworld_pb2.HelloReply(
                    message="Hello {0} ------ {1}".format(
                        request.name,
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                    ))
                yield response
                if i < 4:
                    time.sleep(5)

        return response_messages()

    def SayHelloBidirectionalStreaming(self, request_iterator, context):
        # 双向流模式 (在一次调用中, 客户端和服务器都可以向对方多次收发数据)
        # stream-stream (In a single call, both client and server can send and receive data
        # to each other multiple times.)
        for request in request_iterator:
            response = helloworld_pb2.HelloReply(
                message="Hello {0} ------ {1}".format(
                    request.name,
                    time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                ))
            yield response
