from rest_framework import serializers
from ..models import Like
from .user_profile import UserProfileSerializer
from .song import SongReadSerializer


class LikeSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    song = SongReadSerializer(read_only=True)

    class Meta:
        model = Like
        fields = "__all__"
