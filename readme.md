# WebChat – Setup Guide

## 1. Clone Repository

```bash
git clone https://github.com/yashpatkar-shubpy/webchat_django_channels.git
cd backend
```

---

## 2. Create Virtual Environment and Activate Environment

```bash
python -m venv venv

venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Apply Migrations

```bash
python manage.py migrate
```

---

## 5. Start Redis

Ensure Redis is running locally. The application expects Redis to be accessible on port `6380`.

You can start Redis using a local installation or a Docker container.

### Local Installation

To start Redis locally on port `6380`:

```bash
redis-server --port 6380
```

### Docker Container

To start a Redis container mapped to host port `6380`:

```bash
docker run -d --name webchat-redis -p 6380:6379 redis:latest
```

---

## 6. Start Celery Worker

```bash
celery -A backend worker --loglevel=info --pool=solo
```

---

## 7. Env file

```bash
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
```

---

## 8. Run Development Server

```bash
python manage.py runserver
```

Application URL:

```
http://127.0.0.1:8000/
```

WebSocket endpoint:

```
ws://127.0.0.1:8000/ws/chat/<conversation_id>/
```