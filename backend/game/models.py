from django.db import models
from django.contrib.auth.models import AbstractUser
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
    coins = models.IntegerField(default=100) #start with 100 coins
    wins = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    MAX_LEVEL = 4
    
    class Meta:
        # This helps fix some collision errors
        verbose_name = 'Player'
        verbose_name_plural = 'Players'


    
    def get_attack_power(self):
        """Calculate attack damage (base + equipment)"""
        base_attack = 25
        
        return base_attack
    
    def recalculate_level(self):
        for lvl, wins_required in LEVEL_THRESHOLDS.items():
            if self.wins >= wins_required:
                self.level = lvl
        self.save()


    def add_win(self, coins_earned: int):
        if self.level < 5:
            self.wins += 1
        self.coins += coins_earned
        old_level = self.level
        self.recalculate_level()
        return self.level > old_level  # did they level up?
        
    def can_access_map(self, map_level: int):
        return self.level >= map_level
    
    def get_max_hp(self):
        base_hp = 100
        upgrades = self.permanent_upgrades.all()
        bonus = sum(u.upgrade.hp_bonus for u in upgrades)
        return base_hp + bonus

    
    def buy_upgrade(user, upgrade_id):
        upgrade = PermanentUpgrade.objects.get(id=upgrade_id)

        if user.coins < upgrade.cost:
            raise ("Not enough coins")

        UserPermanentUpgrade.objects.create(
            user=user,
            upgrade=upgrade
        )

        user.coins -= upgrade.cost
        user.save()

    
    def __str__(self):
        return f"{self.username} (Level {self.level})"


class PermanentUpgrade(models.Model):
    name = models.CharField(max_length=100)
    hp_bonus = models.IntegerField(default=0)
    cost = models.IntegerField()

    def __str__(self):
        return self.name


class UserPermanentUpgrade(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="permanent_upgrades",
        on_delete=models.CASCADE
    )
    upgrade = models.ForeignKey(PermanentUpgrade, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "upgrade")

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


class GameRun(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    map_level = models.IntegerField(default=1)
    current_hp = models.IntegerField()
    active = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)

    def end_run(self, won: bool):
        self.active = False
        self.save()

        if won:
            self.user.add_win(coins_earned=25)



class GameRunSpell(models.Model):
    game_run = models.ForeignKey(
        GameRun, related_name="spells", on_delete=models.CASCADE
    )
    spell = models.ForeignKey(Spell, on_delete=models.CASCADE)
    used = models.BooleanField(default=False)



def use_spell(game_run: GameRun, spell_id: int):
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
