1，创建自己GitHub地址
git clone https://github.com/jake20001/helloflask.git
2，安装pipenv
pip install pipenv
3，创建helloflask的虚拟环境
pipenv install
4，进入虚拟环境
pipenv shell


flask学习点：
1，在当前要运行的目录下配置环境：.flaskenv  FLASK_APP=app.py (如何获取这个环境变量?)
E:\flaskdemo\helloflask_jake\helloflask\demos\hello>flask run --host=0.0.0.0 --port=8000
也可以进入虚拟环境运行
(helloflask-Hq2U_PR1) E:\flaskdemo\helloflask_jake\helloflask\demos\hello>flask run --host=0.0.0.0
2,内网穿透和访问工具：ngrok（https://ngrok.com/）, Localtunnel(https://localtunnel.github.io/www/)
3,app.config['全大写']
app.config['SECRET_KEY'] = 'admin123456'如何生效？






addtions:
1,http://api.jquery.com/
