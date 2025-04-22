from rest_framework import viewsets

from .models import Borrow
from .serializers import BorrowWriteSerializer,BorrowReadSerializer


class BorrowViewSet(viewsets.ModelViewSet):
    queryset = Borrow.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BorrowWriteSerializer
        return BorrowReadSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        from datetime import timedelta
        from django.utils import timezone
        serializer.save(expired_at=timezone.now() + timedelta(days=7))