from ninja import Schema
from datetime import datetime

class BuyHealthSchema(Schema):
    pack_id: str

class PublicQuestionSchema(Schema):
    question_id: int
    question: str
    options: list[str]

class AnswerSubmissionSchema(Schema):
    question_id: int
    selected_index: int


class AnswerResultSchema(Schema):
    correct: bool
    correct_index: int
    explanation: str

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