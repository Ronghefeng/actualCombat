# grpc 参考链接：https://www.codeker.com/post/zai-django-zhong-shi-yong-grpc-kuang-jia/#SayHelloBidirectionalStreaming-%E5%8F%8C%E5%90%91%E6%B5%81%E6%A8%A1%E5%BC%8F
# grpc 服务模式，在服务端实现
    # 1、一元模式：客户端只允许发一次请求，服务端只响应一次
    # 2、客户端流模式：允许客户端发送多次请求，服务端响应一次
    # 3、服务端流模式：客户端发送一次请求，服务端响应多次
    # 4、双向流模式：客户端、服务端允许多次发送请求，多次响应
