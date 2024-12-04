from django.db import models
from .user_profile import UserProfile
from .song import Song


class DownloadedSong(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    last_downloaded_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "song")

    def __str__(self):
        return f"{self.user.user.username} downloaded {self.song.name}"
