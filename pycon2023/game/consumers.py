import random

from channels.generic.websocket import AsyncJsonWebsocketConsumer

teams = ["RED", "BLUE"]


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

    async def change_team(self):
        args = {
            "event": "CHANGE_TEAM",
            "message": self.team,
        }
        await self.send_json(args)