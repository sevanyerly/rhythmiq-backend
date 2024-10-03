from django.db import models
from .user_profile import UserProfile
from .song import Song

class Playlist(models.Model):
    name = models.CharField(max_length=255)
    cover_image_path = models.ImageField(upload_to='playlists/', blank=True, null=True)
    creator_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    private = models.BooleanField(default=False)
    songs = models.ManyToManyField(Song, related_name='playlists', blank=True)
    followers = models.ManyToManyField(UserProfile, related_name='playlists_followed', blank=True)

    def __str__(self):
        return self.name
