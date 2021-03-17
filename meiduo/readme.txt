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