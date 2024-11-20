from rest_framework import serializers
from ..models import Song
from .user_profile import ArtistSerializer

class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = [
            "id",
            "name",
            "cover_image_path",
            "description",
            "mp3_path",
            "created_at",
            "duration",
            "streaming_numbers",
            "artists",
        ]
        read_only_fields = ["created_at", "streaming_numbers"]


class SongSerializer(serializers.ModelSerializer):
    artists = ArtistSerializer(many=True)

    class Meta:
        model = Song
        fields = [
            "id",
            "name",
            "cover_image_path",
            "description",
            "mp3_path",
            "created_at",
            "duration",
            "streaming_numbers",
            "artists",
        ]
        read_only_fields = ["created_at", "streaming_numbers"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        artists = representation.get("artists")
        if artists is None:
            artists = []  # Default to an empty list if artists is None
        filtered_artists = [
            artist for artist in artists if artist and artist.get("account_type") == 2
        ]
        representation["artists"] = filtered_artists
        return representation
