# Megano
Интернет-магазин написанный на python/django

### Стек:
- Python
- Django
- DRF
- Nginx
- Postgres
- docker-compose
- Docker


Для развертки проекта (через консоль):
1. 
    ```
    git clone <this repo>
    ```
    

2. Активировать venv
3.
    ```
    pip install requirements.txt
    ```

4.
    ```
    python manage.py migrate
    ```
   
5. 
    ```
    python manage.py loaddata catalog_dump
    ```
    
6. 
    ```
    python manage.py runserver
    ```

Для развертки проекта (через Docker):<br>
1.
    ```
    git clone <this repo>
    ```
    <br>
2.
    ```
    Создать .env и .env.db файлы в корне проекта
    ```
    .env (базовый шаблон):
    ```
    SECRET_KEY=your_secret_key
    DEBUG=True
    ```
    .env.db
    ```
    POSTGRES_USER=user
    POSTGRES_PASSWORD=user
    POSTGRES_DB=user_db
    ```
   <br>
3.
    ```
    docker-compose up --build
    ```
    <br>

Сайт запускается на 8000 порту
