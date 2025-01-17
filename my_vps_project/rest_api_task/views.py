from drf_spectacular.utils import extend_schema
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserRegistrationSerializer, LoginSerializer, RefreshTokenSerializer, LogoutSerializer, UserSerializer
from .models import RefreshToken
from .utils import generate_access_token
import uuid 

class UserRegistrationView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer
    authentication_classes = []

@extend_schema(
        request=LoginSerializer,
        responses={200: {'description': 'Returns access and refresh tokens'}},
        description='Login endpoint that returns JWT tokens')
class LoginView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer
    authentication_classes = []

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        RefreshToken.objects.filter(user=user).update(is_active=False)
        
        # Generate refresh token
        refresh_token = RefreshToken.objects.create(user=user)

        # Generate access token
        access_token = generate_access_token(user.id)

        return Response({
            'access_token': access_token,
            'refresh_token': str(refresh_token.token)
        }, status=status.HTTP_200_OK)

class RefreshTokenView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = []
    serializer_class = RefreshTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get old refresh token
        old_refresh_token = serializer.validated_data['token']
        
        # Invalidate old token
        old_refresh_token.invalidate()
        
        # Create new refresh token
        new_refresh_token = RefreshToken.objects.create(
            user=old_refresh_token.user
        )
        
        # Generate new access token
        access_token = generate_access_token(old_refresh_token.user.id)
        
        return Response({
            'access_token': access_token,
            'refresh_token': str(new_refresh_token.token)
        }, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = []  
    serializer_class = LogoutSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get and invalidate refresh token
        refresh_token = serializer.validated_data['token']
        refresh_token.invalidate()
        
        return Response(
            {'success': 'User logged out.'}, 
            status=status.HTTP_200_OK
        )

class UserProfileView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    @extend_schema(
        responses={200: UserSerializer},
        description='Get personal user information'
    )
    def get(self, request):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data)

    @extend_schema(
        request=UserSerializer,
        responses={200: UserSerializer},
        description='Update personal user information'
    )
    def put(self, request):
        serializer = self.serializer_class(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            return Response(self.serializer_class(user).data)