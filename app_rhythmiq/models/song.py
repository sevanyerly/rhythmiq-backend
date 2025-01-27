from django.db import models
from .user_profile import UserProfile

from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
import os
import uuid


def song_file_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f"songs/{filename}"


def cover_image_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f"songs/covers/{filename}"


class Song(models.Model):
    name = models.CharField(max_length=100)
    cover_image_path = models.ImageField(
        upload_to=cover_image_path, blank=True, null=True
    )
    description = models.TextField(blank=True)
    song_path = models.FileField(upload_to=song_file_path)
    created_at = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField()
    streaming_numbers = models.IntegerField(default=0)
    artists = models.ManyToManyField(UserProfile, related_name="songs")
    genres = models.ManyToManyField("Genre", related_name="songs", blank=True)

    def __str__(self):
        return self.name

    def delete_files(self):
        if self.cover_image_path:
            if os.path.isfile(self.cover_image_path.path):
                os.remove(self.cover_image_path.path)
        if self.song_path:
            if os.path.isfile(self.song_path.path):
                os.remove(self.song_path.path)


@receiver(post_delete, sender=Song)
def delete_song_files(sender, instance, **kwargs):
    instance.delete_files()
