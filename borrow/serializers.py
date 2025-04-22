from rest_framework import serializers
from .models import Borrow

class BorrowWriteSerializer(serializers.ModelSerializer):
    class Meta :
        model = Borrow
        exclude = ['expired_at','returned_at']

class BorrowReadSerializer(serializers.ModelSerializer):
    class Meta :
        model = Borrow
        fields = '__all__'