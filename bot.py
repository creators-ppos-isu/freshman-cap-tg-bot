import asyncio
from os import getenv
import logging
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.utils import formatting

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


@root.message(Command('me'))
async def cmd_me(message: types.Message, state: FSMContext):
    content = formatting.as_marked_list(
        formatting.as_key_value('Состояние', await state.get_state()),
        formatting.as_key_value('Данные', await state.get_data()),
    )
    await message.answer(**content.as_kwargs())


dp = Dispatcher(storage=MemoryStorage())
dp.include_routers(root, teams, admin)


async def main() -> None:
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    try:
        await init()
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        pass
    finally:
        await close_connections()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO
    )
    asyncio.run(main())
