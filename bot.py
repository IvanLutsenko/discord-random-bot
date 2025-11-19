import discord
from discord import app_commands
from discord.ext import commands
import random
import json
import os
from datetime import datetime
from typing import Optional, List
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Конфигурация бота
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# История выборов
class SelectionHistory:
    def __init__(self, filepath='history.json'):
        self.filepath = filepath
        self.history = self.load_history()
    
    def load_history(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_history(self):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def add_selection(self, guild_id: str, channel_id: str, mode: str, selected: List[str]):
        key = f"{guild_id}_{channel_id}"
        if key not in self.history:
            self.history[key] = {
                'selections': [],
                'used_members': []
            }
        
        self.history[key]['selections'].append({
            'timestamp': datetime.now().isoformat(),
            'mode': mode,
            'selected': selected
        })
        
        # Добавляем в использованные для режима без повторов
        self.history[key]['used_members'].extend(selected)
        
        # Ограничиваем историю последними 100 выборами
        if len(self.history[key]['selections']) > 100:
            self.history[key]['selections'] = self.history[key]['selections'][-100:]
        
        self.save_history()
    
    def get_used_members(self, guild_id: str, channel_id: str) -> List[str]:
        key = f"{guild_id}_{channel_id}"
        return self.history.get(key, {}).get('used_members', [])
    
    def reset_used_members(self, guild_id: str, channel_id: str):
        key = f"{guild_id}_{channel_id}"
        if key in self.history:
            self.history[key]['used_members'] = []
            self.save_history()
    
    def get_recent_selections(self, guild_id: str, channel_id: str, limit: int = 10):
        key = f"{guild_id}_{channel_id}"
        selections = self.history.get(key, {}).get('selections', [])
        return selections[-limit:]

history = SelectionHistory()

@bot.event
async def on_ready():
    print(f'🤖 Бот запущен: {bot.user.name} (ID: {bot.user.id})')
    print(f'📊 Подключен к {len(bot.guilds)} серверам')
    
    try:
        synced = await bot.tree.sync()
        print(f'✅ Синхронизировано {len(synced)} команд')
    except Exception as e:
        print(f'❌ Ошибка синхронизации команд: {e}')

# Команда: случайный из всех участников
@bot.tree.command(name="random", description="Выбрать случайного участника сервера")
@app_commands.describe(
    count="Сколько участников выбрать (по умолчанию: 1)",
    no_repeat="Не повторять ранее выбранных (по умолчанию: False)"
)
async def random_member(
    interaction: discord.Interaction,
    count: Optional[int] = 1,
    no_repeat: Optional[bool] = False
):
    await interaction.response.defer()
    
    members = [m for m in interaction.guild.members if not m.bot]
    
    if not members:
        await interaction.followup.send("❌ Нет доступных участников!")
        return
    
    # Фильтруем уже использованных если включен режим без повторов
    if no_repeat:
        used = history.get_used_members(str(interaction.guild_id), str(interaction.channel_id))
        members = [m for m in members if str(m.id) not in used]
        
        if not members:
            await interaction.followup.send(
                "❌ Все участники уже были выбраны! Используйте `/reset` для сброса истории."
            )
            return
    
    count = min(count, len(members))
    selected = random.sample(members, count)
    
    # Сохраняем в историю
    history.add_selection(
        str(interaction.guild_id),
        str(interaction.channel_id),
        "all",
        [str(m.id) for m in selected]
    )
    
    # Формируем ответ
    embed = discord.Embed(
        title="🎲 Случайный выбор",
        color=discord.Color.purple(),
        timestamp=datetime.now()
    )
    
    if count == 1:
        member = selected[0]
        embed.description = f"## 🎯 {member.mention}\n\n**{member.display_name}**"
        embed.set_thumbnail(url=member.display_avatar.url)
    else:
        embed.description = "\n".join([f"{i+1}. {m.mention} — **{m.display_name}**" for i, m in enumerate(selected)])
    
    embed.set_footer(text=f"Всего участников: {len(members)}")
    
    await interaction.followup.send(embed=embed)

# Команда: случайный онлайн
@bot.tree.command(name="random-online", description="Выбрать случайного участника онлайн")
@app_commands.describe(
    count="Сколько участников выбрать (по умолчанию: 1)",
    no_repeat="Не повторять ранее выбранных (по умолчанию: False)"
)
async def random_online(
    interaction: discord.Interaction,
    count: Optional[int] = 1,
    no_repeat: Optional[bool] = False
):
    await interaction.response.defer()
    
    members = [
        m for m in interaction.guild.members 
        if not m.bot and m.status != discord.Status.offline
    ]
    
    if not members:
        await interaction.followup.send("❌ Нет участников онлайн!")
        return
    
    if no_repeat:
        used = history.get_used_members(str(interaction.guild_id), str(interaction.channel_id))
        members = [m for m in members if str(m.id) not in used]
        
        if not members:
            await interaction.followup.send(
                "❌ Все онлайн участники уже были выбраны! Используйте `/reset` для сброса."
            )
            return
    
    count = min(count, len(members))
    selected = random.sample(members, count)
    
    history.add_selection(
        str(interaction.guild_id),
        str(interaction.channel_id),
        "online",
        [str(m.id) for m in selected]
    )
    
    embed = discord.Embed(
        title="🎲 Случайный выбор (Онлайн)",
        color=discord.Color.green(),
        timestamp=datetime.now()
    )
    
    if count == 1:
        member = selected[0]
        embed.description = f"## 🎯 {member.mention}\n\n**{member.display_name}**"
        embed.set_thumbnail(url=member.display_avatar.url)
    else:
        embed.description = "\n".join([f"{i+1}. {m.mention} — **{m.display_name}**" for i, m in enumerate(selected)])
    
    embed.set_footer(text=f"Онлайн: {len(members)}")
    
    await interaction.followup.send(embed=embed)

# Команда: случайный из голосового канала
@bot.tree.command(name="random-voice", description="Выбрать случайного участника из голосового канала")
@app_commands.describe(
    channel="Голосовой канал (если не указан - твой текущий канал)",
    count="Сколько участников выбрать (по умолчанию: 1)",
    no_repeat="Не повторять ранее выбранных (по умолчанию: False)"
)
async def random_voice(
    interaction: discord.Interaction,
    channel: Optional[discord.VoiceChannel] = None,
    count: Optional[int] = 1,
    no_repeat: Optional[bool] = False
):
    await interaction.response.defer()
    
    # Если канал не указан, берём канал пользователя
    if channel is None:
        if interaction.user.voice is None:
            await interaction.followup.send("❌ Ты не в голосовом канале! Укажи канал или зайди в голосовой.")
            return
        channel = interaction.user.voice.channel
    
    members = [m for m in channel.members if not m.bot]
    
    if not members:
        await interaction.followup.send(f"❌ В канале **{channel.name}** нет участников!")
        return
    
    if no_repeat:
        used = history.get_used_members(str(interaction.guild_id), str(interaction.channel_id))
        members = [m for m in members if str(m.id) not in used]
        
        if not members:
            await interaction.followup.send(
                "❌ Все участники голосового канала уже были выбраны! Используйте `/reset`."
            )
            return
    
    count = min(count, len(members))
    selected = random.sample(members, count)
    
    history.add_selection(
        str(interaction.guild_id),
        str(interaction.channel_id),
        f"voice_{channel.id}",
        [str(m.id) for m in selected]
    )
    
    embed = discord.Embed(
        title=f"🎲 Случайный выбор из 🔊 {channel.name}",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    if count == 1:
        member = selected[0]
        embed.description = f"## 🎯 {member.mention}\n\n**{member.display_name}**"
        embed.set_thumbnail(url=member.display_avatar.url)
    else:
        embed.description = "\n".join([f"{i+1}. {m.mention} — **{m.display_name}**" for i, m in enumerate(selected)])
    
    embed.set_footer(text=f"Участников в канале: {len(members)}")
    
    await interaction.followup.send(embed=embed)

# Команда: случайный с определённой ролью
@bot.tree.command(name="random-role", description="Выбрать случайного участника с определённой ролью")
@app_commands.describe(
    role="Роль для фильтрации",
    count="Сколько участников выбрать (по умолчанию: 1)",
    no_repeat="Не повторять ранее выбранных (по умолчанию: False)"
)
async def random_role(
    interaction: discord.Interaction,
    role: discord.Role,
    count: Optional[int] = 1,
    no_repeat: Optional[bool] = False
):
    await interaction.response.defer()
    
    members = [m for m in role.members if not m.bot]
    
    if not members:
        await interaction.followup.send(f"❌ Нет участников с ролью **{role.name}**!")
        return
    
    if no_repeat:
        used = history.get_used_members(str(interaction.guild_id), str(interaction.channel_id))
        members = [m for m in members if str(m.id) not in used]
        
        if not members:
            await interaction.followup.send(
                f"❌ Все участники с ролью **{role.name}** уже были выбраны! Используйте `/reset`."
            )
            return
    
    count = min(count, len(members))
    selected = random.sample(members, count)
    
    history.add_selection(
        str(interaction.guild_id),
        str(interaction.channel_id),
        f"role_{role.id}",
        [str(m.id) for m in selected]
    )
    
    embed = discord.Embed(
        title=f"🎲 Случайный выбор из роли {role.name}",
        color=role.color if role.color != discord.Color.default() else discord.Color.purple(),
        timestamp=datetime.now()
    )
    
    if count == 1:
        member = selected[0]
        embed.description = f"## 🎯 {member.mention}\n\n**{member.display_name}**"
        embed.set_thumbnail(url=member.display_avatar.url)
    else:
        embed.description = "\n".join([f"{i+1}. {m.mention} — **{m.display_name}**" for i, m in enumerate(selected)])
    
    embed.set_footer(text=f"Участников с ролью: {len(members)}")
    
    await interaction.followup.send(embed=embed)

# Команда: история выборов
@bot.tree.command(name="history", description="Показать историю последних выборов")
@app_commands.describe(limit="Сколько последних выборов показать (по умолчанию: 10)")
async def show_history(interaction: discord.Interaction, limit: Optional[int] = 10):
    await interaction.response.defer()
    
    selections = history.get_recent_selections(
        str(interaction.guild_id),
        str(interaction.channel_id),
        limit
    )
    
    if not selections:
        await interaction.followup.send("📝 История выборов пуста!")
        return
    
    embed = discord.Embed(
        title="📜 История выборов",
        color=discord.Color.gold(),
        timestamp=datetime.now()
    )
    
    for i, sel in enumerate(reversed(selections), 1):
        timestamp = datetime.fromisoformat(sel['timestamp'])
        members = []
        for member_id in sel['selected']:
            member = interaction.guild.get_member(int(member_id))
            if member:
                members.append(member.display_name)
        
        mode_emoji = {
            'all': '👥',
            'online': '🟢',
            'voice': '🔊',
            'role': '🎭'
        }
        
        mode = sel['mode'].split('_')[0]
        emoji = mode_emoji.get(mode, '🎲')
        
        embed.add_field(
            name=f"{emoji} {timestamp.strftime('%d.%m.%Y %H:%M')}",
            value=", ".join(members) if members else "Участники не найдены",
            inline=False
        )
    
    await interaction.followup.send(embed=embed)

# Команда: сброс истории
@bot.tree.command(name="reset", description="Сбросить историю использованных участников")
async def reset_history(interaction: discord.Interaction):
    history.reset_used_members(str(interaction.guild_id), str(interaction.channel_id))
    
    embed = discord.Embed(
        title="🔄 История сброшена",
        description="Теперь все участники снова доступны для выбора!",
        color=discord.Color.orange()
    )
    
    await interaction.response.send_message(embed=embed)

# Команда: помощь
@bot.tree.command(name="help", description="Показать справку по командам бота")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 Справка по командам",
        description="Бот для случайного выбора участников",
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="/random",
        value="Выбрать случайного участника сервера\n`count` — количество участников\n`no_repeat` — без повторов",
        inline=False
    )
    
    embed.add_field(
        name="/random-online",
        value="Выбрать случайного участника онлайн\n`count` — количество\n`no_repeat` — без повторов",
        inline=False
    )
    
    embed.add_field(
        name="/random-voice",
        value="Выбрать из голосового канала\n`channel` — голосовой канал\n`count` — количество\n`no_repeat` — без повторов",
        inline=False
    )
    
    embed.add_field(
        name="/random-role",
        value="Выбрать участника с ролью\n`role` — роль\n`count` — количество\n`no_repeat` — без повторов",
        inline=False
    )
    
    embed.add_field(
        name="/history",
        value="Показать историю выборов\n`limit` — количество записей",
        inline=False
    )
    
    embed.add_field(
        name="/reset",
        value="Сбросить историю использованных участников",
        inline=False
    )
    
    embed.set_footer(text="💡 Режим no_repeat не даёт выбрать участника дважды до сброса истории")
    
    await interaction.response.send_message(embed=embed)

# Запуск бота
if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    
    if not TOKEN:
        print("❌ ОШИБКА: Не найден токен бота!")
        print("Установи переменную окружения DISCORD_BOT_TOKEN")
        exit(1)
    
    bot.run(TOKEN)
