# Most of the code here should be under a dedicated game.py instead of tasks.py. But to simplify the workshop
# and minimize additional setups, tasks.py is used.

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from celery import shared_task
from django.conf import settings
from redis import Redis

import random


channel_layer = get_channel_layer()
redis_db = Redis(*settings.REDIS_URL, decode_responses=True)

teams = ["RED", "BLUE"]
max_timer = 10


def check_winner(red, blue):
    # rock (0), paper (1), scissors (2)

    if red == blue:
        return "TIE"
    elif ((red + 1) % 3) == blue:
        return "BLUE"
    else:
        return "RED"

@shared_task
def update_game_tick():
    current_timer = redis_db.decr("game_TIMER")

    if current_timer <= 0:
        def get_highest_vote(team):
            rock_vote, paper_vote, scissors_vote = get_votes(team)
            choices = []

            highest = max([rock_vote, paper_vote, scissors_vote])
            if rock_vote == highest:
                choices.append(0)
            if paper_vote == highest:
                choices.append(1)
            if scissors_vote == highest:
                choices.append(2)

            return random.choice(choices)

        red = get_highest_vote("RED")
        blue = get_highest_vote("BLUE")
        winner = check_winner(red, blue)

        names = ["ROCK", "PAPER", "SCISSORS"]

        redis_db.set("LAST_MATCH_RED", names[red])
        redis_db.set("LAST_MATCH_BLUE", names[blue])
        redis_db.set("LAST_MATCH_WINNER", winner)

        game_reset()

    send_game_state()

def play_move(team, move):
    key = f"game_{team}_{move.upper()}"
    redis_db.incr(key)

def get_votes(team):
    rock_vote = redis_db.get(f"game_{team}_ROCK")
    rock_vote = int(rock_vote) if rock_vote else 0

    paper_vote = redis_db.get(f"game_{team}_PAPER")
    paper_vote = int(paper_vote) if paper_vote else 0

    scissors_vote = redis_db.get(f"game_{team}_SCISSORS")
    scissors_vote = int(scissors_vote) if scissors_vote else 0

    return rock_vote, paper_vote, scissors_vote

def get_game_state(team):
    rock_vote, paper_vote, scissors_vote = get_votes(team)
    total_votes = max((rock_vote + paper_vote + scissors_vote), 1)

    current_timer = redis_db.get("game_TIMER")

    game_state = {
        "ROCK_VOTE": rock_vote / total_votes * 100,
        "PAPER_VOTE": paper_vote / total_votes * 100,
        "SCISSORS_VOTE": scissors_vote / total_votes * 100,
        "TIMER": current_timer,
        "MAX_TIMER": max_timer,
    }

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

    for team in teams:
        keys = [
            f"game_{team}_ROCK",
            f"game_{team}_PAPER",
            f"game_{team}_SCISSORS",
        ]

        for key in keys:
            redis_db.set(key, 1)

    for team in teams:
        key = f"game_{team}_PLAYERS"
        redis_db.delete(key)

    redis_db.set("game_TIMER", max_timer)


# Force game reset when django starts
game_reset()