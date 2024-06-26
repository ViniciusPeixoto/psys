from django.urls import include, path
from rest_framework.routers import SimpleRouter

from trees import views

router = SimpleRouter()
router.register(r'accounts', viewset=views.AccountViewSet)
router.register(r'users', viewset=views.UserViewSet)
router.register(r'profiles', viewset=views.ProfileViewSet)
router.register(r'trees', viewset=views.TreeViewSet)
router.register(r'planted', viewset=views.PlantedTreeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
