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
        return str(request.user.id) in [str(artist.id) for artist in obj.artists.all()]


class IsProfileOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        print(obj.user)
        print(request.user)
        return obj.user == request.user


class IsProfileOwnerOrPublic(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or not obj.private
