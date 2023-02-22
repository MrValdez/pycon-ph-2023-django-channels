# chat/views.py
from django.shortcuts import render, redirect
from better_profanity import profanity


profanity.load_censor_words()


def index(request):
    return render(request, "chat/index.html")
    

def room(request, room_name):
    if profanity.contains_profanity(room_name):
        return redirect("chat:room", room_name="Jail")

    return render(request, "chat/room.html", {"room_name": room_name})