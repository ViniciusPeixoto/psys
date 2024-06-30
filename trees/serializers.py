from rest_framework import serializers

from trees.models import Account, PlantedTree, Profile, Tree, User


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    account_ids = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all(),
        source='accounts',
        write_only=True,
        many=True,
    )
    accounts = AccountSerializer(many=True, read_only=True)

    class Meta:
        model = User
        exclude = ['password', 'groups', 'user_permissions']
        depth = 1


class ProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )
    user = UserSerializer(read_only=True)
    joined = serializers.DateTimeField(required=False)

    class Meta:
        model = Profile
        fields = '__all__'
        depth = 1


class TreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tree
        fields = '__all__'


class PlantedTreeSerializer(serializers.ModelSerializer):
    tree_id = serializers.PrimaryKeyRelatedField(
        queryset=Tree.objects.all(), source='tree', write_only=True
    )
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )
    account_id = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all(), source='account', write_only=True
    )
    tree = TreeSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    account = AccountSerializer(read_only=True)

    age = serializers.IntegerField(required=False)
    location = serializers.ListField(required=False)

    class Meta:
        model = PlantedTree
        fields = '__all__'
        depth = 1
