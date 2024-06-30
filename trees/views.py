from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

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

    @action(detail=True, methods=['get'])
    def planted(self, request, pk=None, *args, **kwargs):
        user = User.objects.get(pk=pk)
        current_user = request.user
        if not current_user.is_superuser:
            if not current_user == user:
                return Response(
                    {'error': "Can't access Planted Trees from another user"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        trees_queryset = PlantedTree.objects.filter(user_id=user.id)
        serializer = PlantedTreeSerializer(trees_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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

    @action(detail=False, methods=['get'])
    def own(self, request, *args, **kwargs):
        user = request.user
        trees_queryset = PlantedTree.objects.filter(user_id=user.id)
        serializer = PlantedTreeSerializer(trees_queryset, many=True)
        return Response(serializer.data)
