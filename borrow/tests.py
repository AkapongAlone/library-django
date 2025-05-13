from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase


from borrow.models import Borrow
from catalog.models import Book

class BorrowAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.user2 = User.objects.create_user(
            username='testuser2',
            password='testpass123'
        )

        self.active_book = Book.objects.create(
            title='Available Book',
            description='This book is available for borrowing',
            genre=Book.Genre.SCIENCE_FICTION,
            is_active=True
        )

        self.inactive_book = Book.objects.create(
            title='Unavailable Book',
            description='This book is not available for borrowing',
            genre=Book.Genre.DRAMA,
            is_active=False
        )

        self.existing_borrow = Borrow.objects.create(
            user=self.user2,
            book=self.inactive_book,
            status=Borrow.Status.BORROWED,
            expired_at=timezone.now() + timedelta(days=7)
        )

        past_date = timezone.now() - timedelta(days=1)
        self.overdue_borrow = Borrow.objects.create(
            user=self.user2,
            book=Book.objects.create(
                title='Overdue Book',
                description='This book is overdue',
                genre=Book.Genre.HORROR,
                is_active=False
            ),
            status=Borrow.Status.BORROWED,
            expired_at=past_date
        )

        self.client.force_authenticate(user=self.user)

    def test_list_borrow(self):
        url = reverse('borrows-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should return both existing borrows

        # Verify overdue status is updated
        self.overdue_borrow.refresh_from_db()
        self.assertEqual(self.overdue_borrow.status, Borrow.Status.OVERDUE)

    def test_filter_borrows(self):
        # Filter by status
        url = reverse('borrows-list')
        response = self.client.get(url, {'status': Borrow.Status.BORROWED})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only one borrow with BORROWED status after overdue update

        # Filter by book
        response = self.client.get(url, {'book': self.inactive_book.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Filter by user
        response = self.client.get(url, {'user': self.user2.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Both borrows belong to user2

    def test_create_borrow_active_book(self):
        initial_count = Borrow.objects.count()

        self.active_book.refresh_from_db()
        self.assertTrue(self.active_book.is_active, "Book should be active before borrowing")

        url = reverse('borrows-list')
        data = {
            'book': str(self.active_book.id),
            'status': Borrow.Status.BORROWED,
            'user': self.user.id
        }

        response = self.client.post(url, data, format='json')

        if response.status_code != status.HTTP_201_CREATED:
            print(f"Error creating borrow: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED,
                         f"Failed to create borrow: {response.data if hasattr(response, 'data') else 'No data'}")

        self.assertEqual(Borrow.objects.count(), initial_count + 1,
                         "A new borrow record should be created")

        self.active_book.refresh_from_db()
        self.assertFalse(self.active_book.is_active,
                         "Book should be inactive after borrowing")

        new_borrow = Borrow.objects.get(book=self.active_book, user=self.user)

        self.assertEqual(new_borrow.status, Borrow.Status.BORROWED,
                         "Borrow status should be BORROWED")

        expire_delta = new_borrow.expired_at - timezone.now()
        self.assertGreaterEqual(expire_delta.days, 6,
                                "Expiry date should be at least 6 days from now")
        self.assertLessEqual(expire_delta.days, 7,
                             "Expiry date should be at most 7 days from now")

    def test_create_borrow_inactive_book(self):
        url = reverse('borrows-list')
        data = {
            'book': str(self.inactive_book.id),
            'status': Borrow.Status.BORROWED,
            'user': self.user.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('book', response.data)

        self.assertEqual(Borrow.objects.count(), 2)

    def test_return_book(self):
        test_borrow = Borrow.objects.create(
            user=self.user,
            book=Book.objects.create(
                title='Return Test Book',
                description='For testing return',
                genre=Book.Genre.COMEDY,
                is_active=False
            ),
            status=Borrow.Status.BORROWED,
            expired_at=timezone.now() + timedelta(days=7)
        )

        url = reverse('borrows-return-book', args=[test_borrow.id])
        response = self.client.put(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify borrow status is updated
        test_borrow.refresh_from_db()
        self.assertEqual(test_borrow.status, Borrow.Status.RETURNED)
        self.assertIsNotNone(test_borrow.returned_at)

        # Verify book is active again
        self.assertTrue(test_borrow.book.is_active)

    def test_get_borrow_detail(self):
        """Test retrieving a single borrow"""
        url = reverse('borrows-detail', args=[self.existing_borrow.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.existing_borrow.id)
        self.assertEqual(response.data['status'], self.existing_borrow.status)