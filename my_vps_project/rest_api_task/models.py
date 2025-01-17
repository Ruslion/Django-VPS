import uuid
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta

class RefreshToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = datetime.now() + timedelta(days=30)
        super().save(*args, **kwargs)

    def is_valid(self):
        return self.expires_at > datetime.now()