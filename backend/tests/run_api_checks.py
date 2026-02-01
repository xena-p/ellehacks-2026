print('Running API checks...')

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from game import api as game_api

User = get_user_model()
username = 'test_api_user'
password = 'testpass123'

user, created = User.objects.get_or_create(username=username)
if created:
    user.set_password(password)
    user.save()

# Ensure user has sensible defaults
user.coins = user.coins or 0
user.wins = user.wins or 0
user.level = user.level or 1
user.save()

token, _ = Token.objects.get_or_create(user=user)
print('Token:', token.key)

class Req:
    pass

req = Req()
req.user = user

print('\nCalling get_quiz_question...')
try:
    q = game_api.get_quiz_question(req)
    print('get_quiz_question result:', q)
except Exception as e:
    print('get_quiz_question raised:', repr(e))

print('\nCalling start_game...')
try:
    s = game_api.start_game(req)
    print('start_game result:', s)
except Exception as e:
    print('start_game raised:', repr(e))

print('\nCalling report_win...')
try:
    r = game_api.report_win(req)
    print('report_win result:', r)
except Exception as e:
    print('report_win raised:', repr(e))

print('\nDone.')
