from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Extra details for each user
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_genres = models.CharField(max_length=255, blank=True)  # Example: "Action,Drama"

    def __str__(self):
        return self.user.username


# Movies table
class Movie(models.Model):
    title = models.CharField(max_length=255)
    genres = models.CharField(max_length=255, blank=True)  # Example: "Comedy|Romance"
    release_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title


# Ratings given by users
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.FloatField()  # 0.5 to 5.0
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} → {self.movie.title} ({self.rating})"


# Watch history (what user watched)
class WatchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    watched_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} watched {self.movie.title}"
