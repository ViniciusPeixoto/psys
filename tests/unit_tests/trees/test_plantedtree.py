from datetime import datetime, timedelta, timezone

import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.forms import model_to_dict
from django.urls import reverse

from trees.models import Account, PlantedTree, Tree, User


@pytest.mark.django_db
def test_newly_planted_trees_have_correct_parameters():
    lat, long = (-22.0123, -47.8908)
    user = User.objects.get(username='Zeus')
    account = user.accounts.first()
    tree = Tree.objects.get(name='Olive')
    alpha = PlantedTree.objects.create(
        tree_id=tree.id,
        user_id=user.id,
        account_id=account.id,
        latitude=lat,
        longitude=long,
    )
    now = datetime.now().replace(tzinfo=timezone(timedelta(hours=-3)))

    assert alpha.planted_at - now < timedelta(seconds=5)
    assert alpha.age == 0
    assert alpha.location == (lat, long)


@pytest.mark.django_db
def test_planted_tree_viewset_get(client):
    url = reverse('plantedtree-list')

    response = client.get(url)

    # cannot list all planted trees
    assert response.status_code == 405


@pytest.mark.django_db
def test_planted_tree_viewset_get_tree(client):
    planted = PlantedTree.objects.filter(user__username='Zeus').first()
    user = User.objects.get(username='Zeus')
    url = reverse('plantedtree-detail', args=[planted.id])

    client.force_login(user)
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_planted_tree_viewset_get_tree_from_another_user(client):
    planted = PlantedTree.objects.exclude(user__username='Zeus').first()
    user = User.objects.get(username='Zeus')
    url = reverse('plantedtree-detail', args=[planted.id])

    client.force_login(user)
    response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_planted_tree_viewset_unauthorized(client):
    data = {'tree_id': 1}
    url = reverse('plantedtree-list')

    response = client.post(url, data=data, content_type='application/json')

    assert response.status_code == 403


@pytest.mark.django_db
def test_planted_tree_viewset_post(client, django_user_model):
    user = django_user_model.objects.create(
        username='test_user', password='test_password'
    )
    account = Account.objects.get(name='Humans')
    tree = Tree.objects.get(name='Olive')
    lat, long = (-22.0123, -47.8908)
    data = {
        'tree_id': tree.id,
        'user_id': user.id,
        'account_id': account.id,
        'latitude': lat,
        'longitude': long,
    }
    url = reverse('plantedtree-list')
    now = datetime.now().replace(tzinfo=timezone(timedelta(hours=-3)))

    client.force_login(user)
    response = client.post(url, data=data, content_type='application/json')

    assert response.status_code == 201

    planted_at = datetime.strptime(
        response.json().get('planted_at'), '%Y-%m-%dT%H:%M:%S.%f%z'
    )
    assert planted_at - now < timedelta(seconds=5)
    assert response.json().get('latitude') == f'{lat:.6f}'
    assert response.json().get('longitude') == f'{long:.6f}'


@pytest.mark.django_db
def test_planted_tree_viewset_post_for_another_user(client, django_user_model):
    user = django_user_model.objects.create(
        username='test_user', password='test_password'
    )
    zeus = User.objects.get(username='Zeus')
    account = Account.objects.get(name='Humans')
    tree = Tree.objects.get(name='Olive')
    lat, long = (-22.0123, -47.8908)
    data = {
        'tree_id': tree.id,
        'user_id': zeus.id,
        'account_id': account.id,
        'latitude': lat,
        'longitude': long,
    }
    url = reverse('plantedtree-list')

    client.force_login(user)
    response = client.post(url, data=data, content_type='application/json')

    assert response.status_code == 403


@pytest.mark.django_db
def test_planted_tree_viewset_patch(client, django_user_model):
    user = django_user_model.objects.get(username='Zeus')
    alpha = PlantedTree.objects.filter(user__username='Zeus').first()
    data = {'latitude': -22.0123}
    url = reverse('plantedtree-detail', args=[alpha.id])

    client.force_login(user)
    response = client.patch(url, data=data, content_type='application/json')

    assert response.status_code == 200
    assert response.json().get('latitude') == '-22.012300'
    assert response.json().get('longitude') == '22.349900'


@pytest.mark.django_db
def test_planted_tree_viewset_delete(client, django_user_model):
    user = django_user_model.objects.get(username='Zeus')
    alpha = PlantedTree.objects.filter(user__username='Zeus').first()
    url = reverse('plantedtree-detail', args=[alpha.id])

    client.force_login(user)
    response = client.delete(url)

    assert response.status_code == 204
    with pytest.raises(ObjectDoesNotExist):
        PlantedTree.objects.get(id=alpha.id)


@pytest.mark.django_db
def test_list_plants_from_current_user(client):
    user = User.objects.get(username='Zeus')
    client.force_login(user)

    url = reverse('plantedtree-own')

    response = client.get(url)

    assert response.status_code == 200
    trees = [
        model_to_dict(tree)
        for tree in PlantedTree.objects.filter(user__username='Zeus').all()
    ]
    results = response.json()
    for tree, result in zip(trees, results):
        assert tree.get('id') == result.get('id')


@pytest.mark.django_db
def test_list_plants_from_account(client):
    user = User.objects.get(username='Zeus')
    user_account = user.accounts.first()
    client.force_login(user)

    url = reverse('plantedtree-account')

    response = client.get(url, data={'account': user_account.name})

    assert response.status_code == 200
    trees = [
        model_to_dict(tree)
        for tree in PlantedTree.objects.filter(account__name=user_account.name)
    ]
    results = response.json()
    for tree, result in zip(trees, results):
        assert tree.get('id') == result.get('id')


@pytest.mark.django_db
def test_list_plants_from_another_account(client):
    user = User.objects.get(username='Zeus')
    another_account = Account.objects.exclude(users__username='Zeus').first()
    client.force_login(user)

    url = reverse('plantedtree-account')

    response = client.get(url, data={'account': another_account.name})

    assert response.status_code == 403
