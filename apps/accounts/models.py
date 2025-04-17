from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Add extra fields here as needed, for example:
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username
