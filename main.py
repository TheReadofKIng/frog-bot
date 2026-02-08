import asyncio
import random
import time
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiohttp import web

# --- НАСТРОЙКИ ---
TOKEN = "8515456316:AAHSsPSEDotA30RJU-demHz5nQE1tPlrACI" 
ADMIN_ID = 6420881795 

bot = Bot(token=TOKEN)
dp = Dispatcher()

users, families, last_work = {}, {}, {}

# Словарь карточек
CARDS_DB = {
    1: "🐸 Новичок", 2: "🌿 Прыгунья", 3: "💧 Капля", 4: "🦟 Ловец",
    5: "🪵 Хранитель", 6: "🍃 Лист", 7: "🎭 Артист", 8: "⚔️ Рыцарь",
    9: "🧙 Алхимик", 10: "🌑 Ночной", 11: "💎 Изумруд", 12: "✨ Патриарх"
}

def get_u(uid, name="Жаба"):
    uid = int(uid)
    if uid not in users:
        users[uid] = {"n": name, "f": 50, "c": [], "b": False, "fid": None}
    u = users[uid]
    if uid == ADMIN_ID: u["r"] = "👑 Бог Священного Болота"
    else:
        val = families[u["fid"]]["f"] if u["fid"] else u["f"]
        u["r"] = "Икринка" if val < 100 else "Болотная Жаба" if val < 1000 else "Патриарх Болота"
    return u

def get_bal(u):
    if u["fid"] and u["fid"] in families: return families[u["fid"]]["f"]
    return u["f"]

def add_f(u, amt):
    if u["fid"] and u["fid"] in families: families[u["fid"]]["f"] += amt
    else: u["f"] += amt

# --- НОВАЯ КОМАНДА: ВЫДАТЬ ВСЕ КАРТЫ СРАЗУ ---
@dp.message(Command("give_all_cards"))
async def give_all(m: types.Message):
    if m.from_user.id != ADMIN_ID:
        return await m.reply("❌ Только Бог может раздавать все карты!")
    
    try:
        args = m.text.split()
        if len(args) < 2:
            return await m.reply("⚠ Пиши: `/give_all_cards [ID]` или `/give_all_cards me`")
        
        target_id = ADMIN_ID if args[1] == "me" else int(args[1])
        u = get_u(target_id)
        
        # Добавляем только те карты, которых еще нет
        added_count = 0
        for card_name in CARDS_DB.values():
            if card_name not in u["c"]:
                u["c"].append(card_name)
                added_count += 1
        
        await m.answer(f"🃏 Полная коллекция собрана! Жабе {u['n']} выдано {added_count} новых карт. Всего в сумме: 12/12.")
            
    except ValueError:
        await m.reply("⚠ Ошибка в ID! Введи цифры или 'me'.")

# --- КОМАНДА ВЫДАЧИ ОДНОЙ КАРТЫ ПО ID ---
@dp.message(Command("give_card"))
async def give_card(m: types.Message):
    if m.from_user.id != ADMIN_ID: return
    try:
        args = m.text.split()
        card_id, target_id = int(args[1]), (ADMIN_ID if args[2] == "me" else int(args[2]))
        if card_id not in CARDS_DB: return await m.reply("❌ ID карты от 1 до 12!")
        u = get_u(target_id)
        card_name = CARDS_DB[card_id]
        if card_name not in u["c"]:
            u["c"].append(card_name)
            await m.answer(f"🎁 Выдана карта: {card_name} для {u['n']}")
    except: await m.reply("⚠ Формат: `/give_card [ID_карты] [ID_юзера]`")

# --- ОСТАЛЬНЫЕ КОМАНДЫ ---
@dp.message(Command("start"))
async def st(m: types.Message):
    get_u(m.from_user.id, m.from_user.full_name)
    await m.answer("🟢 Бот готов!\n/give_all_cards me — получить все карты (для тебя)")

@dp.message(Command("me"))
async def profile(m: types.Message):
    u = get_u(m.from_user.id, m.from_user.full_name)
    await m.reply(f"👤 {u['n']}\n🦟 Мух: {get_bal(u)}\n🧬 Ранг: {u['r']}\n🃏 Карт: {len(u['c'])}/12")

@dp.message(Command("cards"))
async def my_cards(m: types.Message):
    u = get_u(m.from_user.id)
    await m.reply(f"🃏 Твоя коллекция:\n" + ("Пусто" if not u["c"] else "\n".join(u["c"])))

# --- СЕРВЕР ---
async def handle(request): return web.Response(text="Alive")
async def start_webserver():
    app = web.Application(); app.router.add_get("/", handle)
    runner = web.AppRunner(app); await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 8080))).start()

async def main():
    asyncio.create_task(start_webserver())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
