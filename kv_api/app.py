import json

import tarantool

from flask import Flask, jsonify, request
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=['2 per second'],
)

# подключаемся к серверу и к необходимому спейсу
c = tarantool.connect('localhost', 3301, user='api_user', password='secret')
space = c.space('api')



@app.errorhandler(429)
def ratelimit_handler(e):
    app.logger.warning(f'[ratelimit_handler]: too many requests')
    return jsonify({'message': 'too many requests', 
                    'status': 429}), 429



@app.route('/kv/<string:key>', methods=['GET'])
def get_value(key):
    
    # ищем запись в базе
    val = space.select(key)
    
    if val.data == []:
        app.logger.warning(f'[get_value]: key not found: {key}')
        return jsonify({'message': 'key not found', 
                        'status': 404}), 404
        
    else:
        app.logger.info(f'[get_value]: found data on key: {key}') 
        return jsonify({'value': val[0][1]})
    

    
@app.route('/kv/<string:key>', methods=['PUT'])
def update_value(key):
    
    val = space.select(key)
    
    # получаем тело запроса
    data = request.data
    
    if val.data == []:
        app.logger.warning(f'[update_value]: key not found: {key}')
        return jsonify({'message': 'key not found', 
                        'status': 404}), 404
    else:
        try:
            # проверка body на корректность
            dat = json.loads(data)
            
            if not 'value' in dat:
                app.logger.warning(f'[update_value]: invalid request body: {data}')
                return jsonify({'message': 'invalid request body', 
                                'status': 400}), 400
            
            # обновляем данные
            space.replace((key, dat['value']))
            
            app.logger.info(f"[update_value]: updated data on key: {key} with value: {dat['value']}") 
            
            return jsonify({'message': 'updated', 
                            'status': 200}), 200
            
        except Exception:
            app.logger.warning(f'[update_value]: invalid request body: {data}')
            return jsonify({'message': 'invalid request body',
                            'status': 400}), 400
            

            
@app.route('/kv', methods=['POST'])
def insert_value():
    
    data = request.data
    
    try:
        dat = json.loads(data)
        
        if (not 'key' in dat) or (not 'value' in dat):
            app.logger.warning(f'[insert_value]: invalid request body: {data}')
            return jsonify({'message': 'invalid request body', 
                            'status': 400}), 400
            
        key = dat['key']
        
        val = space.select(key)
        
        if val.data == []:
            
            # добавляем данные в базу
            space.insert((key, dat['value']))
            
            app.logger.info(f"[insert_value]: inserted data on key: {key} with value: {dat['value']}") 
            
            return jsonify({'message': 'inserted', 
                            'status': 200}), 200
        else:
            app.logger.warning(f'[insert_value]: key already exists: {key}')
            return jsonify({'message': 'key already exists', 
                            'status': 409}), 409
        
    except Exception:
        app.logger.warning(f'[insert_value]: invalid request body: {data}')
        return jsonify({'message': 'invalid request body', 
                        'status': 400}), 400
        

        
@app.route('/kv/<string:key>', methods=['DELETE'])
def delete_value(key):
    
    val = space.select(key)
    
    if val.data == []:
        app.logger.warning(f'[delete_value]: key not found: {key}')
        return jsonify({'message': 'key not found', 
                        'status': 404}), 404
    else:
        # удаляем данные из базы
        space.delete(key)
        
        app.logger.info(f'[delete_value]: delete data on key: {key}')    
            
        return jsonify({'message': 'deleted', 
                        'status': 200}), 200        

        
        
if __name__ == '__main__':
    import logging
    from logging.handlers import RotatingFileHandler
    
    handler = RotatingFileHandler('kv_api.log', maxBytes=5242880, backupCount=10)
    handler.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0', port='5000', debug=True)