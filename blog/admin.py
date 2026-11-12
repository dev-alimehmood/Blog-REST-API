"""
Django Admin configuration for Mini Blog.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count
from .models import User, Post, Comment


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin configuration for custom User model.
    """
    list_display = ('id', 'name', 'email', 'username', 'is_staff', 'is_active', 'date_joined')
    list_display_links = ('id', 'name', 'username')
    search_fields = ('name', 'email', 'username')
    ordering = ('id',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Profile Info', {'fields': ('name',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Custom Profile Info', {'fields': ('name', 'email')}),
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Admin configuration for Blog Posts.
    """
    list_display = ('id', 'title', 'user', 'comment_count_display', 'created_at')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'content', 'user__name', 'user__email')
    list_filter = ('created_at',)
    ordering = ('-created_at', '-id')
    raw_id_fields = ('user',)

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .select_related('user')
            .annotate(comment_count=Count('comments'))
        )

    @admin.display(description='Comments', ordering='comment_count')
    def comment_count_display(self, obj):
        return getattr(obj, 'comment_count', 0)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin configuration for Comments.
    """
    list_display = ('id', 'post', 'user', 'short_comment', 'created_at')
    list_display_links = ('id', 'short_comment')
    search_fields = ('comment_text', 'user__name', 'user__email', 'post__title')
    list_filter = ('created_at',)
    ordering = ('-created_at', '-id')
    raw_id_fields = ('user', 'post')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'post')

    @admin.display(description='Comment Preview')
    def short_comment(self, obj):
        if len(obj.comment_text) > 50:
            return f"{obj.comment_text[:47]}..."
        return obj.comment_text

