from rest_framework import serializers
from ..models import DownloadedSong


class DownloadedSongSerializer(serializers.ModelSerializer):
    class Meta:
        model = DownloadedSong
        fields = "__all__"
