from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from .models import Movie
from .serializers import MovieSerializer
from rest_framework import generics
from .models import Movie
from .serializers import MovieSerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import Case, When, Value, IntegerField, Sum
from .permissions import IsAdminOrReadOnly

class MovieListView(generics.ListAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes=[IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["genres", "release_date"]  # filter by fields
    ordering_fields = ["title", "release_date"]  # sort by fields
    search_fields = ["title"]  # allow search by title


class MovieDetailView(generics.RetrieveAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

class AddMoviesView(generics.CreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = [IsAuthenticated,IsAdminOrReadOnly]


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

from rest_framework import generics, permissions
from rest_framework.response import Response
from django.db.models import Q

from .models import Movie, Rating
from .serializers import MovieSerializer


class RecommendationView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MovieSerializer

    def get(self, request, *args, **kwargs):
        # Step 1: Get movies user rated >= 4
        high_rated = Rating.objects.filter(user=request.user, rating__gte=4).select_related("movie")

        if not high_rated.exists():
            return Response({"detail": "No recommendations available. Please rate some movies first."})

        # Step 2: Collect genres of those movies
        liked_genres = set()
        for rating in high_rated:
            liked_genres.update(rating.movie.genres.split("|"))  # assuming genres stored like "Action|Comedy"

        # Step 3: Recommend movies that match any liked genre (excluding already rated)
        recommendations = Movie.objects.filter(
            Q(genres__icontains=list(liked_genres)[0])  # start with first genre
        )

        for genre in liked_genres:
            recommendations = recommendations | Movie.objects.filter(genres__icontains=genre)

        recommendations = recommendations.exclude(
            id__in=high_rated.values_list("movie_id", flat=True)
        ).distinct()[:10]  # limit 10

        serializer = self.get_serializer(recommendations, many=True)
        return Response(serializer.data)

from collections import defaultdict
from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.response import Response

from .models import Movie, Rating
from .serializers import MovieSerializer


class WeightedRecommendationView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MovieSerializer

    def get(self, request, *args, **kwargs):
        # Step 1: Collect user ratings
        user_ratings = Rating.objects.filter(user=request.user).select_related("movie")

        if not user_ratings.exists():
            return Response({"detail": "No recommendations available. Please rate some movies first."})

        # Step 2: Build genre preference weights
        genre_weights = defaultdict(float)
        for rating in user_ratings:
            for genre in rating.movie.genres.split("|"):
                genre_weights[genre] += rating.rating  # add weight based on rating

        if not genre_weights:
            return Response({"detail": "No genre preferences detected."})

        # Step 3: Recommend movies by weighted genres
        recommendations = Movie.objects.exclude(
            id__in=user_ratings.values_list("movie_id", flat=True)
        )
        cases = [
            When(genres__name=genre, then=Value(weight))
            for genre, weight in genre_weights.items() if weight > 0
        ]

        recommended_movies = (
            Movie.objects.annotate(
                score=Sum(Case(*cases, output_field=IntegerField()))
            )
            .filter(score__gt=0)           # only movies with positive preference
            .order_by("-score")            # highest preference first
        )
        # Rank movies by sum of matching genre weights
        movie_scores = []
        for movie in recommendations:
            score = sum(genre_weights.get(genre, 0) for genre in movie.genres.split("|"))
            if score > 0:
                movie_scores.append((score, movie))

        # Sort by score descending
        movie_scores.sort(key=lambda x: x[0], reverse=True)
        top_movies = [m for _, m in movie_scores[:10]]

        serializer = self.get_serializer(top_movies, many=True)
        return Response(serializer.data)
