from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import UserRegistrationSerializer
from .serializers import LoginSerializer
from .models import RefreshToken
from .utils import generate_access_token

class UserRegistrationView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer


class LoginView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        # Generate refresh token
        refresh_token = RefreshToken.objects.create(user=user)

        # Generate access token
        access_token = generate_access_token(user.id)

        return Response({
            'access_token': access_token,
            'refresh_token': str(refresh_token.token)
        }, status=status.HTTP_200_OK)