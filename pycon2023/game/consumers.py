import random

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .tasks import teams
from . import tasks


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
        pass

    async def setup(self):
        await self.change_team()
        await self.update()

    async def game_send_update(self, event):
        await self.update()

    async def update(self):
        await self.update_game_state()

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
