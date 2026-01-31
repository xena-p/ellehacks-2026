from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
# Create your models here.

class TestItem(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

LEVEL_THRESHOLDS = {
    1: 0,
    2: 1,
    3: 2,
    4: 3,
}

class Player(AbstractUser):
    coins = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    MAX_LEVEL = 4
    class Meta:
        # This helps fix some collision errors
        verbose_name = 'Player'
        verbose_name_plural = 'Players'

    def get_max_hp(self):
        base_hp = 100
        upgrades = UserPermanentUpgrade.objects.filter(user=self)
        bonus = sum(u.upgrade.hp_bonus for u in upgrades)
        return base_hp + bonus
    
    def get_attack_power(self):
        """Calculate attack damage (base + equipment)"""
        base_attack = 25
        
        return base_attack
    
    def calculate_level(self):
        new_level = self.level
        for level, required_wins in LEVEL_THRESHOLDS.items():
            if self.wins >= required_wins:
                new_level = level
        return new_level

    def add_win(self, coins_earned=0):
        self.wins += 1
        self.coins += coins_earned

        leveled_up = False
        if self.level < self.MAX_LEVEL:
            self.level += 1
            leveled_up = True
        self.save()
        return leveled_up
    
    def can_access_area(self, area_level):
        #map access
        return self.level >= area_level
    
    def buy_upgrade(user, upgrade_id):
        upgrade = PermanentUpgrade.objects.get(id=upgrade_id)

        if user.coins < upgrade.cost:
            raise ValueError("Not enough coins")

        UserPermanentUpgrade.objects.create(
            user=user,
            upgrade=upgrade
        )

        user.coins -= upgrade.cost
        user.save()

    
    def __str__(self):
        return f"{self.username} (Level {self.level})"


class PermanentUpgrade(models.Model): #possible upgrades that can be purchased
    name = models.CharField(max_length=100)
    hp_bonus = models.IntegerField(default=0)
    cost = models.IntegerField()

class UserPermanentUpgrade(models.Model): #the upgrades that a user has purchased
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    upgrade = models.ForeignKey(PermanentUpgrade, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "upgrade")

class Spell(models.Model): #for the temp spells
    EFFECT_CHOICES = [
        ("heal", "Heal"),
        ("damage", "Damage"),
        ("shield", "Shield"),
        ("buff_attack", "Buff Attack"),
        ("buff_hp", "Buff Max HP"),
    ]

    name = models.CharField(max_length=100)
    effect = models.CharField(max_length=50)  # "heal", "double_damage"
    value = models.IntegerField()
    duration = models.IntegerField(default=0)  # turns (0 = instant)
    cost = models.IntegerField()

class GameRun(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    current_hp = models.IntegerField()
    started_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)



class GameRunSpell(models.Model):
    game_run = models.ForeignKey(GameRun, on_delete=models.CASCADE)
    spell = models.ForeignKey(Spell, on_delete=models.CASCADE)
    used = models.BooleanField(default=False)


def use_spell(game_run, spell_id):
    run_spell = GameRunSpell.objects.get(
        game_run=game_run,
        spell_id=spell_id,
        used=False
    )

    if run_spell.spell.effect == "heal":
        game_run.current_hp += run_spell.spell.value

    run_spell.used = True
    run_spell.save()
    game_run.save()