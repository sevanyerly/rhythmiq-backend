from django.db import models
# from django.contrib.auth.models import User
from django.conf import settings

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    showed_name = models.CharField(max_length=255, blank=True)
    profile_picture_path = models.ImageField(upload_to='profiles/', blank=True, null=True)
    private = models.BooleanField(default=False)
    following_artists = models.ManyToManyField('UserProfile', related_name='following', blank=True)

    def __str__(self):
        return self.user.username
