from django.contrib import admin

from .models import Post, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка тегов с автоматическим заполнением slug из name."""

    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Удобный список постов в административной панели."""

    list_display = ('title', 'author', 'created_at', 'like_count')
    list_filter = ('created_at', 'tags', 'author')
    search_fields = ('title', 'text', 'author__username')
    filter_horizontal = ('tags', 'likes')

# Register your models here.
