from tortoise import Tortoise
from teams.models import Station


async def create_stations():
    stations = (
        (1, 'Главный корпус', '', 596546865, 'Карла-Маркса, 1'),
        (2, 'ИМИТ (Актовый зал)', 'ССК Мой спорт', 906656869, 'Бульвар Гагарина, 20'),
        (3, 'ИМИТ (ауд. 223)', 'ПС ГОС', 715069098, 'Бульвар Гагарина, 20'),
        (4, 'ИСН', 'КИИ', 1344027399, 'Ленина, 3'),
        (5, 'ОГЭО', 'ОСС', 1548346472, 'Сухэ-Батора, 9'),
        (6, 'Биолого-почвенный факультет', 'ЦППИ', 1254926558, 'Сухэ-Батора, 5'),
        (7, 'ОПСиСПО', 'ЦРКТ', 1016017136, 'Нижняя Набережная, 8'),
        (8, 'ФМЕНиТО', 'ОССО', 933604860, 'Нижняя Набережная, 6'),
        (9, 'ИФИЯМ ФИЯ (128)', 'ВЦ', 1380009811, 'Ленина, 8'),
        (10, 'ИФИЯМ ФИЖ (130)', 'ОК', 969074375, 'Ленина, 8'),
        (11, 'Факультет психологии', 'КП', 108269675, 'Чкалова, 2'),
    )

    for pk, name, club, moderator, place in stations:
        await Station.get_or_create(
            id=pk,
            name=name,
            club=club,
            moderator=moderator,
            place=place,
        )


async def init():
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={
            'teams': ['teams.models']
        }
    )
    await Tortoise.generate_schemas()

    stations_created = await Station.all().count() > 0
    if not stations_created:
        await create_stations()


async def close_connections():
    await Tortoise.close_connections()
