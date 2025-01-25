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

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all()
    permission_classes = [
        IsAuthenticatedOrReadOnly,
    ]
    http_method_names = ["get", "post"]

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAuthenticatedOrReadOnly(), IsArtist(), IsSongArtist()]
        if self.action in ["create"]:
            return [IsAuthenticatedOrReadOnly(), IsArtist()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
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

    @swagger_auto_schema(
        operation_description="Increment the view count of a song.",
        responses={
            200: openapi.Response(description="View successfully recorded."),
            400: openapi.Response(description="Invalid song or view already recorded."),
        },
    )
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def increment_view(self, request, pk=None):
        user = request.user
        song = self.get_object()

        cache_key = f"{user.id}_view_{song.id}"

        # Check if the view has already been registered for this user and song
        if cache.get(cache_key):
            return Response(
                {"message": "View already successfully registered."}, status=200
            )
        song.streaming_numbers += 1
        song.save()

        # Store the view in cache for 30 seconds to prevent duplicate views
        cache.set(cache_key, "viewed", timeout=30)

        return Response({"message": "View successfully recorded."}, status=200)

    @swagger_auto_schema(
        operation_description="Filter songs by views, date, or genre.",
        manual_parameters=[
            openapi.Parameter(
                "filter_by",
                openapi.IN_QUERY,
                description="Filter criteria: 'views', 'date_views', or 'genre'",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "genres",
                openapi.IN_QUERY,
                description="Comma-separated genre names (required if filter_by is 'genre')",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: SongReadSerializer(many=True),
            400: openapi.Response(
                description="Bad request due to missing or invalid parameters."
            ),
        },
    )
    @action(detail=False, methods=["get"])
    def filter_songs(self, request):
        filter_by = request.query_params.get("filter_by")
        if not filter_by:
            return Response({"error": "filter_by parameter is required."}, status=400)

        # Filter by views, getting the top 10 songs based on streaming numbers
        if filter_by == "views":
            songs = Song.objects.order_by("-streaming_numbers")[:10]

        # Filter by date of creation and views, getting the top 10 songs
        elif filter_by == "date_views":
            songs = Song.objects.order_by("-created_at", "-streaming_numbers")[:10]

        # Filter by genre, with validation for genre names
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

    @swagger_auto_schema(
        operation_description="Search for songs by title, description, or tags with relevance scoring.",
        manual_parameters=[
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Search term",
                type=openapi.TYPE_STRING,
            )
        ],
        responses={200: SongReadSerializer(many=True), 400: "Bad Request"},
    )
    @action(detail=False, methods=["get"])
    def search_songs(self, request):
        search_term = request.query_params.get("search")
        if not search_term:
            return Response(
                {"error": "The 'search' parameter is required."}, status=400
            )

        # Split the search term
        search_terms = search_term.split()

        query = Q()
        for term in search_terms:
            query |= (
                Q(name__icontains=term)
                | Q(description__icontains=term)
                | Q(genres__name__icontains=term)
            )

        # limit to 10 results
        songs = Song.objects.filter(query).distinct()[:10]

        # Add relevance score
        for song in songs:
            relevance_score = 0

            # For each search term, check how many matches exist
            for term in search_terms:
                if term.lower() in song.name.lower():
                    relevance_score += 2
                if term.lower() in song.description.lower():
                    relevance_score += 1
                if any(
                    term.lower() in genre.name.lower() for genre in song.genres.all()
                ):
                    relevance_score += 1

            song.relevance_score = relevance_score

        songs = sorted(songs, key=lambda x: x.relevance_score, reverse=True)

        serializer = SongReadSerializer(songs, many=True, context={"request": request})
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Retrieve the songs liked by the authenticated user.",
        responses={
            200: SongReadSerializer(many=True),
            401: openapi.Response(description="Unauthorized"),
        },
    )
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def liked_songs(self, request):
        user = request.user.userprofile

        liked_songs = Like.objects.filter(user=user).values_list("song", flat=True)

        songs = Song.objects.filter(id__in=liked_songs)

        serializer = SongReadSerializer(songs, many=True, context={"request": request})
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Retrieve the songs downloaded by the authenticated user.",
        responses={
            200: SongReadSerializer(many=True),
            401: openapi.Response(description="Unauthorized"),
            404: openapi.Response(description="No downloaded songs found"),
        },
    )
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

    @swagger_auto_schema(
        operation_description="Filter songs by a specific artist. The artist is identified by the artist_id parameter.",
        manual_parameters=[
            openapi.Parameter(
                "artist_id",
                openapi.IN_QUERY,
                description="The ID of the artist to filter songs by",
                type=openapi.TYPE_INTEGER,
            )
        ],
        responses={
            200: SongReadSerializer(many=True),
            400: openapi.Response(
                description="Bad Request. Missing or invalid artist_id."
            ),
            404: openapi.Response(description="Artist not found or invalid artist ID."),
        },
    )
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

        # Retrieve songs associated with the artist, ordered by creation date
        songs = Song.objects.filter(artists=artist).order_by("-created_at")

        serializer = SongReadSerializer(songs, many=True, context={"request": request})
        return Response(serializer.data)
