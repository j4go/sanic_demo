# -*- coding: utf-8 -*-

from sanic import Sanic
from sanic.response import json, text

app = Sanic()


@app.route('/')
async def test(request):
    """Response Headers Content-Type:application/json"""
    return json({'hello': 'world'})


@app.route('/tag/<tag>')
async def tag_handler(request, tag):
    """Response Headers Content-Type:text/plain; charset=utf-8"""
    return text('Tag - {}'.format(tag))


@app.route('/number/<integer_arg:int>')
async def integer_handler(request, integer_arg):
    """非负整数参数"""
    return text('Integer - {}'.format(integer_arg))


@app.route('/number/<number_arg:number>')
async def number_handler(request, number_arg):
    """实数参数 包括正负整数和浮点数

    保留原来格式如-000123.0321000 输出Tag - -000123.0321000
    """
    return text('Number - {}'.format(number_arg))


@app.route('/person/<name:[A-z]+>')
async def person_handler(request, name):
    """对参数的限制 只包含字母"""
    return text('Person - {}'.format(name))


@app.route('/folder/<folder_id:[A-z0-9]{0,4}>')
async def folder_handler(request, folder_id):
    """对参数的限制 只包含字母和数字 限定长度不超过4 {m,n} 表示>=m <=n"""
    return text('Folder - {}'.format(folder_id))


# app.route默认是GET methods指定GET或POST
@app.route('/post', methods=['POST'])
async def post_handler(request):
    """使用示例

    http POST http://localhost:8000/post name=John email=john@example.org age=28
    POST request - {'name': 'John', 'email': 'john@example.org', 'age': '28'}
    """
    return text('POST request - {}'.format(request.json))


@app.route('/get', methods=['GET', 'POST'])
async def get_handler(request):
    """使用示例

    http http://localhost:8000/get\?name=John\&email=john@example.org\&age=28
    GET request - {'name': ['John'], 'email': ['john@example.org'], 'age': ['28']}
    """
    return text('GET request - {}'.format(request.args))


# 简化语法 app.post() app.get()
@app.post('/apppost')
async def apppost(request):
    return text('POST request - {}'.format(request.json))

@app.get('/appget')
async def appget(request):
    return text('GET request - {}'.format(request.args))



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)