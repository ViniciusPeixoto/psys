from datetime import datetime, timedelta, timezone
from random import uniform

import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.forms import model_to_dict
from django.urls import reverse

from trees.models import Account, PlantedTree, Tree, User


@pytest.mark.django_db
def test_newly_users_have_correct_parameters():
    alpha = User.objects.create_user(username='alpha', password='beta')
    now = datetime.now().replace(tzinfo=timezone(timedelta(hours=-3)))

    assert alpha.username == 'alpha'
    assert alpha.date_joined - now < timedelta(seconds=5)
    assert not alpha.is_superuser
    assert not alpha.is_staff
    assert alpha.is_active
    assert len(alpha.accounts.all()) == 0


@pytest.mark.django_db
def test_user_viewset_get(client):
    url = reverse('user-list')

    response = client.get(url)

    assert response.status_code == 200
    assert len(response.json()) == 3
    users = response.json()
    assert all(
        user.get('username') in ['Zeus', 'Odin', 'Francis'] for user in users
    )


@pytest.mark.django_db
def test_user_viewset_unauthorized(client):
    data = {'username': 'alpha'}
    url = reverse('user-list')

    response = client.post(url, data=data, content_type='application/json')

    assert response.status_code == 403


@pytest.mark.django_db
def test_user_viewset_post(client, django_user_model):
    user = django_user_model.objects.create(
        username='test_user', password='test_password'
    )
    humans = Account.objects.get(name='Humans')
    data = {
        'username': 'alpha',
        'password': 'beta',
        'account_ids': [humans.id],
    }
    url = reverse('user-list')
    now = datetime.now().replace(tzinfo=timezone(timedelta(hours=-3)))

    client.force_login(user)
    response = client.post(url, data=data, content_type='application/json')

    assert response.status_code == 201
    assert response.json().get('username') == 'alpha'
    # can't show password in response
    assert response.json().get('password') is None

    joined = datetime.strptime(
        response.json().get('date_joined'), '%Y-%m-%dT%H:%M:%S.%f%z'
    )
    assert joined - now < timedelta(seconds=5)

    created = User.objects.get(username='alpha')
    assert created.check_password('beta')


@pytest.mark.django_db
def test_user_viewset_patch(client, django_user_model):
    user = django_user_model.objects.create(
        username='test_user', password='test_password'
    )
    data = {'username': 'beta', 'is_active': False}
    url = reverse('user-detail', args=[user.id])

    client.force_login(user)
    response = client.patch(url, data=data, content_type='application/json')

    assert response.status_code == 200

    assert response.json().get('username') == 'beta'
    joined = datetime.strptime(
        response.json().get('date_joined'), '%Y-%m-%dT%H:%M:%S.%f%z'
    )
    assert joined == user.date_joined
    assert response.json().get('is_active') is False


@pytest.mark.django_db
def test_user_viewset_delete(client, django_user_model):
    user = django_user_model.objects.create(
        username='test_user', password='test_password'
    )
    zeus = User.objects.get(username='Zeus')
    url = reverse('user-detail', args=[zeus.id])

    client.force_login(user)
    response = client.delete(url)

    assert response.status_code == 204
    with pytest.raises(ObjectDoesNotExist):
        User.objects.get(id=zeus.id)


@pytest.mark.django_db
def test_user_viewset_planted(client):
    zeus = User.objects.get(username='Zeus')

    url = reverse('user-planted', args=[zeus.id])

    client.force_login(zeus)
    response = client.get(url)

    assert response.status_code == 200
    trees = [
        model_to_dict(tree)
        for tree in PlantedTree.objects.filter(user__username='Zeus')
    ]
    results = response.json()
    for tree, result in zip(trees, results):
        assert tree.get('id') == result.get('id')


@pytest.mark.django_db
def test_user_viewset_planted_different_account(client):
    zeus = User.objects.get(username='Zeus')
    pope = User.objects.get(username='Francis')

    url = reverse('user-planted', args=[zeus.id])

    client.force_login(pope)
    response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_user_plant_tree():
    zeus = User.objects.get(username='Zeus')
    tree = Tree.objects.create(
        name='Brazilwood', scientific_name='Paubrasilia echinata'
    )
    zeus.plant_tree(zeus.accounts.first(), tree, (27.9811, 86.9250))

    zeus_trees = PlantedTree.objects.filter(user__username='Zeus')
    assert len(zeus_trees) == 2
    assert all(
        planted_tree.tree.name in ['Olive', 'Brazilwood']
        for planted_tree in zeus_trees
    )


@pytest.mark.django_db
def test_user_plant_tree_wrong_account():
    zeus = User.objects.get(username='Zeus')
    humans = Account.objects.get(name='Humans')
    tree = Tree.objects.create(
        name='Brazilwood', scientific_name='Paubrasilia echinata'
    )
    with pytest.raises(ValueError):
        zeus.plant_tree(humans, tree, (27.9811, 86.9250))


@pytest.mark.django_db
def test_user_plant_trees():
    zeus = User.objects.get(username='Zeus')
    trees = [
        planted.tree
        for planted in PlantedTree.objects.exclude(user__username='Zeus')
    ]
    trees_to_plant = [
        (tree, (uniform(-90, 90), uniform(-180, 180))) for tree in trees
    ]

    result = zeus.plant_trees(zeus.accounts.first(), trees_to_plant)
    assert result.get('failed') == []

    zeus_trees = PlantedTree.objects.filter(user__username='Zeus')
    assert len(zeus_trees) == 3
    assert all(
        planted_tree.tree.name in ['Olive', 'Stone pine', 'Norway spruce']
        for planted_tree in zeus_trees
    )


@pytest.mark.django_db
def test_user_plant_trees_with_failed():
    zeus = User.objects.get(username='Zeus')
    humans = Account.objects.get(name='Humans')
    trees = [planted.tree for planted in PlantedTree.objects.all()]
    trees_to_plant = [
        (tree, (uniform(-90, 90), uniform(-180, 180))) for tree in trees
    ]

    result = zeus.plant_trees(humans, trees_to_plant)
    assert len(result.get('failed')) == 3
