import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
import random
import json
import os
from datetime import datetime
from typing import List
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Конфигурация бота
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# История выборов (для режима без повторов)
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
    
    def add_selection(self, guild_id: str, channel_id: str, selected: str):
        key = f"{guild_id}_{channel_id}"
        if key not in self.history:
            self.history[key] = {
                'selections': [],
                'used_members': []
            }
        
        self.history[key]['selections'].append({
            'timestamp': datetime.now().isoformat(),
            'selected': selected
        })
        
        self.history[key]['used_members'].append(selected)
        
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

history = SelectionHistory()

# View с кнопкой "Следующий"
class NextButton(View):
    def __init__(self, voice_channel: discord.VoiceChannel, guild_id: str, channel_id: str):
        super().__init__(timeout=none)
        self.voice_channel = voice_channel
        self.guild_id = guild_id
        self.channel_id = channel_id
    
    @discord.ui.button(label="➡️ Следующий", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        # Получаем онлайн участников из голосового канала
        members = [m for m in self.voice_channel.members if not m.bot]
        
        if not members:
            await interaction.followup.send("❌ В голосовом канале нет участников!", ephemeral=True)
            return
        
        # Фильтруем уже использованных
        used = history.get_used_members(self.guild_id, self.channel_id)
        available = [m for m in members if str(m.id) not in used]
        
        # Если все использованы - автосброс
        if not available:
            history.reset_used_members(self.guild_id, self.channel_id)
            available = members
            reset_msg = "🔄 Все участники были выбраны! История сброшена.\n\n"
        else:
            reset_msg = ""
        
        # Выбираем случайного
        selected = random.choice(available)
        
        # Сохраняем в историю
        history.add_selection(self.guild_id, self.channel_id, str(selected.id))
        
        # Формируем ответ
        embed = discord.Embed(
            title="🎲 Следующий участник",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        embed.description = f"{reset_msg}## 🎯 {selected.mention}\n\n**{selected.display_name}**"
        embed.set_thumbnail(url=selected.display_avatar.url)
        
        remaining = len(available) - 1
        embed.set_footer(text=f"Осталось участников: {remaining} из {len(members)}")
        
        # Создаём новую кнопку для следующего выбора
        new_view = NextButton(self.voice_channel, self.guild_id, self.channel_id)
        
        await interaction.followup.send(embed=embed, view=new_view)

@bot.event
async def on_ready():
    print(f'🤖 Бот запущен: {bot.user.name} (ID: {bot.user.id})')
    print(f'📊 Подключен к {len(bot.guilds)} серверам')
    
    try:
        synced = await bot.tree.sync()
        print(f'✅ Синхронизировано {len(synced)} команд')
    except Exception as e:
        print(f'❌ Ошибка синхронизации команд: {e}')

# Команда: случайный из голосового канала
@bot.tree.command(name="random", description="Выбрать случайного участника из голосового канала (без повторов)")
async def random_voice(interaction: discord.Interaction):
    await interaction.response.defer()
    
    # Проверяем что пользователь в голосовом канале
    if interaction.user.voice is None:
        await interaction.followup.send("❌ Ты не в голосовом канале! Зайди в голосовой канал и попробуй снова.")
        return
    
    voice_channel = interaction.user.voice.channel
    
    # Получаем участников голосового канала (исключая ботов)
    members = [m for m in voice_channel.members if not m.bot]
    
    if not members:
        await interaction.followup.send(f"❌ В канале **{voice_channel.name}** нет участников!")
        return
    
    # Фильтруем уже использованных участников
    used = history.get_used_members(str(interaction.guild_id), str(interaction.channel_id))
    available = [m for m in members if str(m.id) not in used]
    
    # Если все использованы - автоматический сброс
    if not available:
        history.reset_used_members(str(interaction.guild_id), str(interaction.channel_id))
        available = members
        reset_message = "🔄 Все участники были выбраны! История автоматически сброшена.\n\n"
    else:
        reset_message = ""
    
    # Выбираем случайного
    selected = random.choice(available)
    
    # Сохраняем в историю
    history.add_selection(
        str(interaction.guild_id),
        str(interaction.channel_id),
        str(selected.id)
    )
    
    # Формируем ответ
    embed = discord.Embed(
        title=f"🎲 Случайный выбор из 🔊 {voice_channel.name}",
        color=discord.Color.purple(),
        timestamp=datetime.now()
    )
    
    embed.description = f"{reset_message}## 🎯 {selected.mention}\n\n**{selected.display_name}**"
    embed.set_thumbnail(url=selected.display_avatar.url)
    
    remaining = len(available) - 1
    embed.set_footer(text=f"Осталось участников: {remaining} из {len(members)}")
    
    # Создаём view с кнопкой "Следующий"
    view = NextButton(voice_channel, str(interaction.guild_id), str(interaction.channel_id))
    
    await interaction.followup.send(embed=embed, view=view)

# Команда: помощь
@bot.tree.command(name="help", description="Показать справку по командам бота")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 Справка по командам",
        description="Бот для случайного выбора участников из голосового канала",
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="/random",
        value="Выбрать случайного участника из твоего голосового канала\n"
              "• Работает только если ты в голосовом канале\n"
              "• Выбирает из тех кто онлайн в этом канале\n"
              "• Без повторов (автоматически)\n"
              "• После выбора появляется кнопка «Следующий»",
        inline=False
    )
    
    embed.add_field(
        name="➡️ Кнопка «Следующий»",
        value="• Выбирает следующего участника\n"
              "• Не повторяет уже выбранных\n"
              "• Автоматически сбрасывает историю когда все выбраны\n"
              "• Доступна 5 минут после последнего выбора",
        inline=False
    )
    
    embed.add_field(
        name="🎯 Примеры использования",
        value="**Розыгрыш на митапе:**\n"
              "1. Зайди в голосовой канал с участниками\n"
              "2. Используй `/random`\n"
              "3. Жми «Следующий» для выбора призёров\n\n"
              "**Выбор докладчика:**\n"
              "1. Все потенциальные докладчики в голосовом\n"
              "2. `/random` — выбирает одного\n"
              "3. «Следующий» если нужен запасной",
        inline=False
    )
    
    embed.set_footer(text="💡 Бот запоминает выбранных и не повторяет их до сброса истории")
    
    await interaction.response.send_message(embed=embed)

# Запуск бота
if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    
    if not TOKEN:
        print("❌ ОШИБКА: Не найден токен бота!")
        print("Установи переменную окружения DISCORD_BOT_TOKEN")
        exit(1)
    
    bot.run(TOKEN)
