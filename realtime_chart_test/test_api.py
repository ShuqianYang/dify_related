# Flask是使用Flask框架需要导入的依赖
from flask import Flask

# app是Flask构建的实例
app = Flask(__name__)

# @app.route('/')

# 这里定义了HTTP请求的方式，如 GET/POST... 默认为GET请求
# 我们也可以自定义请求方式，如 @app.post('/')

# ('/')中 / 代表请求的URL路径，此时浏览器中访问路径为 127.0.0.1:5000
# ('/hello') 此时浏览器中访问路径为 127.0.0.1:5000/hello

@app.route('/hello')
def hello_world():  # put application's code here
    return 'Hello World!'

# def为python中定义的函数
# hello_world()是函数名
# return后面的即为HTTP请求返回的结果


if __name__ == '__main__':
    app.run()

# app.run() 运行这个实例
# 默认本机访问，默认5000端口
# 我们可以进行自定义
# 如 app.run(host='0.0.0.0', port=5001)
# '0.0.0.0'表示允许全部主机访问，port=5001 指定端口为5001
