


from django.db import IntegrityError, transaction
from django.views.decorators.csrf import csrf_exempt
from functools import wraps
from ninja import NinjaAPI
from django.conf import settings
from django.shortcuts import get_object_or_404
from .schemas import PublicQuestionSchema, SignInReq, SignInRes, WinResponse, AnswerIn, AnswerResult, StartGameResponse, StartGameRequest
from .gemini_utils import assign_question
from .models import Player, QuestionAttempt, GameRun, Spell, PermanentUpgrade, UserPermanentUpgrade, GameRunSpell, Enemy
from .models import use_spell
from ninja.security import django_auth
from rest_framework.authtoken.models import Token
from .auth import TokenAuth
from ninja.errors import HttpError
from .services import PlayerService, GameService, InvalidAnswerIndexError
# Ensure only one NinjaAPI instance exists across different import contexts
api = NinjaAPI() 


@api.post("/auth/signup", response={201: SignInRes})
def signup(request, data: SignInReq):
    user_service = PlayerService()
    username = data.username
    password = data.password

    user, token = user_service.signup_player(
        username,
        password)
    return 201, {"username": user.username, "token": token.key}


@api.post("/auth/login", response=SignInRes)
def login(request, data: SignInReq):
    user_service = PlayerService()
    username = data.username
    password = data.password

    user, token = user_service.login_player(
        username,
        password
    )
    
    return 200, {"username": user.username, "token": token.key}


@api.get("/player", auth=TokenAuth())
def get_player(request):
    user = request.auth
    return {
        "level": user.level,
        "max_hp": user.max_hp,
        "coins": user.coins,
        "wins": user.wins
    }

#for admin purposes only
@api.post("/game/createenemy", auth=TokenAuth())
def create_enemy(request, name: str, level: int):
    if not request.auth.is_superuser:
        raise HttpError(403, "Unauthorized")
    enemy = Enemy.objects.create(name=name, level=level)
    return {"success": True, "enemy_id": enemy.id}

@api.post("/game/start", response=StartGameResponse, auth=TokenAuth())
@transaction.atomic
def start_game(request, data: StartGameRequest):
    user = (
        Player.objects
        .select_for_update()
        .get(id=request.auth.id)
    )
    map_level = data.map_level # Start game at user's current level

    if not user.can_access_map(map_level):
        raise HttpError(403, "Map locked")
    run = (
        GameRun.objects
        .select_for_update()
        .filter(
            user=user,
            map_level=map_level,
            active=True,
        )
        .order_by("-started_at")
        .first()
    )

    resumed = run is not None

    if run is None:
        enemy = (
            Enemy.objects
            .filter(level=map_level)
            .order_by("?")
            .first()
        )

        if enemy is None:
            raise HttpError(
                404,
                "No enemy configured for this map",
            )

        enemy_max_hp = enemy.get_max_hp()

        run = GameRun.objects.create(
            user=user,
            map_level=map_level,
            enemy_name=enemy.name,
            enemy_hp=enemy_max_hp,
            enemy_max_hp=enemy_max_hp,
            enemy_attack_power=enemy.get_attack_power(),
            current_hp=user.max_hp,
            reward_coins=enemy.get_coin_reward(),
        )

    return {
        "game_run_id": run.id,
        "map_level": run.map_level,
        "current_hp": run.current_hp,
        "max_hp": user.max_hp,
        "enemy_name": run.enemy_name,
        "enemy_hp": run.enemy_hp,
        "enemy_max_hp": run.enemy_max_hp,
        "enemy_attack_power": run.enemy_attack_power,
        "reward_coins": run.reward_coins,
        "coins": user.coins,
        "active": run.active,
    }


@api.post("/buy-health", auth=TokenAuth())
def buy_health(request, upgrade_id: int):#change to pack id (no amount and cost)
    """
    Permanently increases the player's max HP by 'amount' if they have enough coins.
    """
    user = request.auth

    success, response = user.buy_upgrade(upgrade_id) #make it for pack id

    if not success:
        raise HttpError(400, "Invalid data")

    return response

@api.get("/game/{game_run_id}/generate-quiz", response=PublicQuestionSchema, auth=TokenAuth())
@transaction.atomic
def get_quiz_question(request, game_run_id: int):
    try:
        game_run = get_object_or_404(
            GameRun,
            id=game_run_id,
            user=request.auth,
            active=True
        )
        question_attempt = assign_question(game_run)

        return {
            "question_id": question_attempt.id,
            "question": question_attempt.question.question_text,
            "options": question_attempt.question.answer_choices
        }

    except IntegrityError:
        raise HttpError(
            409, "An unanswered prompt already exists for this game run."
        )
    
    # 2. If not logged in (testing/guest), default to Level 1
    # else:
    #     return generate_question(1)
    
#NEED TO FINISH
@api.post("/game/{attempt_id}/answer", response=AnswerResult, auth=TokenAuth())
@transaction.atomic
def submit_answer(request, attempt_id: int, data: AnswerIn):
    try:
        game_service = GameService()
        return game_service.process_ans(user=request.auth, attempt_id=attempt_id, idx=data.selected_index)
    except InvalidAnswerIndexError as exc:
        raise HttpError(400, str(exc))
    
    




# @api.post("/report-win", response=WinResponse, auth=TokenAuth())
# def report_win(request):
#     player = request.auth
#     # It adds a win, adds coins, and checks if level should go up.
#     leveled_up = player.add_win(coins_earned=10) 
    
#     msg = "Victory!"
#     if leveled_up:
#         msg = f"LEVEL UP! You are now level {player.level}!"

#     return {
#         "new_coins": player.coins,
#         "new_wins": player.wins,
#         "leveled_up": leveled_up,
#         "message": msg
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

@api.delete("/player/delete", auth=TokenAuth())
def delete_player(request):
    player = request.auth

    if not player:
        return {"success": False, "error": "User not authenticated"}

    player.delete()

    return {"success": True}

@api.patch("/player/username", auth=TokenAuth())
def update_username(request, new_username: str):

    player = request.auth
    player.update_username(new_username)

    return {"success": True, "username": player.username}

@api.patch("/player/password", auth=TokenAuth())
def update_password(request, new_password: str):

    player = request.auth
    player.update_password(new_password)

    return {"success": True}