import random

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings
from redis import Redis
from .tasks import teams
from . import tasks


redis_db = Redis(*settings.REDIS_URL, decode_responses=True)


class GameConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self):
        super().__init__()

        self.team = random.choice(teams)

    async def connect(self):
        args = (self.team, self.channel_name,)
        await self.channel_layer.group_add(*args)

        await self.accept()
        await self.setup()

    async def disconnect(self, close_code):
        args = (self.team, self.channel_name,)
        await self.channel_layer.group_discard(*args)

    async def receive_json(self, content, **kwargs):
        tasks.play_move(self.team, content["move"])

        # Every time a message is receive by the server, it will then send a game state update back.
        # For some games/app, this might use up too much bandwidth. But it helps with responsiveness.
        # As a developer, it's up to you to find the balance.
        await self.update()

    async def setup(self):
        await self.change_team()
        await self.update()

    async def game_send_update(self, event):
        await self.update()

    async def update(self):
        await self.update_game_state()
        await self.update_last_match_result()

    async def change_team(self):
        args = {
            "event": "CHANGE_TEAM",
            "message": self.team,
        }
        await self.send_json(args)

    async def update_game_state(self):
        game_state = tasks.get_game_state(self.team)

        args = {
            "event": "UPDATE_GAME",
            "message": game_state,
        }

        await self.send_json(args)

    async def update_last_match_result(self):
        winner_text = redis_db.get("LAST_MATCH_WINNER")
        if winner_text not in ("RED", "BLUE"):
            winner_text = "BOTH TIED!"
        else:
            winner_text = winner_text + " won!"

        args = {
            "event": "UPDATE_LAST_MATCH_RESULTS",
            "message": {
                "LAST_MATCH_RED": redis_db.get("LAST_MATCH_RED"),
                "LAST_MATCH_BLUE": redis_db.get("LAST_MATCH_BLUE"),
                "WINNER_TEXT": winner_text,
            },
        }
        await self.send_json(args)
