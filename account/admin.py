from django.contrib import admin

# Register your models here.
from account.models import UserProfile, UserToken


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'reputation']

@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'token']
