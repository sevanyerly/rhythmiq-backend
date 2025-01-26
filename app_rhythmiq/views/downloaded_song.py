from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..models import DownloadedSong, Song

from ..serializers import DownloadedSongSerializer, SongReadSerializer

from django.utils.timezone import now
from django.utils.dateparse import parse_datetime


class DownloadedSongViewSet(viewsets.ModelViewSet):
    queryset = DownloadedSong.objects.all()
    serializer_class = DownloadedSongSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["post"]

    @swagger_auto_schema(
        request_body=DownloadedSongSerializer,
        responses={
            201: openapi.Response(
                description="Downloaded song created", schema=DownloadedSongSerializer
            ),
            200: openapi.Response(
                description="Last download date updated",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
            400: openapi.Response(
                description="Bad request error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
            404: openapi.Response(
                description="Song not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={"error": openapi.Schema(type=openapi.TYPE_STRING)},
                ),
            ),
        },
    )
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data["user"] = request.user.id
        song_id = data.get("song")

        # Try to fetch the song and handle any errors gracefully
        song = None
        try:
            song = Song.objects.get(id=song_id)
        except Song.DoesNotExist:
            return Response({"error": "Song not found"}, status=404)

        # Check if the song has already been downloaded
        existing_download = DownloadedSong.objects.filter(
            user=request.user.userprofile, song=song
        ).first()

        if existing_download:
            # Update the last downloaded date
            existing_download.last_downloaded_at = now()
            existing_download.save()
            return Response({"message": "Last downloaded date updated"}, status=200)

        # If it's a new download, create a new DownloadedSong
        serializer = self.get_serializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=201)
        except ValidationError as ve:
            return Response({"error": str(ve)}, status=400)
