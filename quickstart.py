# -*- coding: utf-8 -*-
import sys
import asyncio
import json
from collections import defaultdict
from sanic.log import logger as log
from sanic import response, Blueprint
from sanic.response import text, html, redirect
from sanic.views import HTTPMethodView, CompositionView
from sanic_demo import app

@app.get('/')
async def test(request):
    return html('Hello World!')


@app.route('/json')
async def test(request):
    """Response Headers Content-Type:application/json"""
    log.debug('Route handler: {}'.format(sys._getframe().f_code.co_name))
    return response.json({'hello': 'world'})


@app.get('/html')
async def test(request):
    return html('<h1>Hello World!</h1>')


@app.route('/tag/<tag>')
async def tag_handler(request, tag):
    """Response Headers Content-Type:text/plain; charset=utf-8"""
    log.debug('Route handler: {}'.format(sys._getframe().f_code.co_name))
    return text('Tag - {}'.format(tag))


@app.route('/number/<integer_arg:int>')
async def integer_handler(request, integer_arg):
    """非负整数参数"""
    log.debug('Route handler: {}'.format(sys._getframe().f_code.co_name))
    return text('Integer - {}'.format(integer_arg))


@app.route('/number/<number_arg:number>')
async def number_handler(request, number_arg):
    """实数参数 包括正负整数和浮点数

    保留原来格式如-000123.0321000 输出Tag - -000123.0321000
    """
    log.debug('Route handler: {}'.format(sys._getframe().f_code.co_name))
    return text('Number - {}'.format(number_arg))


@app.route('/person/<name:[A-z]+>')
async def person_handler(request, name):
    """对参数的限制 只包含字母"""
    log.debug('Route handler: {}'.format(sys._getframe().f_code.co_name))
    return text('Person - {}'.format(name))


@app.route('/folder/<folder_id:[A-z0-9]{0,4}>')
async def folder_handler(request, folder_id):
    """对参数的限制 只包含字母和数字 限定长度不超过4 {m,n} 表示>=m <=n"""
    log.debug('Route handler: {}'.format(sys._getframe().f_code.co_name))
    return text('Folder - {}'.format(folder_id))


# app.route默认是GET methods指定GET或POST
@app.route('/post', methods=['POST'])
async def post_handler(request):
    """使用示例

    http POST http://localhost:8000/post name=John email=john@example.org age=28
    POST request - {'name': 'John', 'email': 'john@example.org', 'age': '28'}
    """
    log.debug('Route handler: {}'.format(sys._getframe().f_code.co_name))
    return text('POST request - {}'.format(request.json))


@app.route('/get', methods=['GET', 'POST'])
async def get_handler(request):
    """使用示例

    http http://localhost:8000/get\?name=John\&email=john@example.org\&age=28
    GET request - {'name': ['John'], 'email': ['john@example.org'], 'age': ['28']}
    """
    log.debug('Route handler: {}'.format(sys._getframe().f_code.co_name))
    return text('GET request - {}'.format(request.args))


# 简化语法 app.post() app.get()
@app.post('/apppost')
async def apppost(request):
    log.debug('Route handler: {}'.format(sys._getframe().f_code.co_name))
    return text('POST request - {}'.format(request.json))

@app.get('/appget')
async def appget(request):
    log.debug('Route handler: {}'.format(sys._getframe().f_code.co_name))
    return text('GET request - {}'.format(request.args))


# add_route使用
async def test_addroute(request, name):
    """http post http://localhost:8000/addroute/world"""
    log.debug('Route handler: {}'.format(sys._getframe().f_code.co_name))
    return text('Hello, {}'.format(name))

# sanic的路由工作顺序是先找url是否404，再检查method是否合理

app.add_route(test_addroute, '/addroute/<name:[A-z]+>', methods=['POST'])


# url_for使用
@app.post('/redirect/<name>')
async def test_urlfor(request, name):
    """redirect to /person/aaa?another_arg=another_arg"""

    log.debug('Route handler: {}'.format(sys._getframe().f_code.co_name))
    # url = app.url_for('person_handler', name=name, another_arg="another_arg")

    # redirect to /person/aaa?arg=arg1%2C&arg=arg2
    url = app.url_for('person_handler', name=name, arg=['arg1,', 'arg2'])
    return redirect(url)


@app.websocket('/feed')
async def feed(request, ws):
    """ws://localhost:8000/feed"""
    while True:
        # data = 'Hi..'
        # await ws.send(data)
        data = await ws.recv()
        await ws.send(data)
        # print(data)


connected = set()
user_agents = defaultdict(int)

@app.websocket('/ws')
async def feed(request, ws):
    """在线人数统计 uv"""
    connected.add(ws)
    ua = request.headers.get('user-agent', 'unkown')
    user_agents[ua] += 1
    log.debug('Open WebSockets: ', len(connected))
    try:
        while True:
            await ws.send(json.dumps({
                'user_agents': user_agents,
                'websockets': len(connected),
            }))
            await asyncio.sleep(0.1)
    finally:
        connected.remove(ws)
        user_agents[ua] -= 1
        if user_agents[ua] == 0:
            user_agents.pop(ua)
        log.debug('Open WebSockets: ', len(connected))


# static静态文件
# http://localhost:8000/static/beauty.jpg
app.static('/static', './static')

# blueprint写法 加前缀
# http://localhost:8000/img/pic/beauty.jpg
bp = Blueprint('bpname', url_prefix='img')
bp.static('/pic', './static')
app.blueprint(bp)


# Class-Based views
class SimpleView(HTTPMethodView):

  def get(self, request):
      return text('I am get method')

  def post(self, request):
      return text('I am post method')

  def put(self, request):
      return text('I am put method')

  def patch(self, request):
      return text('I am patch method')

  def delete(self, request):
      return text('I am delete method')

app.add_route(SimpleView.as_view(), '/class')


# Class-Based views 使用async
class SimpleAsyncView(HTTPMethodView):

  async def get(self, request):
      return text('I am async get method')

app.add_route(SimpleAsyncView.as_view(), '/async')


# Class-Based views url 参数
class NameView(HTTPMethodView):

  def get(self, request, name):
    return text('Hello {}'.format(name))

app.add_route(NameView.as_view(), '/<name>')


# 装饰器 demo  不改变被装饰函数
def decorate(f):
    def deco(*args, **kwargs):
        log.debug('我是装饰器')
        return f(*args, **kwargs)
    return deco


# Class-Based views 装饰器
class ViewWithDecorator(HTTPMethodView):
  decorators = [decorate]

  def get(self, request):
    return text('Hello I have a decorator')

app.add_route(ViewWithDecorator.as_view(), '/deco')


# build a URL for an HTTPMethodView
class SpecialClassView(HTTPMethodView):
    def get(self, request):
        return text('Hello from the Special Class View!')

app.add_route(SpecialClassView.as_view(), '/special', name="special_view")

@app.route('/r')
def index(request):
    url = app.url_for('SpecialClassView') # url = app.url_for('special_view')
    return redirect(url)


# 类似HTTPMethodView  另一个CompositionView的用法
def get_handler(request):
    return text('I am a get method')

view = CompositionView()
view.add(['GET'], get_handler)
view.add(['POST', 'PUT'], lambda request: text('I am a post/put method'))

# Use the new view to handle requests to the base URL
app.add_route(view, '/cv')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)