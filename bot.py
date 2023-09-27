import asyncio
import logging

from os import getenv
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db import init, close_connections

from teams.models import Team
from teams.router import teams
from teams.keyboards import DivisionCallback

from admin.router import admin
from settings import DIVISIONS


load_dotenv()
root = Router()
TOKEN = getenv('BOT_TOKEN')


@root.message(CommandStart())
async def cmd_start(message: types.Message):
    team = await Team.get_or_none(leader=message.from_user.id)
    if team is not None:
        return await message.answer(f'Ты уже являешься капитаном команды <b>{team.name}</b>. '
                                    f'Для изменения названия необходимо обратиться к администратору')

    builder = InlineKeyboardBuilder()
    for index, division in enumerate(DIVISIONS):
        builder.button(text=division, callback_data=DivisionCallback(division_id=index))

    builder.adjust(1, repeat=True)
    await message.answer('Выбери подразделение', reply_markup=builder.as_markup())


dp = Dispatcher(storage=MemoryStorage())
dp.include_routers(root, teams, admin)


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    try:
        await init()
        await dp.start_polling(bot)
    finally:
        await close_connections()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO
    )
    asyncio.run(main())
