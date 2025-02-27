import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
import feedparser
import asyncio

logging.basicConfig(level=logging.INFO)

API_TOKEN = ''
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

RSS_FEEDS = {
    "Lenta.ru": "https://lenta.ru/rss",
    "РИА Новости": "https://ria.ru/export/rss2/index.xml",
    "ТАСС": "https://tass.ru/rss/v2.xml",
    "StopGame": "https://stopgame.ru/rss/rss_news.xml",
    "Kanobu": "https://kanobu.ru/rss/articles/",
    "IXBT Games": "https://www.ixbt.com/export/games.rss",
    "PlayGround": "https://www.playground.ru/rss/news.xml",
    "GameTech": "https://www.gametech.ru/rss/news/"
}

keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="/news"), KeyboardButton(text="/gaming")]
], resize_keyboard=True)

@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer(
        "Привет! Я бот, который присылает новости с русских сайтов и новости про игры.\n"
        "Используй команду /news, чтобы получить свежие новости.\n"
        "Используй команду /gaming, чтобы получить новости про игры.",
        reply_markup=keyboard
    )

@dp.message(Command("news"))
async def send_news(message: Message):
    await message.answer("Собираю новости... Пожалуйста, подождите.", reply_markup=keyboard)

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
                await message.answer(f"Не удалось получить новости из {source}.", reply_markup=keyboard)
        except Exception as e:
            logging.error(f"Ошибка при получении новостей из {source}: {e}")
            await message.answer(f"Ошибка при получении новостей из {source}.", reply_markup=keyboard)

@dp.message(Command("gaming"))
async def send_gaming_news(message: Message):
    await message.answer("Собираю игровые новости... Пожалуйста, подождите.", reply_markup=keyboard)

    gaming_feeds = {k: v for k, v in RSS_FEEDS.items() if k in ["StopGame", "Kanobu", "IXBT Games", "PlayGround", "GameTech"]}

    for source, url in gaming_feeds.items():
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
                await message.answer(f"Не удалось получить новости из {source}.", reply_markup=keyboard)
        except Exception as e:
            logging.error(f"Ошибка при получении новостей из {source}: {e}")
            await message.answer(f"Ошибка при получении новостей из {source}.", reply_markup=keyboard)

@dp.message()
async def handle_unknown_command(message: Message):
    await message.answer("Я не понимаю этой команды. Используйте /start для начала.", reply_markup=keyboard)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
