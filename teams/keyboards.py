from aiogram.filters.callback_data import CallbackData


class TeamInPlaceCallback(CallbackData, prefix='next-station'):
    pass


class DivisionCallback(CallbackData, prefix='division'):
    division_id: int
