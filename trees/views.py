from django.contrib.auth import authenticate, login, logout
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from trees.models import Account, PlantedTree, Profile, Tree, User
from trees.permissions import IsOwnerOrAdmin
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
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrAdmin,
    ]

    @action(detail=True, methods=['get'])
    def planted(self, request, pk=None, *args, **kwargs):
        self.check_object_permissions(request, User.objects.get(pk=pk))
        trees_queryset = PlantedTree.objects.filter(user_id=pk)
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
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrAdmin,
    ]

    def retrieve(self, request, pk=None):
        # retrieves profile based on user
        profile = Profile.objects.get(user__id=pk)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)


class PlantedTreeViewSet(viewsets.ModelViewSet):
    """
    Creates, retrieves, updates and deletes PlantedTrees
    """

    queryset = PlantedTree.objects.all()
    serializer_class = PlantedTreeSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrAdmin,
    ]

    def list(self, request, *args, **kwargs):
        # Can't show users Planted Trees they aren't supposed to see
        return Response(
            {'message': 'List function is not offered in this path'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def create(self, request, *args, **kwargs):
        self.check_object_permissions(
            request, User.objects.get(id=request.data.get('user_id'))
        )
        return super().create(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def own(self, request, *args, **kwargs):
        user = request.user
        trees_queryset = PlantedTree.objects.filter(user_id=user.id)
        serializer = PlantedTreeSerializer(trees_queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def account(self, request, *args, **kwargs):
        account_name = request.GET.get('account')
        current_user = request.user
        if not current_user.is_superuser:
            if not current_user.accounts.filter(name=account_name).exists():
                return Response(
                    {
                        'error': "Can't access Planted Trees from accounts you are not part of"
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
        trees_queryset = PlantedTree.objects.filter(account__name=account_name)
        serializer = PlantedTreeSerializer(trees_queryset, many=True)
        return Response(serializer.data)


class LoginView(APIView):
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({'login': 'success'}, status=status.HTTP_200_OK)
        return Response(
            {'login': 'failed'}, status=status.HTTP_401_UNAUTHORIZED
        )

    def delete(self, request):
        logout(request)
        return Response({'logout': 'success'}, status=status.HTTP_200_OK)
