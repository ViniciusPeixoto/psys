from rest_framework import serializers

from trees.models import Account, PlantedTree, Profile, Tree, User


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    accounts = AccountSerializer(many=True)

    class Meta:
        model = User
        fields = '__all__'
        depth = 1


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Profile
        fields = '__all__'
        depth = 1


class TreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tree
        fields = '__all__'


class PlantedTreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantedTree
        fields = '__all__'
