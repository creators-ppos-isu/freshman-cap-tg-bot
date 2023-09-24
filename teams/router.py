from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from .states import TeamReg


teams = Router()


@teams.message(TeamReg.name)
async def process_team_name(message: Message, state: FSMContext):
    await state.update_data(team_name=message.text)
    await message.answer('Спасибо, я запомнил!')
    await state.set_state(None)
