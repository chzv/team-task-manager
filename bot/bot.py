import os, asyncio, aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_BASE = os.getenv("API_BASE", "http://localhost:8000/api")
SERVICE_TOKEN = os.getenv("SERVICE_TOKEN", "dev-service-token")

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

@dp.message(F.text == "/start")
async def start(m: Message):
    await m.answer("Привет! /link — привязка аккаунта, /tasks — список задач, /done <id> — завершить.")

@dp.message(F.text == "/link")
async def link(m: Message):
    async with aiohttp.ClientSession() as s:
        async with s.post(f"{API_BASE}/telegram/create_code/",
                          headers={"Authorization": f"Bearer {SERVICE_TOKEN}"},
                          json={"tg_user_id": m.from_user.id}) as r:
            if r.status != 200:
                txt = await r.text()
                await m.answer(f"Не удалось создать код (HTTP {r.status}). {txt[:200]}")
                return
            data = await r.json()
            code = data.get("code")
            if not code:
                await m.answer("Сервер не вернул код.")
                return
            await m.answer(f"Ваш код: {code}\nОткройте веб-приложение и подтвердите привязку.")

@dp.message(F.text == "/tasks")
async def tasks_cmd(m: Message):
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{API_BASE}/tg/tasks/",
                         headers={"Authorization": f"Bearer {SERVICE_TOKEN}", "X-TG-USER": str(m.from_user.id)}) as r:
            data = await r.json()
            if not data:
                await m.answer("На вас нет открытых задач.")
            else:
                lines = [f"• #{t['id']} {t['title']} (до {t['due_at'] or '—'}) {'✅' if t['is_done'] else ''}" for t in data]
                await m.answer("\n".join(lines))

@dp.message(F.text.regexp(r"^/done\s+\d+$"))
async def done_cmd(m: Message):
    task_id = int(m.text.split()[1])
    async with aiohttp.ClientSession() as s:
        async with s.post(f"{API_BASE}/tg/tasks/{task_id}/done/",
                          headers={"Authorization": f"Bearer {SERVICE_TOKEN}", "X-TG-USER": str(m.from_user.id)}) as r:
            await m.answer("Готово!" if r.status == 200 else "Не удалось.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
