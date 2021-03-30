import helloworld_pb2
import helloworld_pb2_grpc


def grpc_hook(server):
    helloworld_pb2_grpc.add_GreeterServicer_to_server(
        HelloWorldServicer(), server
    )


class HelloWorldServicer(helloworld_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        response = helloworld_pb2.HelloReply(message="Hello " + request.name)
        return response
        