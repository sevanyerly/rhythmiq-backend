from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ..models import Song, Genre, UserProfile
from .user_profile import ArtistSerializer
from .genre import GenreSerializer

from datetime import time
import audioread
import tempfile


class SongReadSerializer(serializers.ModelSerializer):
    artists = ArtistSerializer(many=True)

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

    def extract_audio_duration(self, file):
        try:
            # Create a temporary file to store the uploaded file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                for chunk in file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name

            with audioread.audio_open(temp_file_path) as audio_file:
                duration_in_seconds = audio_file.duration

                hours, remainder = divmod(duration_in_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)

                return time(int(hours), int(minutes), int(seconds))

        except Exception as e:
            print(f"Error extracting audio duration: {e}")
            return None
