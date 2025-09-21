from django.urls import path
from .views import MovieListView,MovieDetailView,RatingListCreateView, RatingCustomCreateView,RecommendationView

urlpatterns = [
    path("movies/", MovieListView.as_view(), name="movie-list"),
    path("movies/<int:pk>/", MovieDetailView.as_view(), name="movie-detail"),
    path("ratings/", RatingListCreateView.as_view(), name="rating-list-create"),
    path("ratings/add-custom/", RatingCustomCreateView.as_view(), name="rating-add-custom"),
    path('recommendations/', RecommendationView.as_view(), name='recommendations'),
]
