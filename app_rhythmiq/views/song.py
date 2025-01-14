from rest_framework import viewsets
from django.http import FileResponse
from django.db.models import Count, Q

from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Song, Like, DownloadedSong, UserProfile
from ..serializers import SongReadSerializer, SongCreateSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .permissions import IsArtist, IsSongArtist
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from django.db import models

import mimetypes
from mutagen import File as MutagenFile
from django.core.cache import cache


class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all()
    permission_classes = [
        IsAuthenticatedOrReadOnly,
    ]

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticatedOrReadOnly(), IsArtist(), IsSongArtist()]
        if self.action in ["create"]:
            return [IsAuthenticatedOrReadOnly(), IsArtist()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            print("create")
            return SongCreateSerializer
        return SongReadSerializer

    def perform_create(self, serializer):
        user_id = self.request.user.id

        song_file = self.request.FILES.get("song_path")
        if not song_file:
            raise ValidationError({"error": "No song was provided, please try again"})

        if not self.is_valid_audio_file(song_file):
            raise ValidationError(
                {"error": "The file is not a valid MP3 or WAV audio file."}
            )
        
        image_file = self.request.FILES.get("cover_image_path")

        if image_file and not self.is_valid_image_file(image_file):
            raise ValidationError(
                {"error": "The file is not a valid JPEG or PNG image."}
            )

        artist_ids = self.request.data.getlist("artists")

        if str(user_id) not in artist_ids:
            artist_ids.append(str(user_id))

        artists = UserProfile.objects.filter(user__id__in=artist_ids)
        for artist in artists:
            if artist.account_type != 2:
                raise ValidationError(
                    f"The user {artist.user.username} is not an artist."
                )

        serializer.save(artists=artists)

    def is_valid_audio_file(self, file):
        """
        Validate if the uploaded file is a valid MP3 or WAV file.
        """
        try:
            mime_type, _ = mimetypes.guess_type(file.name)
            valid_mime_types = ["audio/mpeg", "audio/wav", "audio/x-wav"]

            if mime_type not in valid_mime_types:
                return False

            if mime_type == "audio/mpeg":
                try:
                    audio = MutagenFile(file)
                    if not audio:
                        return False
                except Exception as e:
                    return False

            return True

        except Exception as e:
            print("exeption e")
            return False

    def is_valid_image_file(self, file):
        """
        Validate if the uploaded file is a valid image (e.g., JPEG, PNG).
        """
        try:
            mime_type, _ = mimetypes.guess_type(file.name)
            valid_mime_types = ["image/jpeg", "image/png"]

            if mime_type not in valid_mime_types:
                return False

            return True
        except Exception as e:
            return False



    @action(detail=False, methods=["get"])
    def filter_songs(self, request):
        """
        Filters songs by specified type.
        Query parameters :
        - filter_by: views, date_views, genre
        """
        filter_by = request.query_params.get("filter_by")
        if not filter_by:
            return Response({"error": "filter_by parameter is required."}, status=400)

        if filter_by == "views":
            songs = Song.objects.order_by("-streaming_numbers")[:10]

        elif filter_by == "date_views":
            songs = Song.objects.order_by("-created_at", "-streaming_numbers")[:10]
        elif filter_by == "genre":
            genre_names = request.query_params.get("genres")
            if not genre_names:
                return Response(
                    {
                        "error": "genres parameter is required when filter_by is 'genre'."
                    },
                    status=400,
                )

            genre_list = genre_names.split(",")

            songs = (
                Song.objects.filter(genres__name__in=genre_list)
                .annotate(
                    relevance=Count("genres", filter=Q(genres__name__in=genre_list))
                )
                .order_by("-relevance", "-streaming_numbers")
            )

            songs = songs.distinct()[:10]

        else:
            return Response(
                {"error": f"Invalid filter_by value: {filter_by}."}, status=400
            )

        serializer = self.get_serializer(songs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def liked_songs(self, request):
        user = request.user.userprofile

        liked_songs = Like.objects.filter(user=user).values_list("song", flat=True)

        songs = Song.objects.filter(id__in=liked_songs)

        serializer = SongReadSerializer(songs, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def downloaded_songs(self, request):
        user = request.user.userprofile

        downloaded_songs = (
            DownloadedSong.objects.filter(user=user)
            .order_by("-last_downloaded_at")
            .values_list("song", flat=True)
        )

        # Filter songs by last_downloaded_at date
        songs = Song.objects.filter(id__in=downloaded_songs).order_by(
            models.Case(
                *[
                    models.When(id=id, then=models.Value(index))
                    for index, id in enumerate(downloaded_songs)
                ],
                default=models.Value(len(downloaded_songs)),
                output_field=models.IntegerField(),
            )
        )
        serializer = SongReadSerializer(songs, many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def filter_by_artist(self, request):
        artist_id = request.query_params.get("artist_id")

        if not artist_id:
            return Response({"error": "artist_id parameter is required."}, status=400)

        try:
            artist = UserProfile.objects.get(user__id=artist_id, account_type=2)
        except UserProfile.DoesNotExist:
            return Response(
                {"error": "Artist not found or invalid artist ID."}, status=404
            )

        songs = Song.objects.filter(artists=artist).order_by("-created_at")

        serializer = SongReadSerializer(songs, many=True, context={"request": request})
        return Response(serializer.data)
