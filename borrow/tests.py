from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase, APIClient


from borrow.models import Borrow
from catalog.models import Book


class BorrowModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user = User.objects.create_user(username='testuser', password='12345')
        test_book = Book.objects.create(
            title='Test Book',
            description='This is a test book',
            genre=Book.Genre.SCIENCE_FICTION
        )

        Borrow.objects.create(
            user=test_user,
            book=test_book,
            expired_at=timezone.now() + timedelta(days=7),
            status=Borrow.Status.BORROWED
        )

    def test_borrow_creation(self):
        borrow = Borrow.objects.get(book__title = 'Test Book')
        self.assertEqual(borrow.status, Borrow.Status.BORROWED)
        self.assertIsNotNone(borrow.expired_at)
        self.assertIsNone(borrow.returned_at)


class BorrowAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.book = Book.objects.create(
            title='Test API Book',
            description='This is a test book for API',
            genre=Book.Genre.SCIENCE_FICTION,
            is_active=True
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_borrow(self):
        url = reverse('borrows-list')
        data = {'book': str(self.book.id)}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        book = Book.objects.get(id=self.book.id)
        self.assertFalse(book.is_active)

    def test_return_book(self):
        borrow = Borrow.objects.create(
            user=self.user,
            book=self.book,
            status=Borrow.Status.BORROWED
        )
        self.book.is_active = False
        self.book.save()

        url = reverse('borrows-return-book', args=[borrow.id])
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        borrow.refresh_from_db()
        self.book.refresh_from_db()
        self.assertEqual(borrow.status, Borrow.Status.RETURNED)
        self.assertTrue(self.book.is_active)