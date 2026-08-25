from django.contrib import admin

# Register your models here.
from .models import Player, PermanentUpgrade, GameRun, Enemy
from .gemini_utils import QuestionSchema

admin.site.register(Player)
admin.site.register(PermanentUpgrade)
admin.site.register(GameRun)
admin.site.register(Enemy)
#admin.site.register(QuestionSchema)