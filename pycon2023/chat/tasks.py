from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from celery import shared_task
from celery.utils.log import get_task_logger

import random

logger = get_task_logger(__name__)
channel_layer = get_channel_layer()


@shared_task
def get_chat_facts():
    facts = [
        "Did you know? <todo: insert fact>",
    ]
    fact = random.choice(facts)

    logger.info(fact)

    return fact


@shared_task
def send_chat_facts():
    room_group_name = "chat_PyCon-PH-2023"
    args = {
        "type": "chat.message",
        "message": get_chat_facts(),
    }

    async_to_sync(channel_layer.group_send)(room_group_name, args)