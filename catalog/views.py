from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from .models import Book
from .serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['genre', 'title', 'publisher','is_active']