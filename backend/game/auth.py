# game/auth.py
from ninja.security import APIKeyHeader
from rest_framework.authtoken.models import Token

class TokenAuth(APIKeyHeader):
    param_name = "Authorization"

    def authenticate(self, request, key):
        if not key:
            return None
        # Expect header: Authorization: Token <key>
        if key.startswith("Token "):
            key = key.split(" ")[1]
        try:
            token = Token.objects.get(key=key)
            return token.user
        except Token.DoesNotExist:
            return None
