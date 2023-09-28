from aiogram.fsm.state import State, StatesGroup


class CreatingPost(StatesGroup):
    write_content = State()
