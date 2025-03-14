import os
import uuid
import logging
from django.db import models
from django.conf import settings
from django.db.models.signals import post_delete
from django.dispatch import receiver


logger = logging.getLogger(__name__)

DEFAULT_PROFILE_PICTURE = "profiles/default_profile_picture.png"


def profile_picture_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f"profiles/{filename}"


class UserProfile(models.Model):
    ACCOUNT_TYPES = [
        (0, "Admin"),
        (1, "User"),
        (2, "Artist"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True
    )
    showed_name = models.CharField(max_length=30, blank=True)
    profile_picture_path = models.ImageField(
        upload_to=profile_picture_path,
        blank=True,
        null=True,
        default=DEFAULT_PROFILE_PICTURE,
    )
    private = models.BooleanField(default=False)
    account_type = models.IntegerField(choices=ACCOUNT_TYPES, default=0)

    following_artists = models.ManyToManyField(
        "self", related_name="followers", symmetrical=False, blank=True
    )

    def __str__(self):
        return self.user.username

    def delete_files(self):
        if (
            self.profile_picture_path
            and self.profile_picture_path.name != DEFAULT_PROFILE_PICTURE
        ):
            if os.path.isfile(self.profile_picture_path.path):
                try:
                    os.remove(self.profile_picture_path)
                    logger.info(
                        f"Profile picture deleted : {self.profile_picture_path}"
                    )
                except Exception as e:
                    logger.error(
                        f"Error when deleting : {self.profile_picture_path} : {e}"
                    )


@receiver(post_delete, sender=UserProfile)
def delete_user_profile_files(sender, instance, **kwargs):
    instance.delete_files()
