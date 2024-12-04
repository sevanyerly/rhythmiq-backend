from rest_framework.permissions import BasePermission


class IsArtist(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        user_profile = request.user.userprofile
        return user_profile.account_type == 2


class IsSongArtist(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        user_profile = request.user.userprofile
        return str(user_profile.id) in [str(artist.id) for artist in obj.artists.all()]
