from rest_framework import serializers
from ..models import Like
from .user_profile import UserProfileSerializer
from .song import SongSerializer


class LikeSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    song = SongSerializer(read_only=True)

    class Meta:
        model = Like
        fields = "__all__"
