from django.contrib import admin

from .models import Category, Location, Post, Comments

empty_value_display = 'Не задано'


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'pub_date',
        'author',
        'is_published',
        'location',
        'category',
        'id'
    )
    list_editable = (
        'is_published',
        'location',
        'category',
        'pub_date'
    )
    search_fields = ('title',)
    list_filter = ('category', 'is_published', 'created_at')
    list_display_links = ('title',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'slug',
        'is_published',
        'id',
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('title',)
    list_filter = ('is_published', 'created_at')
    list_display_links = ('title',)


class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_published',
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('name',)
    list_filter = ('is_published', 'created_at')
    list_display_links = ('name',)


class CommentsAdmin(admin.ModelAdmin):
    pass


admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Comments, CommentsAdmin)
