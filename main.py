import os
import asyncio
import discord
from discord.ext import commands
from aiohttp import web

# ===================================================
# 1. НАСТРОЙКА ВЕБ-СЕРВЕРА (Чтобы Render не спал)
# ===================================================
async def handle(request):
    return web.Response(text="Бот лиги по CS активен и работает!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Render выдает порт динамически в переменную окружения PORT
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"[*] Веб-сервер успешно поднят на порту {port}")

# ===================================================
# 2. НАСТРОЙКА DISCORD БОТА И КОМАНД
# ===================================================
intents = discord.Intents.default()
intents.message_content = True  # Чтение текста сообщений
intents.members = True          # Работа со списком участников сервера

bot = commands.Bot(command_prefix="!", intents=intents)

# Твой обновленный словарь с командами
COMMANDS_DATA = {
    "giverole": {
        "manager_role_id": 1489414660141748334,
        "target_role_id": 1489414725791121551
    },
    "giverolecap": {
        "manager_role_id": 1489415083678240959,
        "target_role_id": 1489415114342928435
    }
}

@bot.event
async def on_ready():
    print(f"[+] Бот {bot.user.name} вошел в сеть Discord!")

@bot.event
async def on_message(message):
    # Не реагируем на сообщения от самого бота
    if message.author.bot:
        return

    content = message.content.strip()
    parts = content.split()
    
    if not parts:
        return
        
    command_name = parts[0]
    
    # Убираем префикс "!", если он есть
    clean_command = command_name.lstrip('!')
    
    # Проверяем, есть ли введенная команда в нашем словаре
    if clean_command in COMMANDS_DATA:
        # Проверяем, упомянут ли пользователь
        if not message.mentions:
            await message.channel.send("❌ Команда использована неверно. Упомяните пользователя через @.")
            return
            
        target_user = message.mentions[0]
        role_info = COMMANDS_DATA[clean_command]
        
        manager_role_id = role_info["manager_role_id"]
        target_role_id = role_info["target_role_id"]
        
        # Проверяем, есть ли у автора сообщения роль менеджера
        author_roles = [role.id for role in message.author.roles]
        if manager_role_id not in author_roles:
            await message.channel.send("❌ У вас нет прав для использования этой команды.")
            return
            
        # Ищем роль на сервере
        target_role = message.guild.get_role(target_role_id)
        if not target_role:
            await message.channel.send("❌ Целевая роль не найдена на этом сервере.")
            return
            
        try:
            # Выдаем роль
            await target_user.add_roles(target_role)
            await message.channel.send(f"✅ Роль **{target_role.name}** успешно выдана {target_user.mention}!")
        except discord.Forbidden:
            await message.channel.send("❌ У бота нет прав на выдачу ролей. Поднимите роль бота выше в списке ролей в настройках сервера!")
        except Exception as e:
            await message.channel.send(f"❌ Произошла непредвиденная ошибка: {e}")

    await bot.process_commands(message)

# ===================================================
# 3. ТОЧКА ВХОДА
# ===================================================
async def main():
    # Запускаем веб-сервер для Render
    await start_web_server()
    
    # Получаем токен из переменных окружения
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("[!] ОШИБКА: Переменная DISCORD_TOKEN не найдена в настройках Render!")
        return
        
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
