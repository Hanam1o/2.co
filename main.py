import os
import discord
from discord.ext import commands
from aiohttp import web
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

COMMANDS_DATA = {
    "give1": {
        "manager_role_id": 1489363262536548532,
        "target_role_id": 1489363312323068114
    },
    "give2": {
        "manager_role_id": 1489381724713386146,
        "target_role_id": 1489381762412056720
    },
}

@bot.event
async def on_ready():
    print(f"Бот {bot.user.name} успешно запущен и готов к работе!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.startswith("!"):
        parts = message.content.split()
        command_name = parts[0][1:]

        if command_name in COMMANDS_DATA:
            config = COMMANDS_DATA[command_name]
            
            has_role = any(role.id == config["manager_role_id"] for role in message.author.roles)
            if not has_role:
                await message.channel.send("❌ У вас нет прав на использование этой команды.")
                return

            if len(message.mentions) == 0:
                await message.channel.send(f"⚠️ Использование: `!{command_name} @Пользователь`")
                return

            member = message.mentions[0]
            role_to_give = message.guild.get_role(config["target_role_id"])

            if not role_to_give:
                await message.channel.send("❌ Ошибка: Роль для выдачи не найдена на сервере.")
                return

            try:
                await member.add_roles(role_to_give)
                await message.channel.send(f"Роль {role_to_give.mention} успешно выдана пользователю {member.mention}!")
            except discord.errors.Forbidden:
                await message.channel.send("❌ Ошибка: У бота не хватает прав! Проверьте иерархию ролей.")
            return

    await bot.process_commands(message)

async def handle(request):
    return web.Response(text="Бот работает 24/7!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get('PORT', 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"Веб-сервер запущен на порту {port}")

async def main():
    await start_web_server()
    await bot.start("MTQ0OTM3M3N1A1NDY0MzUyNzczMA.GLvwvj.FFGJM-PrKPFG_wlNNBihMVOV-Zb-5BG_BBxOh4")

if __name__ == "__main__":
    asyncio.run(main())
