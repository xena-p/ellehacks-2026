# game/auth.py
from ninja.security import APIKeyHeader

from rest_framework.authtoken.models import Token

class TokenAuth(APIKeyHeader):
    param_name = "Authorization"

    def authenticate(self, request, key):
        print(f"--- AUTH ATTEMPT ---")
        print(f"Header received: {key}") # Check your terminal for this!

        if not key:
            return None

        # Robustly strip "Token " or "Bearer " if they exist
        token_key = key
        if " " in key:
            token_key = key.split(" ")[1]
            
        try:
            # We use select_related to grab the user in one database hit
            token_obj = Token.objects.select_related('user').get(key=token_key)
            print(f"User found: {token_obj.user.username}")
            return token_obj.user
        except Token.DoesNotExist:
            print(f"Token {token_key} NOT found in Neon DB")
            return None