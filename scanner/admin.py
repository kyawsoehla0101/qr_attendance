# scanner/admin.py
from django.contrib import admin
from .models import UserProfile, QRLog
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    extra = 0
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(QRLog)
class QRLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'direction', 'timestamp')
    list_filter = ('direction', 'timestamp')