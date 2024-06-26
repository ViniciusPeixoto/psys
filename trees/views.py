from rest_framework import permissions, viewsets

from trees.models import Account, PlantedTree, Profile, Tree, User
from trees.serializers import (
    AccountSerializer,
    PlantedTreeSerializer,
    ProfileSerializer,
    TreeSerializer,
    UserSerializer,
)


class AccountViewSet(viewsets.ModelViewSet):
    """
    Lists, creates, retrieves, updates and deletes Accounts
    """

    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class UserViewSet(viewsets.ModelViewSet):
    """
    Lists, creates, retrieves, updates and deletes Users
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class TreeViewSet(viewsets.ModelViewSet):
    """
    Lists, creates, retrieves, updates and deletes Trees
    """

    queryset = Tree.objects.all()
    serializer_class = TreeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ProfileViewSet(viewsets.ModelViewSet):
    """
    Lists, creates, retrieves, updates and deletes Profiles
    """

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class PlantedTreeViewSet(viewsets.ModelViewSet):
    """
    Lists, creates, retrieves, updates and deletes PlantedTrees
    """

    queryset = PlantedTree.objects.all()
    serializer_class = PlantedTreeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
