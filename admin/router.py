import logging

from aiogram import Router
from aiogram.types import Message
from aiogram.utils.formatting import as_list
from aiogram.filters import Command

from teams.models import Team


admin = Router()


@admin.message(Command('teams'))
async def cmd_team(message: Message):
    teams = await Team.all()
    content = as_list(*teams)
    await message.answer(**content.as_kwargs())
