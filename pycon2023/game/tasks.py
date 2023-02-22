# Most of the code here should be under a dedicated game.py instead of tasks.py. But to simplify the workshop
# and minimize additional setups, tasks.py is used.

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from celery import shared_task
from django.conf import settings
from redis import Redis


channel_layer = get_channel_layer()
redis_db = Redis(*settings.REDIS_URL, decode_responses=True)

teams = ["RED", "BLUE"]
max_timer = 10


@shared_task
def update_game_tick():
    current_timer = redis_db.decr("game_TIMER")

    if current_timer <= 0:
        game_reset()

    send_game_state()


def get_game_state(team):
    current_timer = redis_db.get("game_TIMER")

    game_state = {
        "TIMER": current_timer,
        "MAX_TIMER": max_timer,
    }
    print(game_state)

    return game_state

def send_game_state():
    for team in teams:
        try:
            args = {
                "type": "game.send_update",
                "message": get_game_state(team)
            }

            async_to_sync(channel_layer.group_send)(team, args)
        except:
            # It's possible that a channel haven't join group RED or group BLUE. This would cause an exception (RuntimeError: Event loop is closed).
            # The correct way to handle this is to store the channels who joined a group (maybe via redis or session), then check
            # if it is not empty before sending to the group.
            # But for the workshop's simplicity, we are ignoring this error.
            pass

def game_reset():
    print("Restarting game")

    redis_db.set("game_TIMER", max_timer)


# Force game reset when django starts
game_reset()