from rest_framework import serializers
from ..models import UserProfile


from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]

    def validate_email(self, value):
        # Check if the email already exists
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "user",
            "showed_name",
            "profile_picture_path",
            "private",
            "following_artists",
            "account_type",
        ]
        read_only_fields = ["user"]


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "id",
            "showed_name",
            "profile_picture_path",
            "account_type",
        ]
        read_only_fields = ["user"]

    def to_representation(self, instance):
        if instance.account_type == 2:
            return super().to_representation(instance)
        return None
