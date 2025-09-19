from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from .models import Movie
from .serializers import MovieSerializer

class MovieListView(generics.ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["genres", "release_date"]  # filter by fields
    ordering_fields = ["title", "release_date"]  # sort by fields
    search_fields = ["title"]  # allow search by title
