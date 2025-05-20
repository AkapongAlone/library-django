from datetime import timedelta
from telnetlib import STATUS

from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from rest_framework import viewsets, serializers, permissions
from rest_framework.response import Response

from .models import Borrow
from .serializers import BorrowWriteSerializer,BorrowReadSerializer


class BorrowViewSet(viewsets.ModelViewSet):
    queryset = Borrow.objects.all()

    permission_classes = [permissions.IsAuthenticated]
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BorrowWriteSerializer
        return BorrowReadSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'book','user']

    def perform_create(self, serializer):
        book = serializer.validated_data['book']
        user = serializer.validated_data['user']
        print(user)
        if not book.is_active:
            raise serializers.ValidationError({"book": "This book is not available for borrowing."})
        if user.is_borrowing:
            raise serializers.ValidationError({"user": "This user is already borrowing."})
        serializer.save(
            user=user,
            expired_at=timezone.now() + timedelta(days=7)
        )

        user.is_borrowing = True
        user.save()
        book.is_active = False
        book.save()

    @action(detail=True, methods=['put'])
    def return_book(self, request, pk=None):
        try:
            borrow = self.get_object()

            if borrow.status == Borrow.Status.RETURNED:
                return Response(
                    {"error": "This book has already been returned"},
                    status=400
                )

            borrow.status = Borrow.Status.RETURNED
            borrow.returned_at = timezone.now()
            borrow.save()

            book = borrow.book
            book.is_active = True
            book.save()

            user = borrow.user
            user.is_borrowing = False
            user.save()

            serializer = BorrowReadSerializer(borrow)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=400)