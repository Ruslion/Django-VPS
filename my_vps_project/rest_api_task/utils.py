import jwt
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from constance import config
from rest_framework import exceptions

def generate_access_token(user_id):
    exp = timezone.now() + timedelta(seconds=config.ACCESS_TOKEN_LIFETIME_SECONDS)
    payload = {
        'user_id': user_id,
        'exp': exp,
        'iat': timezone.now(),
        'token_type': 'access'
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

def verify_token(token, token_type='access'):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        if payload.get('token_type') != token_type:
            raise exceptions.AuthenticationFailed('Invalid token type')
        return payload
    except jwt.ExpiredSignatureError:
        raise exceptions.AuthenticationFailed('Token has expired')
    except jwt.InvalidTokenError:
        raise exceptions.AuthenticationFailed('Invalid token')