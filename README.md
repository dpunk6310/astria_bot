# Astria Bot

## Deploy

### Запуск проекта

#### 1. Установка зависимостей

Перед запуском проекта убедитесь, что у вас установлены [Docker](https://www.docker.com/) и [Docker Compose](https://docs.docker.com/compose/).

#### 2. Настройка .env файла

В корне проекта создайте файл `.env` и добавьте в него следующие данные:

```env
DJANGO_SECRET_KEY=r7j
DJANGO_DEBUG=True

POSTGRES_DB_NAME=dfg33223d2f2467HGjfg
POSTGRES_USER=HJffr2323thjthd6kfyjhgg
POSTGRES_PASSWORD=HJVr67yjrj4y332FDT34gkhd
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432

REDIS_PASSWORD=hjvTj4y3y333iuyfhjvhgdty5
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
BOT_TOKEN=
PLACE=test
DJANGO_URL=http://localhost:8000
```

- DJANGO_SECRET_KEY: Секретный ключ Django.
- DJANGO_DEBUG: Включение режима отладки в Django.
- POSTGRES_DB_NAME, POSTGRES_USER, POSTGRES_PASSWORD: Данные для подключения к базе данных PostgreSQL.
- REDIS_*: Данные для подключения к Redis.
- BOT_TOKEN: Токен для вашего бота (если используется).
- PLACE: Название места, которое используется в проекте.
- DJANGO_URL: URL вашего Django приложения.

#### 3. Запуск базы данных
Для запуска контейнера с базой данных PostgreSQL используйте команду:

```bash
docker-compose -f docker-compose.db.yml up --build -d
```
Это создаст и запустит контейнер с базой данных.


#### 4. Запуск приложения Django
После того как база данных запустится, можно запускать основной контейнер с приложением Django:

```bash
docker-compose up -d
```

#### 5. Создание суперпользователя Django
После запуска контейнера с Django, зайдите в контейнер и создайте суперпользователя:

```bash
docker exec -it <container_name> bash
python manage.py createsuperuser
```

#### 6. Доступ к приложению
Теперь ваше приложение доступно по адресу http://localhost:8000.

#### 7. Остановка контейнеров
Чтобы остановить контейнеры, выполните:

```bash
docker-compose down
```
