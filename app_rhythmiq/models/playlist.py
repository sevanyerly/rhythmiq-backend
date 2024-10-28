import os
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .user_profile import UserProfile
from .song import Song


def playlist_cover_image_path(instance, filename):
    return f"playlists/{filename}"


class Playlist(models.Model):
    name = models.CharField(max_length=255)
    cover_image_path = models.ImageField(
        upload_to=playlist_cover_image_path, blank=True, null=True
    )
    creator_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    private = models.BooleanField(default=False)
    songs = models.ManyToManyField(Song, related_name="playlists", blank=True)
    followers = models.ManyToManyField(
        UserProfile, related_name="playlists_followed", blank=True
    )

    def __str__(self):
        return self.name

    def delete_files(self):
        """Supprime le fichier image de couverture associé."""
        if self.cover_image_path:
            if os.path.isfile(self.cover_image_path.path):
                os.remove(self.cover_image_path.path)


@receiver(post_delete, sender=Playlist)
def delete_playlist_files(sender, instance, **kwargs):
    """Signal pour supprimer les fichiers de couverture lorsque la Playlist est supprimée."""
    instance.delete_files()
