from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ..models import Song, Genre, UserProfile, Like
from .user_profile import ArtistSerializer
from .genre import GenreSerializer

import audioread
import tempfile


class SongReadSerializer(serializers.ModelSerializer):
    artists = ArtistSerializer(many=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Song
        fields = [
            "id",
            "name",
            "cover_image_path",
            "description",
            "song_path",
            "created_at",
            "duration",
            "streaming_numbers",
            "artists",
            "genres",
            "is_liked",
        ]
        read_only_fields = ["created_at", "streaming_numbers"]

    def get_is_liked(self, obj):
        user = self.context.get("request").user
        if user.is_authenticated:
            # Check if the user liked this song
            return Like.objects.filter(user=user.userprofile, song=obj).exists()
        return False

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        artists = representation.get("artists")
        if artists is None:
            artists = []  # Default to an empty list if artists is None
        filtered_artists = [
            artist for artist in artists if artist and artist.get("account_type") == 2
        ]
        representation["artists"] = filtered_artists
        genres = instance.genres.all()
        representation["genres"] = [genre.name for genre in genres]
        return representation


class SongCreateSerializer(serializers.ModelSerializer):
    artists = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.all(), many=True
    )
    genres = serializers.PrimaryKeyRelatedField(queryset=Genre.objects.all(), many=True)

    class Meta:
        model = Song
        fields = [
            "id",
            "name",
            "cover_image_path",
            "description",
            "song_path",
            "duration",
            "artists",
            "genres",
        ]
        extra_kwargs = {
            "duration": {"read_only": True},
        }

    def validate(self, attrs):
        song_file = attrs.get("song_path")
        if not song_file:
            raise ValidationError({"error": "No song file provided."})

        # Extract duration
        duration = self.extract_audio_duration(song_file)
        if duration is None:
            raise ValidationError(
                {
                    "error": "Unable to extract duration. Ensure it's a valid MP3 or WAV file."
                }
            )

        attrs["duration"] = duration
        return attrs

    def validate_artists(self, artists):
        invalid_artists = [artist for artist in artists if artist.account_type != 2]
        if invalid_artists:
            invalid_usernames = ", ".join(
                [artist.user.username for artist in invalid_artists]
            )
            raise ValidationError(
                f"The following users are not artists: {invalid_usernames}"
            )
        return artists

    def extract_audio_duration(self, file):
        try:
            # Create a temporary file to store the uploaded file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                for chunk in file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name

            with audioread.audio_open(temp_file_path) as audio_file:
                duration_in_seconds = audio_file.duration
                if duration_in_seconds > 3599:
                    raise ValueError(
                        "Audio duration exceeds the 59 minute 59 second limit."
                    )

                return duration_in_seconds

        except Exception as e:
            return None
