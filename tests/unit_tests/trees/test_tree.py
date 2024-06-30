import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse

from trees.models import Tree


@pytest.mark.django_db
def test_newly_trees_have_correct_parameters():
    tree = Tree.objects.create(
        name='Brazilwood', scientific_name='Paubrasilia echinata'
    )

    assert tree.name == 'Brazilwood'
    assert tree.scientific_name == 'Paubrasilia echinata'


@pytest.mark.django_db
def test_tree_viewset_get(client):
    url = reverse('tree-list')

    response = client.get(url)

    assert response.status_code == 200
    assert len(response.json()) == 3
    trees = response.json()
    assert all(
        tree.get('name') in ['Olive', 'Stone pine', 'Norway spruce']
        for tree in trees
    )


@pytest.mark.django_db
def test_tree_viewset_unauthorized(client):
    data = {'name': 'Brazilwood', 'scientific_name': 'Paubrasilia echinata'}
    url = reverse('tree-list')

    response = client.post(url, data=data, content_type='application/json')

    assert response.status_code == 403


@pytest.mark.django_db
def test_tree_viewset_post(client, django_user_model):
    user = django_user_model.objects.create(
        username='test_user', password='test_password'
    )
    data = {'name': 'Brazilwood', 'scientific_name': 'Paubrasilia echinata'}
    url = reverse('tree-list')

    client.force_login(user)
    response = client.post(url, data=data, content_type='application/json')

    assert response.status_code == 201
    assert response.json().get('name') == 'Brazilwood'
    assert response.json().get('scientific_name') == 'Paubrasilia echinata'


@pytest.mark.django_db
def test_tree_viewset_patch(client, django_user_model):
    user = django_user_model.objects.create(
        username='test_user', password='test_password'
    )
    tree = Tree.objects.get(name='Olive')
    data = {'scientific_name': 'Paubrasilia echinata'}
    url = reverse('tree-detail', args=[tree.id])

    client.force_login(user)
    response = client.patch(url, data=data, content_type='application/json')

    assert response.status_code == 200
    assert response.json().get('scientific_name') == 'Paubrasilia echinata'


@pytest.mark.django_db
def test_tree_viewset_delete(client, django_user_model):
    user = django_user_model.objects.create(
        username='test_user', password='test_password'
    )
    tree = Tree.objects.get(name='Olive')
    url = reverse('tree-detail', args=[tree.id])

    client.force_login(user)
    response = client.delete(url)

    assert response.status_code == 204
    with pytest.raises(ObjectDoesNotExist):
        Tree.objects.get(id=tree.id)
