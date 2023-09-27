from tortoise import Tortoise
from teams.models import Station


async def init():
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={
            'teams': ['teams.models']
        }
    )
    await Tortoise.generate_schemas()

    stations = (
        (1, 'Главный корпус', 596546865, 'Карла-Маркса, 1'),
        # (2, 'ИМИТ', 596546865, 'Бульвар Гагарина, 20')
    )

    for pk, name, moderator, place in stations:
        await Station.get_or_create(
            id=pk,
            name=name,
            moderator=moderator,
            place=place,
        )


async def close_connections():
    await Tortoise.close_connections()
