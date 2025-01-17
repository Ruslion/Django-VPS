from django.urls import path
from .views import UserRegistrationView, LoginView, RefreshTokenView, LogoutView, UserProfileView
from rest_framework.permissions import AllowAny


from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [
    path('api/register/', UserRegistrationView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/refresh/', RefreshTokenView.as_view(), name='token-refresh'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/me/', UserProfileView.as_view(), name='user-profile'),
    path('api/schema/', SpectacularAPIView.as_view(permission_classes=[AllowAny], authentication_classes=[]), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema', permission_classes=[AllowAny], authentication_classes=[]), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema', permission_classes=[AllowAny], authentication_classes=[]), name='redoc'),

]