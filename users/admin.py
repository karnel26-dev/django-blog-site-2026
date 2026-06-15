from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Настройка отображения расширенного пользователя в админке.

    UserAdmin уже умеет работать с паролями, группами и правами.
    Мы только добавляем наши поля в карточку пользователя.
    """

    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('phone', 'city', 'avatar')}),
    )
    list_display = ('username', 'email', 'phone', 'city', 'is_staff')

# Register your models here.
