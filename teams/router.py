import logging

from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from tortoise.exceptions import ValidationError

from .states import TeamReg
from .models import Team


teams = Router()


@teams.message(TeamReg.name)
async def process_team_name(message: Message, state: FSMContext):
    try:
        await Team.update_or_create(
            leader=message.from_user.id,
            defaults=dict(
                name=message.text,
            )
        )

    except ValidationError:
        return await message.reply('Неверный формат названия команды: максимальная длина - 32 символа')

    await message.answer('Спасибо, я запомнил!')
    logging.info(f'Registered new team with name {message.text}, leader id: {message.from_user.id}')
    await state.clear()
