import logging

import tortoise.exceptions
from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery, ErrorEvent, InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.filters import Command, ExceptionTypeFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils import formatting
from tortoise.exceptions import ValidationError

from settings import DIVISIONS
from .keyboards import TeamInPlaceCallback, DivisionCallback
from .states import TeamReg
from .models import Team, Station
from admin.keyboards import get_add_score_kb

teams = Router()


@teams.callback_query(DivisionCallback.filter())
async def process_team_division(query: CallbackQuery, callback_data: DivisionCallback, state: FSMContext):
    await state.update_data(division=DIVISIONS[callback_data.division_id])
    await state.set_state(TeamReg.name)
    await query.message.answer('Придумай название для команды')


@teams.message(TeamReg.name)
async def process_team_name(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        await Team.update_or_create(
            leader=message.from_user.id,
            division=data['division'],
            defaults=dict(
                name=message.text,
            )
        )

    except ValidationError:
        return await message.reply('Неверный формат названия команды: максимальная длина - 32 символа')

    await message.answer('Спасибо, я запомнил!')
    logging.info(f'Registered new team from {data["division"]} with name {message.text}, leader id: {message.from_user.id}')
    await state.clear()


async def send_current_station_for(team: Team, message: Message) -> Station:
    station = await team.get_current_station()

    content = formatting.as_list(
        formatting.Bold(station.name),
        formatting.as_key_value('📍', station.place),
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Мы на месте!',
                callback_data=TeamInPlaceCallback().pack())
        ]
    ])
    await message.bot.send_message(
        chat_id=team.leader,
        **content.as_kwargs(),
        reply_markup=keyboard
    )

    return station


@teams.callback_query(TeamInPlaceCallback.filter())
async def team_in_place(query: CallbackQuery):
    team = await Team.get(leader=query.from_user.id)
    station = await team.get_current_station()

    await query.bot.send_message(
        chat_id=station.moderator,
        text=f'Поставьте оценку команде {team.name}',
        reply_markup=get_add_score_kb(team.id)
    )


@teams.message(Command('team'))
async def cmd_team(message: Message):
    team = await Team.get(leader=message.from_user.id)

    content = formatting.as_list(
        formatting.Bold('Информация о команде\n'),
        formatting.as_key_value('Название', team.name),
        formatting.as_key_value('Баллы', team.score),
        formatting.as_key_value('Прогресс', f'{team.progress}/{10}')
    )
    await message.answer(**content.as_kwargs())


@teams.error(ExceptionTypeFilter(tortoise.exceptions.DoesNotExist), F.update.message.as_('message'))
async def handle_team_does_not_exists(event: ErrorEvent, message: Message):
    await message.answer('Объект не найден')
