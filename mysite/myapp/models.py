from django.db import models
from django.utils import timezone
import uuid

class Token(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid.uuid4,editable=False)
    number = models.IntegerField()
    name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_served = models.BooleanField(default=False)
    is_skipped = models.BooleanField(default=False)

    def __str__(self):
        return f"Token {self.number}({self.id})"
