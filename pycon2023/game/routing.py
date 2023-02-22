from django.urls import path

from . import consumers


urlpatterns = [
    path("ws/game/", consumers.GameConsumer.as_asgi()),
]