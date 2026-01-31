from ninja import NinjaAPI, Schema
from django.conf import settings
from .gemini_utils import generate_question, QuestionSchema

# Ensure only one NinjaAPI instance exists across different import contexts
if not hasattr(settings, "ELLEHACKS_NINJA_API"):
    settings.ELLEHACKS_NINJA_API = NinjaAPI()

api = settings.ELLEHACKS_NINJA_API

class WinResponse(Schema):
    new_coins: int
    new_wins: int
    leveled_up: bool
    message: str

@api.get("/hello")
def hello(request):
    return {"message": "Hello from your Game Backend!"}

@api.get("/math_question")
def get_math_question(request):
    return {
        "question": "5 + 3",
        "answer": 8,
        "options": [6, 8, 9, 10]
    }


@api.get("/generate-quiz", response=QuestionSchema)
def get_quiz_question(request):
    if request.user.is_authenticated:
        player_level = request.user.level
        print(f"Generating question for {request.user.username} at Level {player_level}")
        return generate_question(player_level)
    
    # 2. If not logged in (testing/guest), default to Level 1
    else:
        return generate_question(1)
    

@api.post("/report-win", response=WinResponse)
def report_win(request):
    if not request.user.is_authenticated:
         return api.create_response(request, {"detail": "Not logged in"}, status=401)
    
    player = request.user
    # It adds a win, adds coins, and checks if level should go up.
    leveled_up = player.add_win(coins_earned=10) 
    
    msg = "Victory!"
    if leveled_up:
        msg = f"LEVEL UP! You are now level {player.level}!"

    return {
        "new_coins": player.coins,
        "new_wins": player.wins,
        "leveled_up": leveled_up,
        "message": msg
    }