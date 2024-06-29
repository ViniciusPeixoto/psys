from django.contrib import admin
from django.contrib.auth.hashers import make_password

from trees.models import Account, PlantedTree, Tree, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'date_joined']
    search_help_text = 'Name of the account the user is a part of'
    search_fields = ['accounts__name']

    def save_model(self, request, obj, form, change) -> None:
        # hashing newly created user's password
        if not change:
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)


class UserInline(admin.TabularInline):
    model = Account.users.through
    extra = 0
    max_num = 0
    fields = ['username', 'is_active', 'last_login']
    readonly_fields = ['username', 'is_active', 'last_login']
    can_delete = False

    def username(self, obj):
        return obj.user.username

    def is_active(self, obj):
        return obj.user.is_active

    def last_login(self, obj):
        return obj.user.last_login


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'created', 'active']
    list_editable = ['active']
    inlines = [UserInline]


class PlantedTreeInline(admin.TabularInline):
    model = PlantedTree
    extra = 0
    max_num = 0
    fields = ['user', 'account', 'location']
    readonly_fields = ['user', 'account', 'location']
    can_delete = False


@admin.register(Tree)
class TreeAdmin(admin.ModelAdmin):
    list_display = ['name', 'scientific_name']
    inlines = [PlantedTreeInline]
