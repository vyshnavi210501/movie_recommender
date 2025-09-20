from rest_framework import serializers
from .models import Movie
from rest_framework import serializers
from .models import Movie, Rating

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ["id", "title", "genres","release_date"]   # keep it simple for now


# 1. Simple ModelSerializer
class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ["id", "movie", "rating"]   # user comes from request, not from input

    def create(self, validated_data):
        # attach logged-in user automatically
        request = self.context.get("request")
        validated_data["user"] = request.user
        return super().create(validated_data)


# 2. Nested Serializer (Rating + Movie info)
class RatingDetailSerializer(serializers.ModelSerializer):
    movie = serializers.StringRelatedField()   # or use MovieSerializer for full info

    class Meta:
        model = Rating
        fields = ["id", "movie", "rating"]


# 3. Plain Serializer Example (custom validation)
class CustomRatingSerializer(serializers.Serializer):
    movie_id = serializers.IntegerField()
    rating = serializers.FloatField()

    def validate_rating(self, value):
        if value < 0 or value > 5:
            raise serializers.ValidationError("Rating must be between 0 and 5")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        movie = Movie.objects.get(id=validated_data["movie_id"])
        return Rating.objects.create(
            user=request.user, movie=movie, rating=validated_data["rating"]
        )
