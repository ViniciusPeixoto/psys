from datetime import datetime, timedelta, timezone

import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse

from trees.models import Profile


@pytest.mark.django_db
def test_newly_profiles_have_correct_parameters(django_user_model):
    user = django_user_model.objects.create(
        username='test_user', password='test_password'
    )
    alpha = Profile.objects.create(
        user_id=user.id, about='This is the Alpha profile'
    )
    now = datetime.now().replace(tzinfo=timezone(timedelta(hours=-3)))

    assert alpha.about == 'This is the Alpha profile'
    assert alpha.joined - now < timedelta(seconds=5)


@pytest.mark.django_db
def test_profile_viewset_get(client):
    url = reverse('profile-list')

    response = client.get(url)

    assert response.status_code == 200
    assert len(response.json()) == 3
    profiles = response.json()
    assert all(
        profile.get('user').get('username') in ['Zeus', 'Odin', 'Francis']
        for profile in profiles
    )


@pytest.mark.django_db
def test_profile_viewset_unauthorized(client):
    data = {'about': 'This is the Alpha profile'}
    url = reverse('profile-list')

    response = client.post(url, data=data, content_type='application/json')

    assert response.status_code == 403


@pytest.mark.django_db
def test_profile_viewset_post(client, django_user_model):
    user = django_user_model.objects.create(
        username='test_user', password='test_password'
    )
    data = {'user_id': user.id, 'about': 'This is the Alpha profile'}
    url = reverse('profile-list')
    now = datetime.now().replace(tzinfo=timezone(timedelta(hours=-3)))

    client.force_login(user)
    response = client.post(url, data=data, content_type='application/json')

    assert response.status_code == 201
    assert response.json().get('about') == 'This is the Alpha profile'

    joined = datetime.strptime(
        response.json().get('joined'), '%Y-%m-%dT%H:%M:%S.%f%z'
    )
    assert joined - now < timedelta(seconds=5)


@pytest.mark.django_db
def test_profile_viewset_patch(client, django_user_model):
    user = django_user_model.objects.create(
        username='test_user', password='test_password'
    )
    alpha = Profile.objects.get(user__username='Zeus')
    data = {'user_id': alpha.user.id, 'about': 'This is the Beta profile'}
    url = reverse('profile-detail', args=[alpha.id])
    now = datetime.now().replace(tzinfo=timezone(timedelta(hours=-3)))

    client.force_login(user)
    response = client.patch(url, data=data, content_type='application/json')

    assert response.status_code == 200
    assert response.json().get('about') == 'This is the Beta profile'

    joined = datetime.strptime(
        response.json().get('joined'), '%Y-%m-%dT%H:%M:%S.%f%z'
    )
    assert joined - now < timedelta(seconds=5)


@pytest.mark.django_db
def test_profile_viewset_delete(client, django_user_model):
    user = django_user_model.objects.create(
        username='test_user', password='test_password'
    )
    alpha = Profile.objects.get(user__username='Zeus')
    url = reverse('profile-detail', args=[alpha.id])

    client.force_login(user)
    response = client.delete(url)

    assert response.status_code == 204
    with pytest.raises(ObjectDoesNotExist):
        Profile.objects.get(user_id=1)
