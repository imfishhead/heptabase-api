from flask import Flask, request
from flask_caching import Cache
import requests
import time
import json
from flask_cors import CORS

# Jiang 的数字花园 ID
HEPTABASE_WHITEBOARD_ID = '7673672889158c0a8354f4ad8b0e9ee32e7d24d26b697f8d59c665b79da051cf'

# 存储 heptabase base 数据
HEPTABASE_DATA = {'result': 'erro', 'data': {}, 'time': ''}


def get_whiteborad_id():
    '''
    获取 whiteborad ID
    '''
    whiteboard_id = request.args.get('whiteboard_id')
    if(whiteboard_id):
        return whiteboard_id
    else:
        return None


def get_hepta_data(whiteboard_id):
    '''
    获取 heptabase 数据
    '''

    req = requests.get(
        'https://app.heptabase.com/api/whiteboard/?secret='+whiteboard_id)
    if(req.status_code != 200):
        return {'code': req.status_code, 'data': ''}
    else:
        return {'code': req.status_code, 'data': json.loads(req.text)}


app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'SimpleCache'})
CORS(app, supports_credentials=True)


@app.route('/')
# @cache.cached(timeout=30, query_string=True)  # 设置缓存的超时时间（以秒为单位）
def home():
    global HEPTABASE_DATA

    whiteboard_id = get_whiteborad_id()
    cache_key = f'{whiteboard_id}'

    if cache.get(cache_key):  # 如果缓存存在，则直接从缓存中提取数据
        return cache.get(cache_key)['data']
    else:

        if(whiteboard_id):
            req = get_hepta_data(whiteboard_id)
        else:
            # 返回 Jiang 的数字花园数据
            with open('data.json', mode='r') as my_file:
                req = my_file.read()
                req = json.loads(req)
                return {'result': 'success', 'code': req['code'],
                        'data': req['data'], 'time': int(time.time())}

        HEPTABASE_DATA = {'result': 'success', 'code': req['code'],
                          'data': req['data'], 'time': int(time.time())}
        return HEPTABASE_DATA


@app.route('/update')
def update():
    '''
    获取 hepta 数据存储到全局变量中
    '''
    global HEPTABASE_DATA

    whiteboard_id = get_whiteborad_id()
    cache_key = f'{whiteboard_id}'

    req_json = get_hepta_data(whiteboard_id)
    HEPTABASE_DATA = {'result': 'success',
                      'data': req_json, 'time': int(time.time())}

    cache.set(cache_key, HEPTABASE_DATA, timeout=3600)  # 更新缓存并设置新的超时时间

    return HEPTABASE_DATA


@app.route('/about')
def about():
    return 'About Page Route'


@app.route('/portfolio')
def portfolio():
    return 'Portfolio Page Route'


@app.route('/contact')
def contact():
    return 'Contact Page Route'


@app.route('/api')
def api():
    with open('data.json', mode='r') as my_file:
        text = my_file.read()
        return text


if __name__ == '__main__':
    app.run(debug=True)
