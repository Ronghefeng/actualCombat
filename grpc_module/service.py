# 服务端
# 导入grpc第三方库
import grpc
# 导入自动生成的两个py文件
import proto.matsuri_pb2 as pb2
import proto.matsuri_pb2_grpc as pb2_grpc


class Matsuri(pb2_grpc.MatsuriServicer):
    # 我们在protobuf里面创建的服务叫Matsuri, 所以会给我们提供一个名为MatsuriServicer的类
    # 我们直接继承它即可, 当然我们这里的类名叫什么就无所谓了

    # 我们定义的服务里面有一个hello_matsuri的函数
    def hello_matsuri(self, request, context):
        """
        request就是相应的参数(载体): name、age都在里面
        :param request:
        :param context:
        :return:
        """
        name = request.name
        age = request.age

        # 里面返回是response, 这个response内部只有一个字符串类型的result
        result = f"name is {name}, {age} years old"
        # result需要放在response里面
        return pb2.response(result=result)


if __name__ == '__main__':
    # 创建一个gRPC服务
    # 里面传入一个线程池, 我们这里就启动4个线程吧
    from concurrent.futures import ThreadPoolExecutor

    grpc_server = grpc.server(ThreadPoolExecutor(max_workers=4))
    # 将服务注册到gRPC服务中
    pb2_grpc.add_MatsuriServicer_to_server(Matsuri(), grpc_server)
    # 绑定ip和端口
    grpc_server.add_insecure_port("127.0.0.1:22333")
    # 启动服务
    grpc_server.start()

    # 注意: 如果直接这么启动的话, 会发现程序启动之后就会立刻停止
    # 个人猜测, 里面的线程应该是守护线程, 主线程一结束服务就没了
    # 所以我们采用一个死循环
    import time

    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        # 当按下Ctrl+C, 终止服务
        grpc_server.stop(0)
