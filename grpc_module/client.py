# 客户端
import grpc
import proto.matsuri_pb2 as pb2
import proto.matsuri_pb2_grpc as pb2_grpc

# 定义一个频道, 连接至服务端监听的端口
channel = grpc.insecure_channel("127.0.0.1:22333")
# 生成客户端
client = pb2_grpc.MatsuriStub(channel=channel)

# 然后我们就可以直接调用Matsuri服务里面的函数了
print("准备使用服务了~~~~")
while True:
    name, age = input("请输入姓名和年龄, 并使用逗号分割:").split(",")
    # 调用函数, 传入参数request, name和age位于request中
    response = client.hello_matsuri(pb2.request(name=name, age=int(age)))
    # result位于返回值response中, 直接通过属性访问的形式获取
    print(response.result)
