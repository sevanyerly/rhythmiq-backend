from rest_framework import viewsets
from ..serializers import ArtistSerializer
from ..models import UserProfile


class ArtistViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserProfile.objects.filter(account_type=2)
    serializer_class = ArtistSerializer
