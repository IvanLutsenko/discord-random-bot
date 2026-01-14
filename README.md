# 🎲 Рандомайзер участников Discord

Бот для честного случайного выбора участников из голосового канала без повторов. Идеально подходит для розыгрышей призов, выбора докладчиков, и других случайных выборов.

> 🚀 **Бот уже работает!** Просто [добавь на свой сервер](https://discord.com/oauth2/authorize?client_id=1440626365324853271&permissions=2147502080&integration_type=0&scope=bot+applications.commands) и начинай использовать.

---

## 👥 Для пользователей

### 🤖 Как добавить бота на свой сервер

**Хочешь использовать готового бота без настройки?**

1. **Перейди по ссылке приглашения:**
   
   👉 [**Добавить бота на сервер**](https://discord.com/oauth2/authorize?client_id=1440626365324853271&permissions=2147502080&integration_type=0&scope=bot+applications.commands)

2. **Выбери свой сервер** из списка

3. **Нажми "Авторизовать"**

4. **Пройди капчу** (если попросят)

5. **Готово!** 🎉 Бот появится на сервере и можно использовать команды

> ⚠️ **Важно:** У тебя должны быть права администратора на сервере, чтобы добавить бота.

---

### 📋 Доступные команды

**`/random`** — Выбрать случайного участника  
**`/help`** — Показать справку

#### 🎯 Как использовать

1. **Зайди в голосовой канал** с участниками
2. **Напиши команду** `/random` в любом текстовом канале
3. **Бот выберет** одного случайного участника из твоего голосового канала
4. **Нажми кнопку "➡️ Следующий"** чтобы выбрать ещё одного

#### ✨ Особенности

- ✅ **Без повторов** — каждый участник выбирается только один раз
- ✅ **Автосброс** — когда все выбраны, история автоматически очищается
- ✅ **Только из голосового** — выбирает из тех кто онлайн в твоём канале
- ✅ **Кнопка "Следующий"** — не нужно вводить команду каждый раз

#### 🔄 Как сбросить историю?

История сбрасывается **автоматически** когда все участники были выбраны. Увидишь сообщение:
```
🔄 Все участники были выбраны! История сброшена.
```

---

## 🛠️ Для разработчиков

### Как поднять своего бота

#### Вариант А: Deploy на Fly.io (рекомендуется)

**Самый простой способ — бот работает 24/7 бесплатно.**

> 📝 **Почему Fly.io, а не Railway?**
>
> Раньше бот хостился на Railway, но их бесплатный тариф не подходит для Discord ботов:
>
> 1. **Лимит по часам** — Railway даёт **$5 кредитов/месяц** (~500 часов), а Discord бот должен работать **24/7** (~720 часов/месяц). После первого месяца бот просто останавливается.
>
> 2. **Serverless архитектура** — бесплатный Railway работает как "лямбды": приложение засыпает без активности и просыпается по запросу. Но Discord бот требует **постоянного WebSocket соединения** с Discord Gateway. Когда бот "спит", Discord разрывает соединение → бот уходит в оффлайн и перестаёт получать команды.
>
> **Fly.io** предоставляет **3 полноценных VM бесплатно** — не serverless, а настоящие серверы которые работают 24/7. Бот держит постоянное соединение и всегда онлайн.

1. **Fork этот репозиторий**
   - Нажми **Fork** справа сверху на GitHub

2. **Создай Discord бота**
   - Зайди на https://discord.com/developers/applications
   - **New Application** → дай имя боту
   - **Bot** → **Add Bot** → скопируй **Token**
   - Включи **Privileged Gateway Intents:**
     - ✅ Presence Intent
     - ✅ Server Members Intent
     - ✅ Message Content Intent

3. **Пригласи бота на сервер**
   - **OAuth2** → **URL Generator**
   - Scopes: `bot` + `applications.commands`
   - Bot Permissions:
     - Send Messages
     - Embed Links
     - Use Slash Commands
     - View Channels
   - Открой сгенерированный URL → выбери сервер

4. **Установи Fly CLI**
   ```bash
   # macOS / Linux
   curl -L https://fly.io/install.sh | sh

   # После установки
   fly auth login
   ```

5. **Deploy на Fly.io**
   ```bash
   cd discord-random-bot
   fly launch --no-deploy --copy-config --yes
   fly secrets set DISCORD_BOT_TOKEN=твой_токен_здесь
   fly deploy
   ```

6. **Готово!** 🎉
   - Бот онлайн 24/7
   - Бесплатно в рамках free tier
   - `fly logs` для просмотра логов
   - `fly status` для проверки статуса

#### Вариант Б: Локальный запуск

**Для разработки и тестирования:**

1. **Клонируй репозиторий**
   ```bash
   git clone https://github.com/твой-username/discord-random-bot.git
   cd discord-random-bot
   ```

2. **Установи зависимости**
   ```bash
   pip install -r requirements.txt
   ```

3. **Создай `.env` файл**
   ```bash
   cp .env.example .env
   nano .env
   ```
   
   Добавь свой токен:
   ```
   DISCORD_BOT_TOKEN=твой_токен_здесь
   ```

4. **Запусти бота**
   ```bash
   python bot.py
   ```

5. **Проверь логи**
   ```
   🤖 Бот запущен: Твой бот (ID: ...)
   📊 Подключен к 1 серверам
   ✅ Синхронизировано 2 команд
   ```

#### 📁 Структура проекта

```
discord-random-bot/
├── bot.py              # Основной код бота
├── web.py              # FastAPI сервер для health checks
├── run.py              # Запуск бота + веб-сервера
├── requirements.txt    # Зависимости Python
├── Dockerfile          # Контейнеризация для Fly.io
├── fly.toml            # Конфигурация Fly.io
├── .dockerignore       # Исключения для Docker
├── .env.example        # Пример конфигурации
├── .gitignore          # Игнорируемые файлы
├── FLY_DEPLOY.md       # Подробная инструкция по деплою
├── README.md           # Эта документация
└── history.json        # История выборов (создаётся автоматически)
```

#### 🔧 Как добавить новые команды

**Пример добавления команды `/stats`:**

```python
@bot.tree.command(name="stats", description="Показать статистику выборов")
async def stats_command(interaction: discord.Interaction):
    selections = history.get_recent_selections(
        str(interaction.guild_id), 
        str(interaction.channel_id), 
        limit=20
    )
    
    embed = discord.Embed(
        title="📊 Статистика",
        description=f"Всего выборов: {len(selections)}",
        color=discord.Color.blue()
    )
    
    await interaction.response.send_message(embed=embed)
```

#### 🎨 Как изменить стиль embed

В функции `random_voice` найди:

```python
embed = discord.Embed(
    title=f"🎲 Случайный выбор из 🔊 {voice_channel.name}",
    color=discord.Color.purple(),  # Измени цвет
    timestamp=datetime.now()
)
```

Доступные цвета: `blue()`, `green()`, `red()`, `gold()`, `orange()`, `purple()`

#### 🔄 Как изменить логику без повторов

В классе `NextButton` найди:

```python
# Для отключения автосброса закомментируй эти строки:
if not available:
    history.reset_used_members(self.guild_id, self.channel_id)
    available = members
```

#### 📝 История выборов

Хранится в `history.json`:
```json
{
  "guild_id_channel_id": {
    "selections": [
      {
        "timestamp": "2025-11-19T10:30:00",
        "selected": "123456789"
      }
    ],
    "used_members": ["123456789", "987654321"]
  }
}
```

#### 🧪 Тестирование

```bash
# Запусти бота локально
python bot.py

# В Discord:
/random  # Должно работать из голосового канала
/help    # Проверь справку
```

#### 🐛 Troubleshooting

**Бот не отвечает на команды:**
- Проверь что Privileged Gateway Intents включены
- Подожди 5 минут после добавления бота на сервер
- Перезапусти Discord клиент

**"Missing Permissions":**
- Убедись что бот имеет нужные права на сервере
- Проверь что у бота есть доступ к каналу

**"Members intent is required":**
- Включи Server Members Intent в Developer Portal
- Перезапусти бота

**Команды не синхронизируются:**
- Удали бота с сервера и добавь заново
- Проверь что scope `applications.commands` включён при приглашении

#### 🔒 Безопасность

⚠️ **ВАЖНО:**
- **Никогда** не коммить `.env` файл в Git
- **Никогда** не публиковать токен бота
- `.env` уже добавлен в `.gitignore`
- Если токен утёк → сразу **Reset Token** в Developer Portal

#### 📈 Деплой на другие платформы

**Fly.io (рекомендуется):**
```bash
fly auth login
fly launch --no-deploy --copy-config --yes
fly secrets set DISCORD_BOT_TOKEN=твой_токен
fly deploy
```

**VPS (systemd service):**
```ini
[Unit]
Description=Discord Random Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/discord-random-bot
Environment="DISCORD_BOT_TOKEN=твой_токен"
ExecStart=/path/to/venv/bin/python bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Docker:**
```bash
docker build -t discord-random-bot .
docker run -e DISCORD_BOT_TOKEN=твой_токен discord-random-bot
```

#### 📄 Лицензия

MIT License — делай с кодом что хочешь!

---

## 🔗 Полезные ссылки

- [Discord Developer Portal](https://discord.com/developers/applications)
- [Fly.io Documentation](https://fly.io/docs/)
- [discord.py Documentation](https://discordpy.readthedocs.io/)

---

**Звёздочка ⭐ на GitHub будет очень мотивировать!**
