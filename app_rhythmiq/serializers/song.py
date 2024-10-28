from rest_framework import serializers
from ..models import Song


class SongSerializer(serializers.ModelSerializer):
    cover_image_url = serializers.SerializerMethodField()
    mp3_url = serializers.SerializerMethodField()

    class Meta:
        model = Song
        fields = [
            'id',
            'name',
            'description',
            'cover_image_url',
            'mp3_url',
            'created_at',
            'duration',
            'streaming_numbers',
            'artists',
        ]

    def get_cover_image_url(self, obj):
        if obj.cover_image_path:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.cover_image_path.url)
        return None

    def get_mp3_url(self, obj):
        if obj.mp3_path:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.mp3_path.url)
        return None
