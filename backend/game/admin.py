from django.contrib import admin

# Register your models here.
from .models import Player, PermanentUpgrade, GameRun, Enemy, Questions, QuestionAttempt

admin.site.register(Player)
admin.site.register(PermanentUpgrade)
admin.site.register(GameRun)
admin.site.register(Enemy)
admin.site.register(Questions)
admin.site.register(QuestionAttempt)
