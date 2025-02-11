import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import feedparser
import asyncio


logging.basicConfig(level=logging.INFO)

API_TOKEN = '8106970514:AAHzqTa-wKim6XauPoSiiVTm89Ic1h9QXBg'
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

RSS_FEEDS = {
    "Lenta.ru": "https://lenta.ru/rss",
    "РИА Новости": "https://ria.ru/export/rss2/index.xml",
    "ТАСС": "https://tass.ru/rss/v2.xml",

    "StopGame": "https://stopgame.ru/rss/rss_news.xml",  # Проверенная ссылка
    "Kanobu": "https://kanobu.ru/rss/articles/",  # Альтернативная ссылка
    "IXBT Games": "https://www.ixbt.com/export/games.rss",  # Проверенная ссылка
    "PlayGround": "https://www.playground.ru/rss/news.xml",  # Рабочая ссылка
    "GameTech": "https://www.gametech.ru/rss/news/"  # Альтернативная ссылка
}

@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer(
        "Привет! Я бот, который присылает новости с русских сайтов и новости про игры.\n"
        "Используй команду /news, чтобы получить свежие новости.\n"
        "Используй команду /gaming, чтобы получить новости про игры."
    )

@dp.message(Command("news"))
async def send_news(message: Message):
    await message.answer("Собираю новости... Пожалуйста, подождите.")

    general_feeds = {k: v for k, v in RSS_FEEDS.items() if k not in ["StopGame", "Kanobu", "IXBT Games", "PlayGround", "GameTech"]}

    for source, url in general_feeds.items():
        try:        
            feed = feedparser.parse(url)
            if feed.entries:
                for entry in feed.entries[:3]:
                    news_message = (
                        f"<b>{source}</b>\n\n"
                        f"<b>{entry.title}</b>\n"
                        f"{entry.description}\n"
                        f"<a href='{entry.link}'>Читать далее</a>"
                    )
                    await message.answer(news_message, parse_mode="HTML")
            else:
                await message.answer(f"Не удалось получить новости из {source}.")
        except Exception as e:
            logging.error(f"Ошибка при получении новостей из {source}: {e}")
            await message.answer(f"Ошибка при получении новостей из {source}.")

@dp.message(Command("gaming"))
async def send_gaming_news(message: Message):
    await message.answer("Собираю игровые новости... Пожалуйста, подождите.")

    gaming_feeds = {k: v for k, v in RSS_FEEDS.items() if k in ["StopGame", "Kanobu", "IXBT Games", "PlayGround", "GameTech"]}

    for source, url in gaming_feeds.items():
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                # Отправляем первые 3 новости из каждого источника
                for entry in feed.entries[:3]:
                    news_message = (
                        f"<b>{source}</b>\n\n"
                        f"<b>{entry.title}</b>\n"
                        f"{entry.description}\n"
                        f"<a href='{entry.link}'>Читать далее</a>"
                    )
                    await message.answer(news_message, parse_mode="HTML")
            else:
                await message.answer(f"Не удалось получить новости из {source}.")
        except Exception as e:
            logging.error(f"Ошибка при получении новостей из {source}: {e}")
            await message.answer(f"Ошибка при получении новостей из {source}.")

@dp.message()
async def handle_unknown_command(message: Message):
    await message.answer("Я не понимаю этой команды. Используйте /start для начала.")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
