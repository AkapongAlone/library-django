from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from catalog.models import Book


class Borrow(models.Model):
    class Status(models.TextChoices):
        BORROWED = 'BRW', 'borrowed'
        RETURNED = 'RTN', 'returned'
        OVERDUE = 'OVD', 'overdue'

    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(null=True,blank=True)

    user = models.ForeignKey(
            User,
            on_delete=models.CASCADE,
            related_name='borrowings',
            verbose_name='ผู้ยืม'
        )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='borrowing_history',
        verbose_name='หนังสือที่ยืม'
    )

    status = models.CharField(
        max_length=3,
        choices=Status.choices,
        default=Status.BORROWED,
        verbose_name='สถานะการยืม'
    )

    returned_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='วันเวลาที่คืน'
    )

    class Meta:
        verbose_name = 'รายการยืม'
        verbose_name_plural = 'รายการยืม'
        ordering = ['-created_at']

    @property
    def property_status(self):
        print(timezone.localtime(timezone.now()))
        if self.status == Borrow.Status.BORROWED and self.expired_at < timezone.now():
            self.status = Borrow.Status.OVERDUE
            self.save()
        return self.status