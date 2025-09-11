from django.contrib import admin
from .models import UserProfile, Movie, Rating, WatchHistory

admin.site.register(UserProfile)
admin.site.register(Movie)
admin.site.register(Rating)
admin.site.register(WatchHistory)
