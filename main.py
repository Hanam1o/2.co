import os
import asyncio
import discord
from discord.ext import commands
from aiohttp import web

async def handle(request):
    return web.Response(text="Бот лиги по CS активен и работает!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"[*] Веб-сервер запущен на порту {port}")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

COMMANDS_DATA = {
    "give1": {
        "manager_role_id": 111111111111111111,
        "target_role_id": 222222222222222222
    },
    "give2": {
        "manager_role_id": 111111111111111111,
        "target_role_id": 333333333333333333
    }
}

@bot.event
async def on_ready():
    print(f"[+] Бот {bot.user.name} успешно подключился к Discord!")

@bot.command()
async def give_role(ctx, command_name: str, member: discord.Member):
    if command_name not in COMMANDS_DATA:
        await ctx.send("❌ Такой команды не существует.")
        return
        
    role_info = COMMANDS_DATA[command_name]
    manager_role_id = role_info["manager_role_id"]
    target_role_id = role_info["target_role_id"]
    
    author_roles = [role.id for role in ctx.author.roles]
    if manager_role_id not in author_roles:
        await ctx.send("❌ У вас нет прав для использования этой команды.")
        return
        
    target_role = ctx.guild.get_role(target_role_id)
    if not target_role:
        await ctx.send("❌ Роль для выдачи не найдена на этом сервере.")
        return
        
    try:
        await member.add_roles(target_role)
        await ctx.send(f"✅ Роль **{target_role.name}** успешно выдана игроку {member.mention}!")
    except discord.Forbidden:
        await ctx.send("❌ У бота нет прав на выдачу ролей. Поднимите роль бота выше в списке ролей сервера!")
    except Exception as e:
        await ctx.send(f"❌ Произошла ошибка: {e}")

async def main():
    await start_web_server()
    
    token = os.environ.get("DISCORD_TOKEN")
    
    if not token:
        print("[!] ОШИБКА: Переменная окружения DISCORD_TOKEN не найдена!")
        return
        
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
