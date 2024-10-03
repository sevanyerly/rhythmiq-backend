from django.db import models
from .user_profile import UserProfile

class Song(models.Model):
    name = models.CharField(max_length=255)
    cover_image_path = models.ImageField(upload_to='songs/', blank=True, null=True)
    description = models.TextField(blank=True)
    mp3_path = models.FileField(upload_to='songs/')
    created_at = models.DateTimeField(auto_now_add=True)
    duration = models.TimeField()
    streaming_numbers = models.IntegerField(default=0)
    artists = models.ManyToManyField(UserProfile, related_name='songs')

    def __str__(self):
        return self.name
