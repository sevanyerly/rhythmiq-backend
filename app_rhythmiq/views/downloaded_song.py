# views/downloaded_song_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ..models import DownloadedSong
from ..serializers import DownloadedSongSerializer


class DownloadedSongList(APIView):
    def get(self, request):
        downloads = DownloadedSong.objects.all()
        serializer = DownloadedSongSerializer(downloads, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = DownloadedSongSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DownloadedSongDetail(APIView):
    def get(self, request, pk):
        try:
            download = DownloadedSong.objects.get(pk=pk)
            serializer = DownloadedSongSerializer(download)
            return Response(serializer.data)
        except DownloadedSong.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            download = DownloadedSong.objects.get(pk=pk)
            serializer = DownloadedSongSerializer(download, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except DownloadedSong.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            download = DownloadedSong.objects.get(pk=pk)
            download.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except DownloadedSong.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
