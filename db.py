from tortoise import Tortoise


async def init():
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={
            'teams': ['teams.models']
        }
    )
    await Tortoise.generate_schemas()


async def close_connections():
    await Tortoise.close_connections()
