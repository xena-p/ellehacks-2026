from ninja import Schema
from datetime import datetime
from rest_framework.authtoken.models import Token

class SignInReq(Schema):
    username: str
    password: str

class SignInRes(Schema):
    username: str
    token: str 

class BuyHealthSchema(Schema):
    pack_id: str

class PublicQuestionSchema(Schema):
    question_id: int
    question: str
    options: list[str]


class WinResponse(Schema):
    new_coins: int
    new_wins: int
    leveled_up: bool
    message: str

#in
class AnswerIn(Schema):
    selected_index: int

#out
class AnswerResult(Schema):
    correct: bool | None = None
    correct_index: int | None = None
    explanation: str | None = None
    current_hp: int | None = None
    enemy_hp: int | None = None
    outcome: str | None = None
    new_coins: int | None = None
    reward_coins: int | None = None
    leveled_up: bool | None = None
    level: int | None = None
    new_wins: int | None = None
    message: str | None = None
class GeneratedQuestionSchema(Schema):
    question: str
    options: list[str]
    answer: str
    explanation: str

class StartGameResponse(Schema):
    game_run_id: int
    map_level: int
    current_hp: int
    max_hp: int
    enemy_name: str
    enemy_max_hp: int
    enemy_attack_power: int
    enemy_hp: int
    reward_coins: int
    coins: int
    active: bool

class StartGameRequest(Schema):
    map_level: int


class BuySpellRequest(Schema):
    game_run_id: int
    spell_id: int


class UseSpellRequest(Schema):
    game_run_id: int
    game_run_spell_id: int


class EndGameRequest(Schema):
    game_run_id: int
    won: bool


class SpellResponse(Schema):
    id: int
    code: str
    name: str
    effect: str
    value: int
    duration: int
    cost: int


class GameRunSpellResponse(Schema):
    id: int
    used: bool
    purchased_at: datetime
    used_at: datetime | None
    spell: SpellResponse


class RunResponse(Schema):
    id: int
    map_level: int
    current_hp: int
    max_hp: int
    shield_charges: int
    next_attack_multiplier: int
    active: bool
    spells: list[GameRunSpellResponse]


class PlayerStateResponse(Schema):
    coins: int
    wins: int
    level: int


class RunStateResponse(Schema):
    run: RunResponse
    player: PlayerStateResponse