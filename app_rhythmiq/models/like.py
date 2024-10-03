from django.db import models
from .user_profile import UserProfile
from .song import Song

class Like(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'song'),)

    def __str__(self):
        return f"{self.user.user.username} liked {self.song.name}"
