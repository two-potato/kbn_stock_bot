import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message

from parser import parse_product_info

# Bot token can be obtained via https://t.me/BotFather
TOKEN = getenv("TELEGRAM_TOKEN")

# All handlers should be attached to the Dispatcher
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(
        f"Привет, {html.bold(message.from_user.full_name)}! Введите название продукта для поиска."
    )


@dp.message()
async def handle_message(message: Message):
    search_query = message.text.strip()
    await message.reply(f"Ищу артикул: {search_query}...")

    try:
        result_data = parse_product_info(search_query)
        if not result_data:
            await message.answer("Товар не найден.")
            return

        required_keys = [
            "title",
            "brand",
            "price",
            "stock_warehouse",
            "showroom_stock",
            "remote_warehouse",
            "url",
        ]
        if not all(key in result_data for key in required_keys):
            await message.answer("Не удалось получить полную информацию о товаре.")
            return

        reply_message = (
            f"{result_data['title']}\n \n"
            f"Бренд: {result_data['brand']}\n"
            f"Цена: {result_data['price']}\n"
            f"На складе: {result_data['stock_warehouse']}\n"
            f"В шоу-руме: {result_data['showroom_stock']}\n"
            f"На удаленном складе: {result_data['remote_warehouse']}\n"
            f"Ссылка: {result_data['url']}"
        )
        await message.answer(reply_message)
    except Exception as e:
        logging.error(f"Error while parsing product info: {e}")
        await message.answer(
            "Произошла ошибка при обработке запроса. Попробуйте позже."
        )


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
