from grpc_libs import helloworld_pb2
from grpc_libs import helloworld_pb2_grpc


def grpc_hook(server):
    """
    该方法为钩子函数，用于将我们具体的 service 实现类注册进 grpcserver 中
    """

    helloworld_pb2_grpc.add_GreeterServicer_to_server(
        HelloWorldServicer(), server
    )


class HelloWorldServicer(helloworld_pb2_grpc.GreeterServicer):
    """
    该类即为我们实现具体的代码的地方
    """
    pass
