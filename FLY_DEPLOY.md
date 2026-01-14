# Деплой на Fly.io

Инструкция по деплою Discord Random Bot на платформу Fly.io.

## Предварительная подготовка

### 1. Создай Discord бота

1. Перейди на https://discord.com/developers/applications
2. Нажми **New Application** и дай имя боту
3. Перейди в раздел **Bot** → **Add Bot**
4. Скопируй **Token** (он понадобится для настройки)
5. Включи **Privileged Gateway Intents:**
   - ✅ Presence Intent
   - ✅ Server Members Intent
   - ✅ Message Content Intent

### 2. Пригласи бота на сервер

1. В **OAuth2** → **URL Generator**
2. Scopes: `bot` + `applications.commands`
3. Bot Permissions:
   - Send Messages
   - Embed Links
   - Use Slash Commands
   - View Channels
4. Открой сгенерированный URL и выбери сервер

---

## Установка Fly.io CLI

### macOS/Linux:
```bash
curl -L https://fly.io/install.sh | sh
```

### После установки:
```bash
fly auth login
```

---

## Деплой

### Шаг 1: Войди в директорию проекта
```bash
cd discord-random-bot
```

### Шаг 2: Создай приложение на Fly.io
```bash
fly launch
```

Во время создания:
- Выбери регион (рекомендуется `ams` или就近 к тебе)
- Не создавай PostgreSQL (боту не нужна БД)
- Согласись с настройками по умолчанию

### Шаг 3: Установи секреты
```bash
fly secrets set DISCORD_BOT_TOKEN=твой_токен_здесь
```

### Шаг 4: Задеплой
```bash
fly deploy
```

### Шаг 5: Проверь статус
```bash
fly status
```

---

## Полезные команды

### Просмотр логов
```bash
fly logs
```

### Проверка здоровья
```bash
fly checks
```

### Подключение к консоли
```bash
fly console
```

### Перезапуск
```bash
fly apps restart
```

### Масштабирование
```bash
fly scale count 1
fly scale memory 256
```

---

## Мониторинг

### Метрики в реальном времени
```bash
fly dashboard
```

### Статистика ресурсов
```bash
fly status --all
```

---

## Обновление

После внесения изменений в код:
```bash
git add .
git commit -m "описание изменений"
git push

fly deploy
```

---

## Troubleshooting

### Бот не отвечает на команды:
1. Проверь логи: `fly logs`
2. Убедись что токен установлен: `fly secrets list`
3. Проверь что Gateway Intents включены в Discord Developer Portal

### Ошибка "Missing Access":
- Убедись что бот имеет нужные права на сервере
- Проверь что у бота есть доступ к каналу

### Приложение падает:
```bash
fly logs --tail  # Просмотр логов в реальном времени
fly restart      # Перезапуск
```

### Health check failing:
- Проверь что `/health` endpoint отвечает
- `curl https://твое-приложение.fly.dev/health`

---

## Конфигурация

Основные настройки в `fly.toml`:

```toml
app = "discord-random-bot"  # Имя приложения
primary_region = "ams"      # Регион (можно изменить)

[http_service]
  internal_port = 8000      # Порт health check
  min_machines_running = 1  # Минимум машин

[[vm]]
  memory_mb = 256           # Память
  cpus = 1                  # CPU
```

---

## Стоимость

- **Free tier:** ~3GB-дней + 160GB-дней outbound в месяц бесплатно
- **Бот потребляет:** ~256MB RAM
- **Примерная стоимость:** Бесплатно в рамках free tier

---

## Ссылки

- [Fly.io Documentation](https://fly.io/docs/)
- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Discord Developer Portal](https://discord.com/developers/applications)
