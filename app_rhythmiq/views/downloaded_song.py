from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from ..models import DownloadedSong, Song

from ..serializers import DownloadedSongSerializer, SongReadSerializer

from django.utils.timezone import now
from django.utils.dateparse import parse_datetime


class DownloadedSongViewSet(viewsets.ModelViewSet):
    queryset = DownloadedSong.objects.all()
    serializer_class = DownloadedSongSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data["user"] = request.user.id
        song_id = data.get("song")

        try:
            song = Song.objects.get(id=song_id)
            existing_download = DownloadedSong.objects.filter(
                user=request.user.userprofile, song=song
            ).first()

            if existing_download:
                existing_download.last_downloaded_at = now()
                existing_download.save()
                return Response({"message": "Last downloaded date updated"}, status=200)

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=201)

        except Song.DoesNotExist:
            return Response({"error": "Song not found"}, status=404)
        except ValidationError as ve:
            return Response({"error": str(ve)}, status=400)
        except Exception as e:
            return Response({"error": "An unexpected error occurred."}, status=500)


class UserDownloadedSongsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Get the current user's downloaded songs
        user_profile = request.user.userprofile

        # Optionally filter by date range
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        # Build the query
        downloads = DownloadedSong.objects.filter(user=user_profile)

        if start_date:
            start_date = parse_datetime(start_date)
            downloads = downloads.filter(last_downloaded_at__gte=start_date)

        if end_date:
            end_date = parse_datetime(end_date)
            downloads = downloads.filter(last_downloaded_at__lte=end_date)

        # Serialize the results
        downloaded_songs = downloads.select_related("song")

        # Return the songs with their details and download date
        response_data = [
            {
                **SongReadSerializer(download.song).data,
                "last_downloaded_at": download.last_downloaded_at,
            }
            for download in downloaded_songs
        ]

        return Response(response_data, status=200)
