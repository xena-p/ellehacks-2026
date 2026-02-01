from django.contrib import admin

# Register your models here.
from .models import Player, PermanentUpgrade, GameRun
from .gemini_utils import QuestionSchema

admin.site.register(Player)
admin.site.register(PermanentUpgrade)
admin.site.register(GameRun)
#admin.site.register(QuestionSchema)