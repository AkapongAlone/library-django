from django.db import models

class Rent(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
