from django.shortcuts import render
from knox.views import LoginView as KnoxLoginView
from knox.views import LogoutView

from django.contrib.auth import authenticate, login
from rest_framework import permissions, status, viewsets, serializers
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from ..serializers import UserProfileSerializer, UserSerializer
from ..models import UserProfile

from django.contrib.auth import get_user_model

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

User = get_user_model()


@swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "email": openapi.Schema(type=openapi.TYPE_STRING),
            "password": openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=["email", "password"],
    ),
    responses={
        200: openapi.Response(
            description="Successful login",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "token": openapi.Schema(type=openapi.TYPE_STRING),
                    "user_profile": UserProfileSerializer,
                },
            ),
        ),
        400: openapi.Response(
            description="Bad request",
        ),
        401: openapi.Response(
            description="Unauthorized",
        ),
    },
)
class LoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        # Validate the request data with the serializer
        email = request.data.get("email")
        password = request.data.get("password")
        if not email or not password:
            return Response(
                {"error": "Please provide both email and password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Authenticate the user
        user = authenticate(username=email, password=password)
        if not user:
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Check if the user has a profile
        try:
            user_profile = user.userprofile
        except UserProfile.DoesNotExist:
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        login(request, user)

        profile_serializer = UserProfileSerializer(user_profile)

        # Generate the Knox token
        token_response = super(LoginView, self).post(request, format=None).data

        return Response(
            {"token": token_response["token"], "user_profile": profile_serializer.data},
            status=status.HTTP_200_OK,
        )


@swagger_auto_schema(
    operation_description="Log out the user and invalidate the session.",
    responses={
        200: openapi.Response(
            description="Logout successful",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "message": openapi.Schema(type=openapi.TYPE_STRING),
                },
            ),
        ),
        401: openapi.Response(
            description="Unauthorized, user must be authenticated.",
        ),
    },
)
class LogoutView(LogoutView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        response = super(LogoutView, self).post(request, format=None)
        return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)


class SignUpViewSet(ViewSet):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "account_type": openapi.Schema(type=openapi.TYPE_INTEGER),
                "private": openapi.Schema(type=openapi.TYPE_BOOLEAN, default=False),
                "showed_name": openapi.Schema(type=openapi.TYPE_STRING),
                "email": openapi.Schema(type=openapi.TYPE_STRING),
                "password": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=["account_type", "showed_name", "email", "password"],
        ),
        responses={
            201: openapi.Response(
                description="User created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
            400: "Bad Request",
            409: "Conflict - Email already exists",
        },
    )
    def create(self, request):
        account_type = request.data.get("account_type")
        private = request.data.get("private", False)

        showed_name = request.data.get("showed_name")
        email = request.data.get("email")
        password = request.data.get("password")

        if not showed_name or showed_name.strip() == "":
            return Response(
                {"error": "Showed name is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if account_type not in [
            1,
            2,
        ]:
            return Response(
                {"error": "Invalid account type."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "User with this email already exists."},
                status=status.HTTP_409_CONFLICT,
            )
        user_serializer = UserSerializer(data={"username": email, "email": email})
        if user_serializer.is_valid():
            user = user_serializer.save()
            user.set_password(password)
            user.save()
            profile_data = {
                "showed_name": showed_name,
                "private": (True if private else False),
                "account_type": (account_type),
            }
            profile_serializer = UserProfileSerializer(data=profile_data)
            if profile_serializer.is_valid():
                UserProfile.objects.create(
                    user=user, **profile_serializer.validated_data
                )
                return Response(
                    {"message": "User created successfully!"},
                    status=status.HTTP_201_CREATED,
                )
            else:
                user.delete()
                return Response(
                    profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(responses={200: UserProfileSerializer, 401: "Unauthorized"})
    def get(self, request):
        user_profile = request.user.userprofile
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data)
