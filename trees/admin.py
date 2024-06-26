from django.contrib import admin

from trees.models import Account, Tree, User

admin.site.register(Account)
admin.site.register(User)
admin.site.register(Tree)
