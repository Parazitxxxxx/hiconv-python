import uuid

from django.db import models
from model_utils.models import TimeStampedModel


class Invitation(TimeStampedModel):
    user = models.ForeignKey('auth.User', null=True)
    email = models.EmailField(unique=True)
    uid = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        created = not self.pk
        if created:
            self.uid = uuid.uuid4().hex[:20]
        super().save(*args, **kwargs)
