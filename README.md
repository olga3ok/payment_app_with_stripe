# Payment App with Stripe

## Описание
Сервер, который взаимодействует в тестовом режиме со Stripe API и создает платежные формы (Stripe Session или Stripe Payment Intent)

## Использованные технологии
- **Backend**: Django, Django REST Framework, PostgreSQL
- **Контейнеризация**: Docker, Docker Compose

## Возможности
- Просмотр информации о проекте, товарах и заказах
- Создание платежных форм Stripe Session или Stripe Session Intent

- Просмотр информации о товаре: http://127.0.0.1:8000/item/{id}/
- Просмотр информации о заказе: http://127.0.0.1:8000/order/{id}/
- Создание Stripe Session для товара: http://127.0.0.1:8000/api/items/{id}/buy/
- Создание Stripe Payment Intent для товара: http://127.0.0.1:8000/api/items/{id}/payment_intent/
- Создание Stripe Session для заказа: http://127.0.0.1:8000/api/orders/{id}/buy/
- Создание Stripe Payment Intent для заказа: http://127.0.0.1:8000/api/orders/{id}/payment_intent/

## Установка

1. Клонируйте репозиторий:
   ```
   git clone git@github.com:olga3ok/payment_app_with_stripe.git
   ```
   2. Перейдите в директорию проекта и создайте файл .env с настройками Django и PostreSQL:
      ```
      DJANGO_SECRET_KEY=
      DEBUG=
      ALLOWED_HOSTS=

      STRIPLE_API_KEY=

      POSTGRES_USER=
      POSTGRES_PASSWORD=
      POSTGRES_DB=
      DB_HOST=      # Для запуска при помощи Docker укажите "db"
      DB_PORT=5432
      ```
## Запуск
### Docker
```
docker-compose up --build
```
Приложение будет доступно по адресу http://localhost:8000, информация о проекте: http://localhost:8000/api/docs

Для использования админ панели создайте пользователя:
```
docker-compose exec -it backend bash
python manage.py createsuperuser
```
### Backend
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app/manage.py migrate
python app/manage.py runserver
```

Backend будет доступен по адресу http://localhost:8000
