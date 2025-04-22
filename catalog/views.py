from django.shortcuts import render
from .models import Book

def item_list(request):
    items = Book.objects.all()
    return render(request, 'myapp/item_list.html', {'items': items})
