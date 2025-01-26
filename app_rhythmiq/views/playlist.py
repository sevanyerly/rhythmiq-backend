from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..models import Playlist, Song
from ..serializers import PlaylistSerializer, SongReadSerializer
from rest_framework.permissions import IsAuthenticated


class PlaylistViewSet(viewsets.ModelViewSet):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user_profile = self.request.user.userprofile
        serializer.save(creator_user=user_profile)

    @swagger_auto_schema(
        operation_description="Add songs to a playlist",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "song_ids": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_INTEGER),
                )
            },
        ),
        responses={200: "Songs added to playlist", 400: "No valid songs found"},
    )
    @action(detail=True, methods=["post"])
    def add_songs(self, request, pk=None):
        playlist = self.get_object()
        song_ids = request.data.get("song_ids", [])
        songs = Song.objects.filter(id__in=song_ids)

        if songs.exists():
            playlist.songs.add(*songs)
            return Response({"status": "success", "message": "Songs added to playlist"})
        return Response(
            {"status": "error", "message": "No valid songs found"}, status=400
        )

    @swagger_auto_schema(
        operation_description="Get songs in a playlist",
        responses={200: SongReadSerializer(many=True)},
    )
    @action(detail=True, methods=["get"])
    def get_songs(self, request, pk=None):
        playlist = self.get_object()
        songs = playlist.songs.all()

        serializer = SongReadSerializer(songs, many=True)

        return Response({"songs": serializer.data})
