from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import Q
# Create your models here.



LEVEL_THRESHOLDS = {
    1: 0,
    2: 1,
    3: 2,
    4: 3,
    5: 5,
}



class PermanentUpgrade(models.Model):
    name = models.CharField(max_length=100)
    hp_bonus = models.IntegerField(default=0)
    cost = models.IntegerField()

    def __str__(self):
        return self.name

class Player(AbstractUser):
    coins = models.IntegerField(default=100) #start with 100 coins
    wins = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    base_hp = models.IntegerField(default=100)
    
    created_at = models.DateTimeField(auto_now_add=True)
    MAX_LEVEL = 5

    upgrades = models.ManyToManyField(
        PermanentUpgrade, 
        through='UserPermanentUpgrade',
        related_name='owners'
    )

    class Meta:
        #This helps fix some collision errors
        verbose_name = 'Player'
        verbose_name_plural = 'Players'

    @property
    def max_hp(self):
        bonus = sum(
            u.upgrade.hp_bonus
            for u in self.permanent_upgrades.select_related("upgrade")
        )
        return self.base_hp + bonus
    
    def get_attackpower(self): #at a later point in time, change so that you can upgrade attack power
        """Calculate attack damage (base + equipment)"""
        base_attack = 25
        
        return base_attack
    
    def update_username(self, new_username):
        self.username = new_username
        self.save()

    def update_password(self, new_password):
        self.set_password(new_password)
        self.save()
    
    def recalculate_level(self):
        
        new_level = max(
            lvl for lvl, wins_req in LEVEL_THRESHOLDS.items()
            if self.wins >= wins_req
        )
        self.level = min(new_level, self.MAX_LEVEL)
        self.save(update_fields=["level"])

    #might not need

    
    def can_access_map(self, map_level: int):
        return self.level >= map_level

    def add_win(self, coins_earned: int):
        if self.level < self.MAX_LEVEL:
            self.wins += 1
        self.coins += coins_earned
        self.save(update_fields=["wins", "coins"])

    
    def __str__(self):
        return f"{self.username} (Level {self.level})"


class Questions(models.Model):
    SOURCE_CHOICES = [
        ("seed", "Seed"),
        ("gemini", "Gemini"),
    ]
    level = models.PositiveSmallIntegerField()   
    question_text = models.TextField()
    answer_choices = models.JSONField()
    correct_answer_index = models.IntegerField()
    explanation = models.TextField()

    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES
    )
    fingerprint = models.CharField(
        max_length=64,
        unique=True
    )
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)




class UserPermanentUpgrade(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="permanent_upgrades",
        on_delete=models.CASCADE
    )
    upgrade = models.ForeignKey(PermanentUpgrade, on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "upgrade")



    
class GameRun(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    map_level = models.IntegerField(default=1)
    current_hp = models.IntegerField()
    enemy_name = models.CharField(max_length=100, default="unknown")
    enemy_hp = models.IntegerField(default=50)
    enemy_max_hp = models.IntegerField(default=50)
    enemy_attack_power = models.IntegerField(default=10)
    active = models.BooleanField(default=True)
    reward_coins = models.IntegerField(default=10)
    started_at = models.DateTimeField(auto_now_add=True)

    

    def damage_enemy(self, amount: int):
        self.enemy_hp=max(0, self.enemy_hp - amount)
        self.save()

    def damage_player(self, amount: int):
        self.current_hp=max(0, self.current_hp - amount)
        self.save()

    def is_won(self):
        return self.enemy_hp <= 0

    def is_lost(self):
        return self.current_hp <= 0

    def end_run(self):
        self.active = False
        self.save()

class QuestionAttempt(models.Model):
    game_run = models.ForeignKey(GameRun, on_delete=models.CASCADE, related_name="question_attempts")
    question = models.ForeignKey(Questions, on_delete=models.PROTECT)
    selected_answer_index = models.PositiveSmallIntegerField(
        null=True, blank=True
    )
    correct = models.BooleanField(
        null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["game_run"],
                condition=Q(answered_at__isnull=True),
                name="unique_active_unanswered_per_game_run",
            )
        ]



class Spell(models.Model):
    EFFECT_CHOICES = [
        ("heal", "Heal"),
        ("damage", "Damage"),
        ("shield", "Shield"),
    ]

    name = models.CharField(max_length=100)
    effect = models.CharField(max_length=20, choices=EFFECT_CHOICES)
    value = models.IntegerField()
    duration = models.IntegerField(default=0)  # turns, 0 = instant
    cost = models.IntegerField()

    def __str__(self):
        return self.name
    
class GameRunSpell(models.Model):
    game_run = models.ForeignKey(
        GameRun, related_name="spells", on_delete=models.CASCADE
    )
    spell = models.ForeignKey(Spell, on_delete=models.CASCADE)
    used = models.BooleanField(default=False)
    turns_remaining = models.PositiveSmallIntegerField(default=0)








def use_spell(self, game_run: GameRun, spell_id: int):
    run_spell = GameRunSpell.objects.get(
        game_run=game_run,
        spell_id=spell_id,
        used=False
    )

    spell = run_spell.spell

    if spell.effect == "heal":
        game_run.current_hp += spell.value

    # damage / shield handled in game engine logic

    run_spell.used = True
    run_spell.save()
    game_run.save()

class Enemy(models.Model):
    name = models.CharField(max_length=100)
    level = models.IntegerField(default=1)

    def get_max_hp(self):
        return 40 + (self.level * 10)

    def get_attack_power(self):
        return 5 + (self.level * 5)

    def get_coin_reward(self):
        return 5 + (self.level * 5)


    def __str__(self):
        return self.name