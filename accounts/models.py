from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifier
    for authentication instead of usernames.
    """
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, name, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model supporting email authentication, name, and password.
    """
    username = None
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.name} ({self.email})"
