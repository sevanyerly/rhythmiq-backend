from django.db import models
from .user_profile import UserProfile

from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
import os


def song_file_path(instance, filename):
    return f"songs/{filename}"


def cover_image_path(instance, filename):
    return f"songs/covers/{filename}"


class Song(models.Model):
    name = models.CharField(max_length=255)
    cover_image_path = models.ImageField(
        upload_to=cover_image_path, blank=True, null=True
    )
    description = models.TextField(blank=True)
    mp3_path = models.FileField(upload_to=song_file_path)
    created_at = models.DateTimeField(auto_now_add=True)
    duration = models.TimeField()
    streaming_numbers = models.IntegerField(default=0)
    artists = models.ManyToManyField(UserProfile, related_name="songs")

    def __str__(self):
        return self.name


    def delete_files(self):
        if self.cover_image_path:
            if os.path.isfile(self.cover_image_path.path):
                os.remove(self.cover_image_path.path)
        if self.mp3_path:
            if os.path.isfile(self.mp3_path.path):
                os.remove(self.mp3_path.path)


@receiver(post_delete, sender=Song)
def delete_song_files(sender, instance, **kwargs):
    instance.delete_files()
