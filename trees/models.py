from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError, models
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


class Tree(models.Model):
    name = models.CharField(
        max_length=settings.CHAR_FIELD_MAX_LENGTH, unique=True
    )
    scientific_name = models.CharField(unique=True)


class User(AbstractUser):
    accounts = models.ManyToManyField(Account, related_name='users')

    class Meta:
        ordering = ['username']

    def plant_tree(
        self,
        account: Account,
        tree: Tree,
        location: tuple[Decimal, Decimal],
    ):
        if account not in self.accounts.all():
            raise ValueError('This Account is not associated with this User.')

        latitude, longitude = location
        planted_tree = PlantedTree.objects.create(
            account=account,
            user=self,
            tree=tree,
            latitude=latitude,
            longitude=longitude,
        )

        return planted_tree

    def plant_trees(
        self,
        account: Account,
        trees: list[tuple[Tree, tuple[Decimal, Decimal]]],
    ) -> bool:
        if account not in self.accounts.all():
            raise ValueError('This Account is not associated with this User.')

        success, failed = [], []
        for tree_entry in trees:
            tree, location = tree_entry
            try:
                success.append(
                    self.plant_tree(
                        account=account, tree=tree, location=location
                    )
                )
            except (
                ValueError,
                ValidationError,
                IntegrityError,
                ObjectDoesNotExist,
            ):
                failed.append(tree_entry)

        return {
            'success': success,
            'failed': failed,
        }


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True
    )
    about = models.TextField()
    joined = models.DateTimeField(auto_now_add=True)


class PlantedTree(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.OneToOneField(Account, on_delete=models.CASCADE)
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE)
    planted_at = models.DateTimeField(default=now)

    # location stored in latitude and longitude with less than a meter precision
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=0)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=0)

    @property
    def age(self):
        today = now()

        # adjusting for month using True == 1
        return (
            today.year
            - self.planted_at.year
            - (
                (today.month, today.day)
                < (self.planted_at.month, self.planted_at.day)
            )
        )

    @property
    def location(self):
        return (self.latitude, self.longitude)
