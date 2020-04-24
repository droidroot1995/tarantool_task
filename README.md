## Key-Value API

Реализовано на языке Python с использованием базы данных Tarantool. Протестировать можно здесь https://alexander-goryakin.droidroot1995.tk/kv

### Установка:

Устанавливаем зависимости с помощью:
> pip install -r requirements.txt

Копируем файл kv.lua в папку:
> /etc/tarantool/instances.available/kv.lua

Создаем symlink:
> ln -s /etc/tarantool/instances.available/kv.lua /etc/tarantool/instances.enabled/kv.lua

Запускаем сервер:
> tarantoolctl start kv

Запускаем в папке kv_api:
> gunicorn -b 0.0.0.0:5000 -w 4 wsgi:app --log-config=gunicorn_logging.conf

### API

#### POST

Путь запроса:

> /kv

Формат запроса:

>{  
> &nbsp; &nbsp; &nbsp; &nbsp;"key": "test",   
> &nbsp; &nbsp; &nbsp; &nbsp;"value": {SOME ARBITRARY JSON}  
>} 

Ответ в случае успешной записи:

>{  
> &nbsp; &nbsp; &nbsp; &nbsp;"message": "inserted",   
> &nbsp; &nbsp; &nbsp; &nbsp;"status": 200  
>} 

Ответ в случае некорректного тела запроса:

>{  
> &nbsp; &nbsp; &nbsp; &nbsp;"message": "invalid request body",   
> &nbsp; &nbsp; &nbsp; &nbsp;"status": 400 
>} 

Ответ в случае, если ключ уже существует:

>{  
> &nbsp; &nbsp; &nbsp; &nbsp;"message": "key already exists",   
> &nbsp; &nbsp; &nbsp; &nbsp;"status": 409  
>} 

#### GET

Формат запроса:

Путь запроса:

> /kv/{key}

Ключ **{key}** являеся строковым значением.

Ответ в случае наличия записи:

>{  
> &nbsp; &nbsp; &nbsp; &nbsp;"value": {SOME ARBITRARY JSON},  
>} 

Ответ в случае отсутствия ключа:

>{  
> &nbsp; &nbsp; &nbsp; &nbsp;"message": "key not found",   
> &nbsp; &nbsp; &nbsp; &nbsp;"status": 404  
>} 


#### PUT

Путь запроса:

> /kv/{key}

Ключ **{key}** являеся строковым значением.

Формат запроса:

>{   
> &nbsp; &nbsp; &nbsp; &nbsp;"value": {SOME ARBITRARY JSON}  
>} 

Ответ в случае успешного обновления записи:

>{  
> &nbsp; &nbsp; &nbsp; &nbsp;"message": "updated",   
> &nbsp; &nbsp; &nbsp; &nbsp;"status": 200  
>} 

Ответ в случае некорректного тела запроса:

>{  
> &nbsp; &nbsp; &nbsp; &nbsp;"message": "invalid request body",   
> &nbsp; &nbsp; &nbsp; &nbsp;"status": 400  
>} 

Ответ в случае, если ключ отсутствует:

>{  
> &nbsp; &nbsp; &nbsp; &nbsp;"message": "key not found",   
> &nbsp; &nbsp; &nbsp; &nbsp;"status": 404   
>} 

#### DELETE

Путь запроса:

> /kv/{key}

Ключ **{key}** являеся строковым значением.

Ответ в случае успешного удаления:

>{  
> &nbsp; &nbsp; &nbsp; &nbsp;"message": "deleted",   
> &nbsp; &nbsp; &nbsp; &nbsp;"status": 200  
>} 

Ответ в случае отсутствия ключа:

>{  
> &nbsp; &nbsp; &nbsp; &nbsp;"message": "key not found",   
> &nbsp; &nbsp; &nbsp; &nbsp;"status": 404   
>} 


#### Превыешение заданного количества запросов в секунду

В случае превышения заданного числа запросов в секунду будет получен следующий ответ от сервера:

>{  
> &nbsp; &nbsp; &nbsp; &nbsp;"message": "too many requests",   
> &nbsp; &nbsp; &nbsp; &nbsp;"status": 429   
>} 

Число запросов можно изменить в файле **app.py** в переменной **limiter**, параметре **default_limits**.

### База данных
Сервер запущен на порту 3301.

Схема базы следующая:

>{  
> &nbsp; &nbsp; &nbsp; &nbsp;{name = 'key', type = 'string'}  
> &nbsp; &nbsp; &nbsp; &nbsp;{name='value', type='map'}   
>} 


Индекс, работающий по параметру **{key}**, задаётся следующим образом:

>{  
> &nbsp; &nbsp; &nbsp; &nbsp;'primary'   
> &nbsp; &nbsp; &nbsp; &nbsp;{type = 'hash', parts = {'key'}}    
>} 


### Тест
На данный момент в базе записано только одно значение **state**, которое можно посмотреть по адресу

>https://alexander-goryakin.droidroot1995.tk/kv/state
