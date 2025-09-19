import pandas as pd
import logging
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from movies.models import Movie, Rating

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()  # prints to console
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


class Command(BaseCommand):
    help = "Import movies and ratings from CSV files into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--movies",
            type=str,
            required=True,
            help="Path to movies.csv"
        )
        parser.add_argument(
            "--ratings",
            type=str,
            required=True,
            help="Path to ratings.csv"
        )

    def handle(self, *args, **options):
        movies_file = options["movies"]
        ratings_file = options["ratings"]

        try:
            self.import_movies(movies_file)
            self.import_ratings(ratings_file)
        except Exception as e:
            logger.error(f"Import failed: {e}")
            raise CommandError(f"Import failed: {e}")

    def import_movies(self, file_path):
        """Import movies from CSV"""
        logger.info(f"Starting movies import from {file_path}...")
        movies_df = pd.read_csv(file_path)
        for _, row in movies_df.iterrows():
            Movie.objects.update_or_create(
                id=row["movieId"],
                defaults={"title": row["title"], "genres": row["genres"]}
            )
        logger.info(f"✔ Imported {len(movies_df)} movies successfully.")

    def import_ratings(self, file_path):
        """Import ratings and create users if needed"""
        logger.info(f"Starting ratings import from {file_path}...")
        ratings_df = pd.read_csv(file_path)

        chunksize = 100000
        for chunk in pd.read_csv(file_path, chunksize=chunksize):
            for _, row in chunk.iterrows():
                user, _ = User.objects.get_or_create(username=f"user_{row['userId']}")
                try:
                    movie = Movie.objects.get(id=row['movieId'])
                except Movie.DoesNotExist:
                    continue
                Rating.objects.update_or_create(user=user, movie=movie, defaults={"rating": row["rating"]})
