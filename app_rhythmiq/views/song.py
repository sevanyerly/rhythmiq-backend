from rest_framework import viewsets
from django.http import FileResponse
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import Song
from ..serializers import SongSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class SongViewSet(viewsets.ModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly
    ]  # Authenticated users can create/edit, others can only read.

    def perform_create(self, serializer):
        serializer.save()  # Add custom logic here if needed.


# class SongViewSet(viewsets.ModelViewSet):
#     queryset = Song.objects.all()
#     serializer_class = SongSerializer

#     @action(detail=True, methods=["get"])
#     def stream(self, request, pk=None):
#         """
#         Stream the MP3 file of the song.
#         """
#         song = self.get_object()
#         if song.mp3_path:
#             try:
#                 return FileResponse(open(song.mp3_path.path, "rb"), content_type="audio/mpeg")
#             except FileNotFoundError:
#                 return Response({"detail": "MP3 file not found."}, status=404)
#         return Response({"detail": "No MP3 file available."}, status=400)

#     @action(detail=True, methods=["get"])
#     def cover(self, request, pk=None):
#         """
#         Access the cover image of the song.
#         """
#         song = self.get_object()
#         if song.cover_image_path:
#             try:
#                 return FileResponse(open(song.cover_image_path.path, "rb"), content_type="image/jpeg")
#             except FileNotFoundError:
#                 return Response({"detail": "Cover image not found."}, status=404)
#         return Response({"detail": "No cover image available."}, status=400)
