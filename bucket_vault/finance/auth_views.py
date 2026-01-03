from django.contrib.auth.models import User
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    """
    Register a new user and return JWT tokens.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email', '')

    if not username or not password:
        return Response(
            {'detail': 'Username and password are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {'detail': 'Username already taken.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Create user (triggers your signal to create default portfolio)
    user = User.objects.create_user(
        username=username,
        password=password,
        email=email
    )

    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)

    return Response({
        'detail': 'User created successfully.',
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def logout(request):
    """
    Blacklist the refresh token (optional, for token rotation).
    """
    try:
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'detail': 'Logged out successfully.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_token(request):
    """
    Verify JWT token and return user info.
    """
    user = request.user
    return Response({
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
    })