from django.views.decorators.csrf import csrf_exempt
from functools import wraps
from ninja import NinjaAPI, Schema
from django.conf import settings
from .gemini_utils import generate_question, QuestionSchema
from .models import Player
from .models import GameRun, Spell, PermanentUpgrade, UserPermanentUpgrade, GameRunSpell
from .models import use_spell
from django.contrib.auth import authenticate, login
from ninja.security import django_auth
from rest_framework.authtoken.models import Token
from .auth import TokenAuth

# Ensure only one NinjaAPI instance exists across different import contexts
api = NinjaAPI() 

class WinResponse(Schema):
    new_coins: int
    new_wins: int
    leveled_up: bool
    message: str

# @api.get("/hello", auth=TokenAuth())
# def hello(request):
#     return {"message": "Hello from your Game Backend!"}

# @api.get("/math_question", auth=TokenAuth())
# def get_math_question(request):
#     return {
#         "question": "5 + 3",
#         "answer": 8,
#         "options": [6, 8, 9, 10]
#     }

@api.post("/buy-health", auth=TokenAuth())
def buy_health(request, amount: int, cost: int):
    """
    Permanently increases the player's max HP by 'amount' if they have enough coins.
    """
    player = request.auth

    if player.coins < cost:
        return {"error": "Not enough coins"}, 400

    # Deduct coins and increase max HP
    player.coins -= cost
    player.max_hp += amount
    player.save()

    return {
        "new_coins": player.coins,
        "new_max_hp": player.max_hp  # send back to frontend
    }

@api.get("/generate-quiz", response=QuestionSchema, auth=TokenAuth())
def get_quiz_question(request):
    if request.auth.is_authenticated:
        player_level = request.auth.level
        print(f"Generating question for {request.auth.username} at Level {player_level}")
        return generate_question(player_level)
    
    # 2. If not logged in (testing/guest), default to Level 1
    else:
        return generate_question(1)
    

@api.post("/report-win", response=WinResponse, auth=TokenAuth())
def report_win(request):
    player = request.auth
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

@api.post("/auth/signup")
def signup(request, username: str, password: str):
    if Player.objects.filter(username=username).exists():
        return {"error": "Username taken"}

    user = Player.objects.create_user(
        username=username,
        password=password
    )
    token, _ = Token.objects.get_or_create(user=user)
    return {"success": True, "token": token.key}


@api.post("/auth/login")
def login_user(request, username: str, password: str):
    user = authenticate(username=username, password=password)
    token, _ = Token.objects.get_or_create(user=user)
    return {"success": True, "token": token.key}


@api.get("/player", auth=TokenAuth())
def get_player(request):
    player = request.auth
    return {
        "level": player.level,
        "max_hp": player.max_hp,
        "coins": player.coins,
        "wins": player.wins
    }

# @api.post("/game/start", auth=TokenAuth())
# def start_game(request):
#     if not request.auth.is_authenticated:
#         return {"message": "Authentication required"}, 401

#     user = request.auth
#     map_level = user.level  # Start game at user's current level

#     if not user.can_access_map(map_level):
#         return {"error": "Map locked"}

#     run = GameRun.objects.create(
#         user=user,
#         map_level=map_level,
#         current_hp=user.get_max_hp()
#     )

#     return {
#         "game_run_id": run.id,
#         "starting_hp": run.current_hp,
#         "map_level": run.map_level
#     }



@api.post("/shop/buy-spell", auth=TokenAuth())
def buy_spell(request, spell_id: int, game_run_id: int):
    user = request.auth
    spell = Spell.objects.get(id=spell_id)

    if user.coins < spell.cost:
        return {"error": "Not enough coins"}

    run = GameRun.objects.get(id=game_run_id, user=user, active=True)

    GameRunSpell.objects.create(game_run=run, spell=spell)
    user.coins -= spell.cost
    user.save()
    return {"success": True, "coins": user.coins}

@api.post("/shop/buy-upgrade", auth=TokenAuth())
def buy_upgrade(request, upgrade_id: int):
    user = request.auth
    upgrade = PermanentUpgrade.objects.get(id=upgrade_id)

    if user.coins < upgrade.cost:
        return {"error": "Not enough coins"}

    UserPermanentUpgrade.objects.create(user=user, upgrade=upgrade)
    user.coins -= upgrade.cost
    user.save()
    return {"success": True, "coins": user.coins}

@api.post("/game/use-spell", auth=TokenAuth())
def api_use_spell(request, game_run_id: int, spell_id: int):
    run = GameRun.objects.get(
        id=game_run_id,
        user=request.auth,
        active=True
    )

    use_spell(run, spell_id)
    return {"current_hp": run.current_hp}

@api.post("/game/end", auth=TokenAuth())
def end_game(request, game_run_id: int, won: bool):
    run = GameRun.objects.get(
        id=game_run_id,
        user=request.auth,
        active=True
    )

    run.end_run(won)

    return {
        "won": won,
        "new_level": request.user.level,
        "coins": request.user.coins
    }
