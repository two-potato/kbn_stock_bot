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
# TOKEN = "6036100416:AAHRn2OFsI9WbOvI-w3NYQZhkSluAN6zyDo"

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message()
async def handle_message(message: Message):
    search_query = message.text
    await message.reply(f"Ищу артикул: {search_query}...")
    result_message = parse_product_info(search_query)
    if not result_message:
        await message.answer("Неверный артикул")
    print(result_message["stock_warehouse"])
    reply_message = (
        f"Артикул: {search_query} \n"
        f"{result_message["title"]}\n \n"
        f"Бренд: {result_message["brand"]} \n"
        f"{result_message["price"]} \n"
        f'На складе: {result_message["stock_warehouse"]} \n'
        f'В шоу-руме: {result_message["showroom_stock"]} \n'
        f'На удаленном: {result_message["remote_warehouse"]} \n'
    )
    await message.answer(reply_message)


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
