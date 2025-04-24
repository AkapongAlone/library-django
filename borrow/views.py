from datetime import timedelta

from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from rest_framework import viewsets, serializers
from rest_framework.response import Response

from .models import Borrow
from .serializers import BorrowWriteSerializer,BorrowReadSerializer


class BorrowViewSet(viewsets.ModelViewSet):
    queryset = Borrow.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BorrowWriteSerializer
        return BorrowReadSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'book','user']

    def list(self, request, *args, **kwargs):
        now = timezone.now()

        Borrow.objects.filter(status= Borrow.Status.BORROWED,expired_at__lt = now).update(status = Borrow.Status.OVERDUE)

        return super().list(request,*args,**kwargs)
    def perform_create(self, serializer):
        book = serializer.validated_data['book']

        if not book.is_active:
            raise serializers.ValidationError({"book": "This book is not available for borrowing."})

        serializer.save(
            user=self.request.user,
            expired_at=timezone.now() + timedelta(days=7)
        )

        book.is_active = False
        book.save()

    @action(detail=True, methods=['put'])
    def return_book(self, request, pk=None):
        try:
            borrow = self.get_object()
            borrow.status = Borrow.Status.RETURNED
            borrow.returned_at = timezone.now()
            borrow.save()

            book = borrow.book
            book.is_active = True
            book.save()

            serializer = BorrowReadSerializer(borrow)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=400)