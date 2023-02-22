import json

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from better_profanity import profanity

profanity.load_censor_words()


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_name = self.clean_group_name(self.room_name)

        self.room_group_name = f"chat_{self.room_name}"
        
        args = (self.room_group_name, self.channel_name,)
        await self.channel_layer.group_add(*args)

        # global chat notification
        args = ("chat_GLOBAL", self.channel_name,)
        await self.channel_layer.group_add(*args)

        await self.accept()

    async def disconnect(self, close_code):
        args = (self.room_group_name, self.channel_name,)
        await self.channel_layer.group_discard(*args)

    async def receive_json(self, content, **kwargs):
        message = f"{content['message']}"
        # message = f"{self.channel_name}: {content['message']}"         # show the unique channel name

        user = self.scope['user']
        username = user if not user.is_anonymous else "Anonymous"

        message = f"{username}: {message}"

        args = {
            "type": "chat.message",
            "message": message,
        }
        await self.channel_layer.group_send(self.room_group_name, args)

    async def chat_message(self, event):
        message = event["message"]
        message = profanity.censor(message)

        content = {
            "message": message,
        }

        await self.send_json(content)

    def clean_group_name(self, room_name):
        # Group name must be a valid unicode string with length < 100 containing only ASCII alphanumerics, hyphens, underscores, or periods
        if profanity.contains_profanity(room_name):
            return "Jail"

        room_name = room_name[:100]
        for symbol in " !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~":
            room_name = room_name.replace(symbol, "-")

        return room_name