from django.db import models
import uuid

# Create your models here.
class Book(models.Model):
    class Genre(models.TextChoices):
        SCIENCE_FICTION = 'SCI', 'Science Fiction'
        DRAMA = 'DRA', 'Drama'
        COMEDY = 'COM', 'Comedy'
        HORROR = 'HOR', 'Horror'
        ACTION = 'ACN', 'Action'

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for this record"
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    genre = models.CharField(
        max_length=3,
        choices=Genre.choices,
        default=Genre.SCIENCE_FICTION
    )
    publisher = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title