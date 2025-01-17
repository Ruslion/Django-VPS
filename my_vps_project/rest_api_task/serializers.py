from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import RefreshToken

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = User.objects.filter(email=data['email']).first()
        if user and authenticate(username=user.username, password=data['password']):
            return user
        raise serializers.ValidationError("Invalid email or password")

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('id', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.UUIDField()

    def validate(self, attrs):
        try:
            token = RefreshToken.objects.get(token=attrs['refresh_token'])
            
            # Check if token is expired or inactive
            if not token.is_valid():
                raise serializers.ValidationError({
                    "refresh_token": "Token is expired or invalid"
                })
                
            attrs['token'] = token
            return attrs
            
        except RefreshToken.DoesNotExist:
            raise serializers.ValidationError({
                "refresh_token": "Invalid refresh token"
            })

class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.UUIDField()

    def validate(self, attrs):
        try:
            token = RefreshToken.objects.get(token=attrs['refresh_token'])
            attrs['token'] = token  # Store the token object
            return attrs
        except RefreshToken.DoesNotExist:
            raise serializers.ValidationError({"refresh_token": "Invalid refresh token"})

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        extra_kwargs = {
            'id': {'read_only': True}
        }

    def validate_username(self, value):
        if value and len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long")
        return value

    def update(self, instance, validated_data):
        # Allow partial updates
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance