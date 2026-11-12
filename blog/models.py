from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending AbstractUser.
    Includes unique email and an explicit full name attribute.
    """
    name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Full name or display name of the user."
    )
    email = models.EmailField(
        unique=True,
        help_text="Unique email address used for identification."
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.name or self.username or self.email

    def save(self, *args, **kwargs):
        # Auto-fill name and username fallback if omitted
        if not self.name and self.username:
            self.name = self.username
        if not self.username and self.email:
            self.username = self.email
        super().save(*args, **kwargs)


class Post(models.Model):
    """
    Blog Post model created by a User.
    """
    title = models.CharField(
        max_length=255,
        help_text="Title of the blog post."
    )
    content = models.TextField(
        help_text="Full text content of the blog post."
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        help_text="Author of the blog post."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Timestamp when the post was created."
    )

    class Meta:
        ordering = ['-created_at', '-id']
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
        indexes = [
            models.Index(fields=['-created_at', '-id']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return self.title


class Comment(models.Model):
    """
    Comment model linked to a Post and written by a User.
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="Post that this comment belongs to."
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="User who wrote this comment."
    )
    comment_text = models.TextField(
        help_text="Content text of the comment."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="Timestamp when the comment was created."
    )

    class Meta:
        ordering = ['-created_at', '-id']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        indexes = [
            models.Index(fields=['post', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"Comment by {self.user.name or self.user.username} on {self.post.title}"

