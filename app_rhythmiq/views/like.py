# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework import viewsets
from ..models import Like
from ..serializers import LikeSerializer


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        song_id = request.data.get("song")
        user = request.user.userprofile

        if not song_id:
            return Response(
                {"detail": "Song is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        if Like.objects.filter(user=user, song_id=song_id).exists():
            return Response(
                {"detail": "This song is already in your favorites."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        like = Like.objects.create(user=user, song_id=song_id)
        serializer = self.get_serializer(like)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        song_id = kwargs.get("pk")
        user = request.user.userprofile

        if not song_id:
            return Response(
                {"detail": "Song ID is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        like = Like.objects.filter(user=user, song_id=song_id).first()
        if not like:
            return Response(
                {"detail": "This song is not in your favorites."},
                status=status.HTTP_404_NOT_FOUND,
            )

        like.delete()
        return Response(
            {"detail": "Song removed from favorites."},
            status=status.HTTP_204_NO_CONTENT,
        )
