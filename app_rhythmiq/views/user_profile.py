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
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q


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

    @swagger_auto_schema(
        operation_description="Follow or unfollow an artist.",
        manual_parameters=[
            openapi.Parameter("artist_id", openapi.IN_PATH, type=openapi.TYPE_INTEGER)
        ],
        responses={
            200: openapi.Response(description="Followed or unfollowed successfully."),
            400: openapi.Response(
                description="Cannot follow yourself or missing artist_id."
            ),
            404: openapi.Response(description="Artist not found."),
        },
    )
    @action(
        detail=False,
        methods=["post"],
        permission_classes=[IsAuthenticated],
        url_path="toggle-follow/(?P<artist_id>\d+)",
    )
    def toggle_follow(self, request, artist_id=None):
        user_profile = request.user.userprofile

        try:
            # Try to fetch the artist's profile based on the provided artist_id
            artist = UserProfile.objects.get(user__id=artist_id, account_type=2)

            if artist.user.id == user_profile.user.id:
                return Response(
                    {"error": "You cannot follow yourself."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if the user is already following the artist and toggle accordingly
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

    @swagger_auto_schema(
        operation_description="Search for artists by their name.",
        manual_parameters=[
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Search term for artist name",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: ArtistSerializer(many=True),
            400: "Bad Request - 'search' parameter is required",
        },
    )
    @action(detail=False, methods=["get"])
    def search_artists(self, request):
        search_term = request.query_params.get("search")
        if not search_term:
            return Response(
                {"error": "The 'search' parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Search for artists by showed_name matching the search term and account_type=2 (artist)
        artists = UserProfile.objects.filter(
            Q(showed_name__icontains=search_term) & Q(account_type=2)
        ).distinct()

        serializer = self.get_serializer(artists, many=True)
        return Response(serializer.data)
