import logging

from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery
)
from aiogram.utils.formatting import as_list
from aiogram.filters import Command, CommandObject

from .keyboards import AddScoreCallback
from teams.models import Team, Station, TeamScoreHistory
from teams.router import send_current_station_for

admin = Router()


@admin.message(Command('teams'))
async def cmd_team(message: Message):
    teams = await Team.all()
    content = as_list(*teams)
    await message.answer(**content.as_kwargs())


@admin.message(F.photo)
async def get_photo_id(message: Message):
    await message.answer(f'<code>{ message.photo[0].file_id }</code>')


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
