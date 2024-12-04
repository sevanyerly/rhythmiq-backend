from rest_framework import serializers
from ..models import DownloadedSong


class DownloadedSongSerializer(serializers.ModelSerializer):
    class Meta:
        model = DownloadedSong
        fields = ["id", "user", "song", "last_downloaded_at"]
        read_only_fields = ["last_downloaded_at"]
