from aiohttp import web
from teams.models import Team, TeamScoreHistory
from tortoise.contrib.aiohttp import register_tortoise


routes = web.RouteTableDef()


@routes.get('/teams')
async def get_all_teams(request):
    teams = await Team.all()
    response = []
    for team in teams:
        current_station = await team.get_current_station()
        response.append({
            'id': team.id,
            'division': team.division,
            'name': team.name,
            'score': team.score,
            'progress': team.progress,
            'station': {
                'id': current_station.id,
                'name': current_station.name,
                'place': current_station.place
            }
        })

    return web.json_response(response)


@routes.get('/team/{id}/history')
async def get_team_score_history(request):
    team_id = int(request.match_info['id'])
    team = await Team.get(id=team_id)
    history = await TeamScoreHistory.filter(team=team).values('station__id', 'station__name', 'station__club', 'score')

    return web.json_response({
        'team': {
            'division': team.division,
            'name': team.name
        },
        'history': history
    })


app = web.Application()
app.add_routes(routes)

if __name__ == '__main__':
    register_tortoise(
        app, db_url="sqlite://db.sqlite3", modules={"teams": ["teams.models"]}
    )
    web.run_app(app, port=5000)
