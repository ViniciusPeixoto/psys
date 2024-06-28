from datetime import datetime, timedelta, timezone

import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse

from trees.models import Account, PlantedTree, Tree


@pytest.mark.django_db
def test_newly_planted_trees_have_correct_parameters():
    lat, long = (-22.0123, -47.8908)
    alpha = PlantedTree.objects.create(
        tree_id=1, user_id=1, account_id=1, latitude=lat, longitude=long
    )
    now = datetime.now().replace(tzinfo=timezone(timedelta(hours=-3)))

    assert alpha.planted_at - now < timedelta(seconds=5)
    assert alpha.age == 0
    assert alpha.location == (lat, long)


@pytest.mark.django_db
def test_planted_tree_viewset_get(client):
    PlantedTree.objects.create(tree_id=1, user_id=1, account_id=1)
    url = reverse('plantedtree-list')

    response = client.get(url)

    assert response.status_code == 200
    assert len(response.json()) == 1
    planted_tree = response.json().pop()
    assert planted_tree.get('location') == [0, 0]


@pytest.mark.django_db
def test_planted_tree_viewset_unauthorized(client):
    data = {'tree_id': 1}
    url = reverse('plantedtree-list')

    response = client.post(url, data=data, content_type='application/json')

    assert response.status_code == 403


@pytest.mark.django_db
def test_planted_tree_viewset_post(client, django_user_model):
    username = 'test_user'
    password = 'test_password'
    user = django_user_model.objects.create(
        username=username, password=password
    )
    account = Account.objects.create(name='alpha')
    tree = Tree.objects.create(
        name='Brazilwood', scientific_name='Paubrasilia echinata'
    )
    lat, long = (-22.0123, -47.8908)
    data = {
        'tree': tree.id,
        'user': user.id,
        'account': account.id,
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
def test_planted_tree_viewset_patch(client, django_user_model):
    username = 'test_user'
    password = 'test_password'
    user = django_user_model.objects.create(
        username=username, password=password
    )
    alpha = PlantedTree.objects.create(tree_id=1, user_id=1, account_id=1)
    data = {'latitude': -22.0123}
    url = reverse('plantedtree-detail', args=[alpha.id])

    client.force_login(user)
    response = client.patch(url, data=data, content_type='application/json')

    assert response.status_code == 200
    assert response.json().get('latitude') == '-22.012300'
    assert response.json().get('longitude') == '0.000000'


@pytest.mark.django_db
def test_planted_tree_viewset_delete(client, django_user_model):
    username = 'test_user'
    password = 'test_password'
    user = django_user_model.objects.create(
        username=username, password=password
    )
    alpha = PlantedTree.objects.create(tree_id=1, user_id=1, account_id=1)
    url = reverse('plantedtree-detail', args=[alpha.id])

    client.force_login(user)
    response = client.delete(url)

    assert response.status_code == 204
    with pytest.raises(ObjectDoesNotExist):
        PlantedTree.objects.get(id=alpha.id)
