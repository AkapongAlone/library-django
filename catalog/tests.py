from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User

from catalog.models import Book
from rest_framework.test import APITestCase

class BookAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.book = Book.objects.create(
            title='API Test Book',
            description='Testing API',
            genre=Book.Genre.DRAMA
        )
        self.client.force_authenticate(user=self.user)

    def test_get_books_list(self):
        url = reverse('books-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_book_detail(self):
        url = reverse('books-detail', args=[str(self.book.id)])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'API Test Book')

    def test_create_book(self):
        url = reverse('books-list')
        data = {
            'title': 'New Book',
            'description': 'New Description',
            'genre': Book.Genre.COMEDY
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)

    def test_update_book(self):
        url = reverse('books-detail',args=[str(self.book.id)])
        data = {
            'title': 'TestUpdate',
            'description': 'TestUpdate',
            'genre': Book.Genre.COMEDY
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_book = Book.objects.get(id=self.book.id)
        self.assertEqual(updated_book.title, 'TestUpdate')
        self.assertEqual(updated_book.description, 'TestUpdate')
        self.assertEqual(updated_book.genre, Book.Genre.COMEDY)

    def test_delete_book(self):
        url = reverse('books-detail', args=[str(self.book.id)])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 0)