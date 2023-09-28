import logging
import asyncio
from typing import Dict, Any, Callable, Awaitable

import tortoise.exceptions
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery, Update, ErrorEvent
)
from aiogram.utils.formatting import as_list, as_key_value
from aiogram.filters import Command, CommandObject, ExceptionTypeFilter

from .keyboards import AddScoreCallback
from .states import CreatingPost

from teams.models import Team, Station, TeamScoreHistory
from teams.router import send_current_station_for

admin = Router()


class AccessDenied(Exception):
    pass


@admin.message.middleware()
async def check_admin(
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
):
    if event.from_user.id not in {596546865}:
        raise AccessDenied()
    return await handler(event, data)


@admin.error(ExceptionTypeFilter(AccessDenied), F.update.message.as_('message'))
async def handle_access_denied(event: ErrorEvent, message: Message):
    await message.answer('У Вас недостаточно прав для доступа к этим функциям')


def format_teams(teams):
    return as_list(*[
        as_list(
            as_key_value('ID', team.id),
            as_key_value('Подразделение', team.division),
            as_key_value('Название', team.name),
            as_key_value('Баллы', team.score),
            as_key_value('Пройдено станций', team.progress),
        ) for team in teams], sep='\n\n')


@admin.message(Command('teams'))
async def cmd_team(message: Message):
    teams = await Team.all()
    content = format_teams(teams)
    await message.answer(**content.as_kwargs())


@admin.message(Command('rating'))
async def cmd_rating(message: Message):
    teams = await Team.all().order_by('-score')
    content = format_teams(teams)
    await message.answer(**content.as_kwargs())


@admin.message(F.photo & F.caption.regexp(r'\d+'))
async def upload_station_image(message: Message):
    try:
        station_id = int(message.caption)

        station = await Station.get(id=station_id)
        photo_id = message.photo[0].file_id
        station.image = photo_id
        await station.save()

        logging.warning(f'Image for station {station.id} uploaded by {message.from_user.id}')
        await message.reply(f'Фотография для станции <b>{station.name}</b> успешно обновлена')

    except tortoise.exceptions.DoesNotExist:
        await message.reply('Станция с данным ID не найдена')


@admin.message(Command('start_route'))
async def cmd_start_route(message: Message, command: CommandObject):
    route = int(command.args)
    team = await Team.get(id=route)

    await send_current_station_for(team, message)

    await message.answer(f'Успешно отправлена текущая станция для команды {team.name}')


@admin.callback_query(AddScoreCallback.filter())
async def add_score_callback(query: CallbackQuery, callback_data: AddScoreCallback):
    team = await Team.get(id=callback_data.team_id)

    station = await Station.get(moderator=query.from_user.id)
    await TeamScoreHistory.create(team=team, station=station, score=callback_data.score)

    await query.message.answer(f'Вы поставили свою оценку команде {team.name}')

    team.progress += 1
    team.score += callback_data.score

    await team.save()

    await query.bot.send_message(
        chat_id=team.leader,
        text=f'Вам поставили оценку <b>{callback_data.score}</b> на станции <b>{station.name}</b>'
    )
    await send_current_station_for(team, query.message)
    await query.message.edit_reply_markup()


@admin.message(Command('mailing'))
async def cmd_mailing(message: Message, state: FSMContext):
    """Рассылка"""
    await state.set_state(CreatingPost.write_content)
    await message.answer('Введите текст для рассылки пользователям')


@admin.message(CreatingPost.write_content)
async def process_post_content(message: Message, state: FSMContext):
    leaders = await Team.all().values_list('leader')
    leaders = tuple(zip(*leaders))[0]  # get first column of matrix

    await message.reply('Начинаю рассылку...')

    for leader in leaders:
        try:
            await message.copy_to(leader)
        except Exception as e:
            await message.answer(f'Не удалось отправить сообщение пользователю {leader}: {e}')
        finally:
            await asyncio.sleep(1)

    await message.answer('Рассылка успешно завершена')
    await state.clear()
