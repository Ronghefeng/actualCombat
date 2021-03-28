一、REST framework 自动生成接口文档
    接口文档能自动生成的是继承自 APIView 及其子类的视图
    1、安装依赖
        pip install coreapi


二、前端资源管理
    1、安装 nvm
        git clone https://github.com/nvm-sh/nvm.git
        ./nvm/install.sh
        配置环境变量
            export NVM_DIR="$HOME/.nvm"
            [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
            [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
    2、安装 node
        nvm install node
    3、安装 live-server
        npm install -g live-server
        live-server 前端服务器

三、自动生成依赖文件 requiert.txt
    pip install pipreqs
    pipreqs .
    安装 requiert.txt：pip install -r requiert.txt


四、忽略日志文件
    .gitignore ：添加 logs/*.log
    .gitkeep : 不忽略当前文件夹

五、Django 模型建立索引
        # 唯一1约束   其中goods和user不能重复
        unique_together = ["goods", "user"]
        # 联合索引
        index_together = ["user", "goods"]

    related_name：从 一 查多
    related_query_name：从多查一

六、进程、线程、协程（异步函数）
    1、多线程
        1）引入模块
        from threading import Thread
        2）线程的新建、启动、等待
            新建：t = Thread(target=func_nam, args=args) # 函数名 func_nam；args 传给函数的参数
            启动：t.start()
            等待：t.join()
        3）数据通信
            import queue
            q = queue.Queue()
            q.put(item) # 传入数据
            q.get(item) # 取出数据
        4）线程安全加锁
            from threading import Lock
            lock = Lock()
            with lock:
                do something
        5）池化技术
            from concurrent.futures import TreadPoolExecutor
            with TreadPoolExecutor() as executer:
                # 批量传入
                results = executer.map(func_nam, args)  # 可以传多个参数，表示func_nam(1)、func_nam(2)...
                # 单个传入
                future = executer.submit(func_nam, 1)
                result = future.result()
    2、多进程
        1）引入模块
        from multiproceesing import Process
        2）线程的新建、启动、等待
            新建：p = Process(target=func_nam, args=args) # 函数名 func_nam；args 传给函数的参数
            启动：p.start()
            等待：p.join()
        3）数据通信
            from multiproceesing import Queue
            q = Queue()
            q.put(item) # 传入数据
            q.get(item) # 取出数据
        4）线程安全加锁
            from multiproceesing import Lock
            lock = Lock()
            with lock:
                do something
        5）池化技术
            from concurrent.futures import ProcessPoolExecutor
            with ProcessPoolExecutor() as executer:
                # 批量传入
                results = executer.map(func_nam, args)  # 可以传多个参数，表示func_nam(1)、func_nam(2)...
                # 单个传入
                future = executer.submit(func_nam, 1)
                result = future.result()
    2、协程
        1）使用协程
            import asynico

            urls = []

            loop = asynico.get_event_loop() # 获取循环

            asynic def test(url):
                await get_url(url)  # 执行该 IO 操作时可以切换到下一个任务
            
            # 创建协程任务列表
            tasks = [loop.create_task(test(url) for url in urls)]

            # 执行事件列表
            loop.run_until_complete(asynico.wait(tasks))

        2）信号量，控制协程数
            asynico.Semophere(max_size)

七、curl
    查看请求花费时间：time curl url 

八、redis 基本操作
    1、数据库
        选择数据库：select 0[1,2,3..15]
        连接数据库：redis-cli
    2、查询当前数据库中所有 key：keys *
    3、基本命令
        1）string
            设置值： set(key, timeout, value)
            获取值：get key value
        2）list
            获取值：lrange(key, start, stop)
            设置值：lpush(key, value1, value2...)
            删除值：lrem(key, count, value)
        3）hash
            获取值：hget(key, field); hgetall(key)
            设置值：hset(key, field, value); hincrby(key, filed, count)
            删除值：hdel(key, field)
        4）set
        5）zset
