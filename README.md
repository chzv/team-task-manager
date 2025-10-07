# Team Task Manager

Веб-приложение и Telegram-бот для управления задачами в команде.

**Стек:** Django + DRF · Channels (WebSocket) · Celery · Redis · Aiogram · Postgres · Docker Compose

## Возможности
- Аутентификация (Django auth).
- Команды → списки задач → задачи.
- Назначение исполнителя и дедлайна, отметка “выполнено”.
- Обновления в реальном времени (WebSocket): создание/изменение/выполнение задач.
- Уведомления:
  - Если пользователь активен в вебе — тост внутри приложения.
  - Если не активен — сообщение в Telegram.
- Telegram-бот:
  - `/link` — привязка аккаунта к Telegram.
  - `/tasks` — список назначенных задач.
  - `/done <id>` — завершить задачу.

## Сервисы в Docker
- **web** — Django + Daphne (ASGI).
- **worker** — Celery worker.
- **beat** — Celery beat (периодические задачи, например проверка просрочки).
- **bot** — Aiogram-поллинг.
- **redis** — брокер Celery и бэкенд Channels.
- **db** — PostgreSQL.

## Быстрый старт

1) Создайте файл окружения:
```bash
cp .env.example .env

2) Запустите стек:
docker compose up --build

3) Примените миграции и создать администратора:
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
(Опционально) собрать статику:
docker compose exec web python manage.py collectstatic --noinput

4) Зайдите в админку:
http://localhost:8000/admin/
Создайте тестовую команду, список и пару задач.

5) Привязка Telegram
Напишите боту /link — бот вернёт 6-значный код.
В веб-приложении откройте страницу привязки (или профиль) и введите код — произойдёт связывание с пользователем.

Проверка:
Если в вебе онлайн, уведомление будет тостом в интерфейсе.
Если офлайн (нет heartbeat в последние 30 сек), придёт сообщение в Telegram.

## Переменные окружения (.env)

.env.example, основные:

DEBUG — 0/1
SECRET_KEY — секрет Django
ALLOWED_HOSTS — хосты, через запятую (* для локали)
DATABASE_URL — postgres://tasker:tasker@db:5432/tasker
REDIS_URL — redis://redis:6379/0
CHANNEL_LAYER_URL — redis://redis:6379/1
SERVICE_TOKEN — сервисный токен (бот → API)
BOT_TOKEN — токен Telegram-бота (от @BotFather)
API_BASE — http://web:8000/api (для контейнера бота)

## Реальное время (Channels)

User socket: /ws/user/ — тосты/события для конкретного пользователя.
Team socket: /ws/team/<team_id>/ — широковещательные события для команды.
Клиент шлёт heartbeat, чтобы сервер понимал “онлайн ли пользователь”.
Celery задачи
apps.tasks.tasks.notify_assigned_task — уведомление о назначении.
apps.tasks.tasks.check_overdue — раз в минуту помечает просрочку и шлёт уведомления.
API (фрагмент)
POST /api/telegram/create_code/ — бот запрашивает код (заголовок Authorization: Bearer <SERVICE_TOKEN>).
POST /api/telegram/confirm/ — веб привязывает код к текущему пользователю.
GET /api/tg/tasks/ — бот получает задачи (заголовки: Authorization: Bearer <SERVICE_TOKEN>, X-TG-USER: <tg_id>).
POST /api/tg/tasks/<id>/done/ — бот завершает задачу.
Траблшутинг
Порт 5432 занят: либо останови локальный Postgres, либо убери публикацию порта в docker-compose.yml.
whitenoise не найден: проверь, что он есть в requirements.txt, пересобери образ.
AlreadyRegistered в админке: убедись, что модели регистрируются один раз.
WS/CSRF: укажи CSRF_TRUSTED_ORIGINS=http://localhost:8000 в .env.

## Скрипты для проверки 

# миграции
docker compose exec web python manage.py migrate

# суперюзер
docker compose exec web python manage.py createsuperuser

# проверка воркера
docker compose logs -f worker

# проверка beat (периодика)
docker compose logs -f beat

