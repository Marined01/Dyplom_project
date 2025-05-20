from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Key

@admin.register(Key)
class KeyAdmin(admin.ModelAdmin):
    list_display = ('auditory', 'status', 'take_key_time', 'put_key_time', 'holder')
    list_filter = ('status', )
    list_fields = ('auditory', )

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'name', 'surname')
    search_fields = ('email', 'name', 'surname')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),  # логін
        ('Персональні дані', {'fields': ('name', 'surname')}),  # основна інформація
        ('Статус', {'fields': ('is_active',)}),  # статус
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'surname', 'password1', 'password2', 'is_active'),
        }),
    )


