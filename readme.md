# Требования
Python версии >= 3.6.

Менеджер пакетов Python – pip.

# Установка
```
pip install -r requirements.txt
python manage.py bower install
python manage.py collectstatic
```

# Конфигурация OntoGen
1. Создать файл local_settings.py в корне проекта
2. Задать секретный ключ
```
SECRET_KEY = '% секретный ключ %'
```
3. Задать список разрешенных адресов
```
ALLOWED_HOSTS = [
    '127.0.0.1', 'localhost', ...
]
```
4. Задать параметры подключение к репозиторию SimplyFire
```
SIMPLYFIRE_ADDRESS = '% адрес SimplyFire %'
SIMPLYFIRE_API_VERSION = '% версия API %'
SIMPLYFIRE_TOKEN = '% токен аутентификации %'
SIMPLYFIRE_PROJECT_ID = '% идентификатор проекта %'
```

# Запуск
```
python manage.py runserver
```