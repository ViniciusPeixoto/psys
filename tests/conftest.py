import pytest

from trees.models import Account, Profile, Tree, User


@pytest.fixture(autouse=True)
def load_db(db):
    zeus = User.objects.create_user(username='Zeus', password='Olympus')
    odin = User.objects.create_user(username='Odin', password='Asgard')
    pope = User.objects.create_user(username='Francis', password='Rome')

    Profile.objects.create(user=zeus, about='I am the King of all Gods')
    Profile.objects.create(user=odin, about='I am the Allfather')
    Profile.objects.create(user=pope, about='I am His Holiness')

    gods = Account.objects.create(name='Gods', active=True)
    humans = Account.objects.create(name='Humans', active=True)

    gods.users.add(zeus)
    gods.users.add(odin)
    humans.users.add(pope)

    olive = Tree.objects.create(name='Olive', scientific_name='Olea europaea')
    pine = Tree.objects.create(
        name='Stone pine', scientific_name='Pinus pinea'
    )
    spruce = Tree.objects.create(
        name='Norway spruce', scientific_name='Picea abies'
    )

    zeus.plant_tree(gods, olive, (40.0834, 22.3499))
    odin.plant_tree(gods, spruce, (63.0106, 8.2941))
    pope.plant_tree(humans, pine, (41.9031, 12.4519))
