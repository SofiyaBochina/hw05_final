from django.contrib import admin

from yatube.settings import EMPTY_CONST

from .models import Comment, Follow, Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = EMPTY_CONST


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'slug',
        'title',
        'description',
    )
    search_fields = ('title',)
    list_filter = ('slug', 'title',)
    empty_value_display = EMPTY_CONST


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'post',
        'author',
        'created',
    )
    search_fields = ('text', 'author')
    list_filter = ('post', 'created')
    empty_value_display = EMPTY_CONST


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
    )
    search_fields = ('user', 'author')
    list_filter = ('user', 'author',)
    empty_value_display = EMPTY_CONST
