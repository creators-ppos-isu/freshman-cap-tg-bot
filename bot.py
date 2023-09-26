import asyncio
from os import getenv
import logging
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext

from db import init, close_connections

from teams.router import teams
from teams.states import TeamReg

from admin.router import admin


root = Router()
TOKEN = getenv('BOT_TOKEN')


@root.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.set_state(TeamReg.name)
    await message.answer('Придумай название для команды')


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
