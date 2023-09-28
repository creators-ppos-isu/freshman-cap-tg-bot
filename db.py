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
        (2, 'ИМИТ (Актовый зал)', 0, 'Бульвар Гагарина, 20'),
        (3, 'ИМИТ (ауд. 223)', 0, 'Бульвар Гагарина, 20'),
        (4, 'ИСН', 0, 'Ленина, 3'),
        (5, 'ОГЭО', 0, 'Сухэ-Батора, 9'),
        (6, 'Биолого-почвенный факультет', 0, 'Сухэ-Батора, 5'),
        (7, 'ОПСиСПО', 0, 'Нижняя Набережная, 8'),
        (8, 'ФМЕНиТО', 0, 'Нижняя Набережная, 6'),
        (9, 'ИФИЯМ ФИЯ (128)', 0, 'Ленина, 8'),
        (10, 'ИФИЯМ ФИЖ (130)', 0, 'Ленина, 8'),
        (11, 'Факультет психологии', 0, 'Чкалова, 2'),
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
