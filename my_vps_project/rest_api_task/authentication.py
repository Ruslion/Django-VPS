from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework import authentication
from rest_framework import exceptions
from django.contrib.auth.models import User
from .utils import verify_token

class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise exceptions.AuthenticationFailed('Authentication credentials were not provided.')

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            raise exceptions.AuthenticationFailed('Invalid authorization header format. Use Bearer token')

        token = parts[1]
        try:
            payload = verify_token(token, 'access')
            user = User.objects.get(id=payload['user_id'])
            return (user, None)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('User not found')
        except Exception as e:
            raise exceptions.AuthenticationFailed('Invalid or expired token')

    def authenticate_header(self, request):
        """
        This is required to return 401 instead of 403
        """
        return 'Bearer'

class JWTAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = JWTAuthentication  
    name = 'JWT'  

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
            'description': 'Enter JWT token in format: Bearer <token>'
        }