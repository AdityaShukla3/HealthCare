from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    """
    Register a new user with name, email, and password.
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate tokens upon registration
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "User registered successfully.",
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            },
            status=status.HTTP_201_CREATED
        )


class LoginView(TokenObtainPairView):
    """
    Log in a user and return JWT access and refresh tokens.
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
