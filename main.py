import asyncio
import random
import time
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

# --- НАСТРОЙКИ ---
TOKEN = "8515456316:AAHSsPSEDotA30RJU-demHz5nQE1tPlrACI" #твой токен должен быть тут
ADMIN_ID = 6420881795 

bot = Bot(token=TOKEN)
dp = Dispatcher()

# База данных (в оперативной памяти)
users = {}
families = {}
active_swamps = set()
last_work = {}

CARDS = ["🐸 Новичок", "🌿 Прыгунья", "💧 Капля", "🦟 Ловец", "🪵 Хранитель", "🍃 Лист", 
         "🎭 Артист", "⚔️ Рыцарь", "🧙 Алхимик", "🌑 Ночной", "💎 Изумруд", "✨ Патриарх"]

# --- СИСТЕМНЫЕ ФУНКЦИИ ---
def get_u(uid, name="Жаба"):
    uid = int(uid)
    if uid not in users:
        users[uid] = {"n": name, "f": 50, "d": 0, "c": [], "b": False, "fid": None}
    u = users[uid]
    
    if uid == ADMIN_ID:
        u["r"] = "👑 Бог Священного Болота"
    else:
        val = families[u["fid"]]["f"] if u["fid"] else u["f"]
        u["r"] = "Икринка" if val < 100 else "Болотная Жаба" if val < 1000 else "Патриарх Болота"
    return u

def get_bal(u):
    if u["fid"] and u["fid"] in families:
        return families[u["fid"]]["f"]
    return u["f"]

def add_f(u, amt):
    if u["fid"] and u["fid"] in families:
        families[u["fid"]]["f"] += amt
    else:
        u["f"] += amt

# --- КОМАНДЫ ---
@dp.message(Command("start"))
async def st(m: types.Message):
    get_u(m.from_user.id, m.from_user.full_name)
    await m.answer("🟢 Бот запущен!\n/me — профиль\n/work — работа\n/marry — свадьба (реплаем)")

@dp.message(Command("me"))
async def profile(m: types.Message):
    u = get_u(m.from_user.id, m.from_user.full_name)
    badge = " ⭐" if u["b"] else ""
    fam = " ❤️ В браке" if u["fid"] else ""
    await m.reply(f"👤 {u['n']}{badge}{fam}\n🦟 Мух: {get_bal(u)}\n🧬 Ранг: {u['r']}")

@dp.message(Command("work"))
async def work(m: types.Message):
    uid = m.from_user.id
    if uid in last_work and time.time() - last_work[uid] < 600:
        return await m.reply("⏳ Отдохни 10 минут!")
    
    u = get_u(uid, m.from_user.full_name)
    rew = random.randint(20, 60)
    add_f(u, rew)
    last_work[uid] = time.time()
    await m.reply(f"🛠 Поймано {rew} мух!")

@dp.message(Command("marry"))
async def marry(m: types.Message):
    if not m.reply_to_message:
        return await m.reply("Ответь на сообщение партнера!")
    u1, u2 = get_u(m.from_user.id), get_u(m.reply_to_message.from_user.id)
    if u1["fid"] or u2["fid"]:
        return await m.reply("Кто-то уже в браке!")
    
    kb = InlineKeyboardBuilder()
    kb.button(text="💍 Да!", callback_data=f"ma_{m.from_user.id}_{m.reply_to_message.from_user.id}")
    await m.answer(f"🔔 {u1['n']} предлагает союз жабе {u2['n']}!", reply_markup=kb.as_markup())

@dp.callback_query(F.data.startswith("ma_"))
async def marry_ok(c: types.CallbackQuery):
    _, id1, id2 = c.data.split("_")
    if c.from_user.id != int(id2): return await c.answer("Не для тебя!")
    u1, u2 = get_u(int(id1)), get_u(int(id2))
    fid = f"fam_{id1}"
    families[fid] = {"f": u1["f"] + u2["f"], "m": [int(id1), int(id2)]}
    u1["fid"] = u2["fid"] = fid
    await c.message.edit_text(f"🎉 Свадьба состоялась!")

@dp.message(Command("god_mode"))
async def god(m: types.Message):
    if m.from_user.id == ADMIN_ID:
        u = get_u(ADMIN_ID)
        if u["fid"]: families[u["fid"]]["f"] = 1000000
        else: u["f"] = 1000000
        await m.answer("👑 ТЫ БОГ!")

# --- СЕРВЕР ДЛЯ RENDER ---
async def handle(request):
    return web.Response(text="Alive")

async def start_webserver():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 8080)))
    await site.start()

async def main():
    asyncio.create_task(start_webserver())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
