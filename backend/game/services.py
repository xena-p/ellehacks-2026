from .models import Player, Enemy, PermanentUpgrade, UserPermanentUpgrade, GameRun, GameRunSpell, QuestionAttempt, Questions, Spell
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.db import IntegrityError, transaction
from .models import Player
from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja.errors import HttpError

class InvalidAnswerIndexError(Exception):
    pass


class PlayerService: 

    class UsernameTaken(Exception):
        pass


    class InvalidCredentials(Exception):
        pass

    
    def signup_player(self, username:str, password:str):
        username = username.strip()

        try: 
            with transaction.atomic():
                user = Player.objects.create_user(
                    username=username,
                    password=password
                )
                token, _ = Token.objects.get_or_create(user=user)

        except IntegrityError as error:
            if Player.objects.filter(username=username).exists():
                raise PlayerService.UsernameTaken from error
            raise

        return user, token

    def login_player(self, username:str, password:str):
        username=username.strip()
        user = authenticate(username=username, password=password)
        if user is None:
            raise HttpError(404, "InvalidCredentials")

        token, _ = Token.objects.get_or_create(user=user)

        return user, token

    def __init__(self, user_model=Player):
        self.user_model = user_model
    
    def buy_upgrade(self, upgrade_id):
        upgrade = PermanentUpgrade.objects.get(id=upgrade_id)

        if self.coins < upgrade.cost:
            return False, {"error": "Not enough coins"}
        
        self.base_hp += upgrade.hp_bonus

        UserPermanentUpgrade.objects.create(
            user=self,
            upgrade=upgrade
        )

        self.coins -= upgrade.cost
        self.save()

        return True, {
            "new_coins": self.coins,
            "new_base_hp": self.base_hp  
        }



class GameService:


    class GameError(Exception):
        "Base exception for game-related errors."


    class GameAlreadyCompletedError(GameError):
        def __init__(self):
            super().__init__("Game has already been completed")


    class GameNotWonError(GameError):
        def __init__(self):
            super().__init__("Game has not been won")

            

    
    @transaction.atomic
    def process_ans(self, user, attempt_id, idx):
        question_attempt = get_object_or_404(
                QuestionAttempt.objects.select_for_update().select_related("question", "game_run"),
                id=attempt_id,
                game_run__user=user,
                game_run__active=True,
                answered_at=None,
            )

        question = question_attempt.question
        game_run = question_attempt.game_run

        options = question.answer_choices
        if not 0 <= idx < len(options):
            raise HttpError(400, "Invalid answer index")

        is_correct = (idx == question.correct_answer_index)

        question_attempt.selected_answer_index = idx
        question_attempt.correct = is_correct
        question_attempt.answered_at = timezone.now()
        question_attempt.save(
            update_fields=[
                "selected_answer_index",
                "correct",
                "answered_at"
            ]
        )
        if question_attempt.correct:
            game_run.damage_enemy(user.get_attackpower())
        else:
            game_run.damage_player(game_run.enemy_attack_power)

        game_service = GameService()

        if game_run.is_won() or game_run.is_lost():
            return game_service.complete_game(game_run.id, question_attempt)

        
        return {
            "correct": question_attempt.correct,
            "correct_index": question_attempt.question.correct_answer_index,
            "explanation": question_attempt.question.explanation,
            "current_hp": game_run.current_hp,
            "enemy_hp": game_run.enemy_hp,
            "outcome": None,
            

            "new_coins": user.coins,
            "new_wins": user.wins,
            "level": user.level,
            "leveled_up": False,

            "message": (
                "Correct!"
                if question_attempt.correct
                else "Incorrect!"
            ),

        }
    
    @transaction.atomic
    def complete_game(self, game_run_id, question_attempt):
        game_run = (
            GameRun.objects
            .select_for_update()
            .select_related("user")
            .get(id=game_run_id)
        )
        user = game_run.user

        if not game_run.active:
            raise HttpError(400, "GameAlreadyCompletedError")
        game_run.active = False
        game_run.save(update_fields=["active"])
        

        if not game_run.is_won():
            question = question_attempt.question

            return {
                "correct": question_attempt.correct,
                "correct_index": question.correct_answer_index,
                "explanation": question.explanation,
                "new_coins": user.coins,
                "current_hp": game_run.current_hp,
                "enemy_hp": game_run.enemy_hp,
                "outcome": "lost",
                "leveled_up": question_attempt.correct,
                "new_wins": int(0),
                "message": str("you lost"),
                "level": user.level,
            }
        

        

        if game_run.map_level >= user.level:
            user.recalculate_level()
            user.add_win(game_run.reward_coins)




        return {
            "correct": question_attempt.correct,
            "outcome": str("won"),
            "current_hp": game_run.current_hp,
            "enemy_hp": game_run.enemy_hp,
            "new_coins": user.coins,
            "new_wins": user.wins,
            "reward_coins": game_run.reward_coins,
            "level": user.level,
            "message": str("YOU WON!!"),
        }



        