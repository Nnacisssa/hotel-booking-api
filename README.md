# Hotel Booking REST API

Современный асинхронный REST API сервис для бронирования номеров в отелях. Проект разработан на FastAPI с использованием PostgreSQL, Redis, SQLAlchemy 2.0 и JWT-авторизации.

## Основной функционал

- **Авторизация и аутентификация**: Регистрация, вход, хеширование паролей (Bcrypt) и защита эндпоинтов через JWT (Bearer tokens).
- **Управление отелями и номерами**: Просмотр списка отелей, фильтрация по городам, добавление номеров.
- **Бронирование с защитой от овербукинга**: Алгебраическая проверка пересечения дат заезда и выезда.
- **Кэширование (Redis)**: Ускорение чтения списков отелей через Redis с таймаутом жизни кэша (TTL).
- **Фоновые задачи (Background Tasks)**: Асинхронная симуляция отправки подтверждающих e-mail писем без задержки ответа пользователю.
- **Интерактивный веб-интерфейс**: Встроенная демо-страница на HTML/JS (Pico.css).

## Технологический стек

- **Language**: Python 3.11+
- **Framework**: FastAPI, Pydantic v2, Pydantic-Settings
- **Database**: PostgreSQL, SQLAlchemy 2.0 (AsyncIO), Asyncpg
- **Caching**: Redis, aioredis
- **Infrastructure**: Docker, Docker Compose
- **Security**: PyJWT, Passlib, Bcrypt

## Инструкция по запуску

### 1. Клонирование репозитория
```bash
git clone [https://github.com/your-username/hotel-booking-api.git](https://github.com/your-username/hotel-booking-api.git)
cd hotel-booking-api
```

### 2. Настройка виртуального окружения
```bash
python -m venv .venv
```
# Для Windows:
.venv\Scripts\activate
# Для Linux/macOS:
source .venv/bin/activate
pip install -r requirements.txt


### 3. Запуск инфраструктуры в Docker
``` bash
docker-compose up -d
```

### 4. Создание файла .env
Создайте файл .env в корне проекта на основе .env.example:
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/hotel_booking
REDIS_URL=redis://localhost:6379
SECRET_KEY=your_super_secret_key_here
```

### 5. Запуск приложения
```bash
uvicorn app.main:app --reload 
```
Приложение будет доступно по адресам:
1. Веб-интерфейс: http://127.0.0.1:8000/
2. Swagger UI (OpenAPI): http://127.0.0.1:8000/docs

