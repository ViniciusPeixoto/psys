from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now


class Account(models.Model):
    """
    This defines a Group of Users that are able to access the Tree Everywhere application
    """

    name = models.CharField(
        max_length=settings.CHAR_FIELD_MAX_LENGTH, unique=True
    )
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['created']


class User(AbstractUser):
    accounts = models.ManyToManyField(Account)

    class Meta:
        ordering = ['username']


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True
    )
    about = models.TextField()
    joined = models.DateTimeField(auto_now_add=True)


class Tree(models.Model):
    name = models.CharField(
        max_length=settings.CHAR_FIELD_MAX_LENGTH, unique=True
    )
    scientific_name = models.CharField(unique=True)


class PlantedTree(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.OneToOneField(Account, on_delete=models.CASCADE)
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE)
    planted_at = models.DateTimeField(default=now)
    age = models.IntegerField(default=0)
