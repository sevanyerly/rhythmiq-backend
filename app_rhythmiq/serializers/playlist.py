from rest_framework import serializers
from ..models import Playlist, Song
from .user_profile import UserProfileSerializer


class PlaylistSerializer(serializers.ModelSerializer):
    creator_user = UserProfileSerializer(read_only=True)
    songs = serializers.PrimaryKeyRelatedField(
        queryset=Song.objects.all(), many=True, required=False
    )

    class Meta:
        model = Playlist
        fields = [
            "id",
            "name",
            "creator_user",
            "cover_image_path",
            "songs",
            "private",
        ]
