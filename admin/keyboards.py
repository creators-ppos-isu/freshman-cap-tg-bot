from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder


class AddScoreCallback(CallbackData, prefix='add-score'):
    score: int
    team_id: int


def get_add_score_kb(team_id: int):
    builder = InlineKeyboardBuilder()

    for score in range(1, 6):
        builder.button(
            text=str(score),
            callback_data=AddScoreCallback(score=score, team_id=team_id)
        )
    builder.adjust(1, repeat=True)

    return builder.as_markup()
