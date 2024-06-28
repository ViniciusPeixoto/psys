from rest_framework import serializers

from trees.models import Account, PlantedTree, Profile, Tree, User


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    accounts = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all(), many=True
    )

    class Meta:
        model = User
        fields = '__all__'
        depth = 1


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Profile
        fields = '__all__'
        depth = 1


class TreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tree
        fields = '__all__'


class PlantedTreeSerializer(serializers.ModelSerializer):
    tree = serializers.PrimaryKeyRelatedField(queryset=Tree.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    account = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all()
    )
    age = serializers.IntegerField(required=False)
    location = serializers.ListField(required=False)

    class Meta:
        model = PlantedTree
        fields = '__all__'
        depth = 1
