from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from .models import Movie
from .serializers import MovieSerializer
from rest_framework import generics
from .models import Movie
from .serializers import MovieSerializer
from rest_framework.permissions import IsAuthenticated

class MovieListView(generics.ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["genres", "release_date"]  # filter by fields
    ordering_fields = ["title", "release_date"]  # sort by fields
    search_fields = ["title"]  # allow search by title


class MovieDetailView(generics.RetrieveAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

from rest_framework import generics, permissions
from .models import Rating
from .serializers import RatingSerializer, RatingDetailSerializer, CustomRatingSerializer

class RatingListCreateView(generics.ListCreateAPIView):
    serializer_class = RatingSerializer  # use serializer for create
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Rating.objects.filter(user=self.request.user)


# ✅ Create rating with custom validation (using plain Serializer)
class RatingCustomCreateView(generics.CreateAPIView):
    serializer_class = CustomRatingSerializer
    permission_classes = [permissions.IsAuthenticated]

