from aiogram.fsm.state import State, StatesGroup


class TeamReg(StatesGroup):
    name = State()
