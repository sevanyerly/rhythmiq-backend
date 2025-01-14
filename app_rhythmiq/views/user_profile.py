from rest_framework import viewsets
from ..serializers import ArtistSerializer, UserProfileSerializer
from ..models import UserProfile
from .permissions import IsProfileOwnerOrPublic, IsProfileOwner

from rest_framework.permissions import BasePermission
from rest_framework.permissions import IsAuthenticated
from ..models import UserProfile
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsProfileOwnerOrPublic]

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsProfileOwner()]
        return super().get_permissions()

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    @action(
        detail=False,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="toggle-follow/(?P<artist_id>\d+)",
    )
    def toggle_follow(self, request, artist_id=None):
        user_profile = request.user.userprofile

        try:
            artist = UserProfile.objects.get(user__id=artist_id, account_type=2)

            if artist.user.id == user_profile.user.id:
                return Response(
                    {"error": "You cannot follow yourself."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if artist in user_profile.following_artists.all():
                user_profile.following_artists.remove(artist)
                message = f"Successfully unfollowed {artist.showed_name}."
            else:
                user_profile.following_artists.add(artist)
                message = f"Successfully followed {artist.showed_name}!"

            return Response({"message": message}, status=status.HTTP_200_OK)

        except UserProfile.DoesNotExist:
            return Response(
                {"error": "Artist not found."}, status=status.HTTP_404_NOT_FOUND
            )


class ArtistViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserProfile.objects.filter(account_type=2)
    serializer_class = ArtistSerializer
