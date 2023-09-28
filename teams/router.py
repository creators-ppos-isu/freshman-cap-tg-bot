import logging

import tortoise.exceptions
from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery, ErrorEvent
)
from aiogram.filters import Command, ExceptionTypeFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils import formatting
from aiogram.utils.keyboard import InlineKeyboardBuilder
from tortoise.exceptions import ValidationError

from settings import DIVISIONS, ROUTES
from .keyboards import TeamInPlaceCallback, DivisionCallback
from .states import TeamReg
from .models import Team, Station
from admin.keyboards import get_add_score_kb

teams = Router()


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


@teams.callback_query(DivisionCallback.filter())
async def process_team_division(query: CallbackQuery, callback_data: DivisionCallback, state: FSMContext):
    division = DIVISIONS[callback_data.division_id]
    await query.message.edit_text(f'Ты выбрал: {division}')
    await state.update_data(division=division)
    await state.set_state(TeamReg.name)
    await query.message.answer('Придумай название для команды')


@teams.message(TeamReg.name)
async def process_team_name(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        team = await Team.create(
            leader=message.from_user.id,
            division=data['division'],
            name=message.text,
        )

    except ValidationError as e:
        return await message.reply('Неверный формат названия команды: максимальная длина - 32 символа')

    await message.reply(f'Команда {team.name} успешно зарегистрирована!')
    logging.info(f'Registered {team}')
    await state.clear()


async def send_current_station_for(team: Team, message: Message):
    try:
        station = await team.get_current_station()
    except tortoise.exceptions.DoesNotExist:
        station_id = ROUTES[team.id - 1][team.progress]
        return await message.answer(f'Станция {station_id} не найдена в системе!')

    text = \
        f'<b>{station.name}</b>' \
        f'\n📍 {station.place}'

    builder = InlineKeyboardBuilder()
    builder.button(text='Мы на месте', callback_data=TeamInPlaceCallback())

    if station.image is None:
        await message.bot.send_message(
            chat_id=team.leader,
            text=text,
            reply_markup=builder.as_markup()
        )
    else:
        await message.bot.send_photo(
            chat_id=team.leader,
            photo=station.image,
            caption=text,
            reply_markup=builder.as_markup()
        )


@teams.callback_query(TeamInPlaceCallback.filter())
async def team_in_place(query: CallbackQuery):
    await query.message.edit_reply_markup()
    team = await Team.get(leader=query.from_user.id)
    station = await team.get_current_station()

    try:
        await query.bot.send_message(
            chat_id=station.moderator,
            text=f'Поставьте оценку команде {team.name}',
            reply_markup=get_add_score_kb(team.id)
        )
    except Exception as e:
        logging.critical(f'Unable to send message to moderator {station.moderator}: {e}')


@teams.error(ExceptionTypeFilter(tortoise.exceptions.DoesNotExist), F.update.message.as_('message'))
async def handle_team_does_not_exists(event: ErrorEvent, message: Message):
    await message.answer('Объект не найден')
