"""
Serializers for Mini Blog REST API.

Provides serialization, deserialization, and validation
for Users, Posts, Comments, and Analytics responses.
"""

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import User, Post, Comment


class UserSummarySerializer(serializers.ModelSerializer):
    """
    Compact user representation embedded in post and comment responses.
    """
    class Meta:
        model = User
        fields = ['id', 'name', 'email']
        read_only_fields = ['id', 'name', 'email']


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User creation and retrieval.
    Applies Django's configured password validators and ensures passwords are write-only.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Password must satisfy Django password validation rules."
    )

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'date_joined']
        read_only_fields = ['id', 'date_joined']

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Name cannot be empty or blank.")
        return value.strip()

    def validate_email(self, value):
        normalized_email = value.lower().strip()
        if User.objects.filter(email__iexact=normalized_email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return normalized_email

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        name = validated_data.get('name', '').strip()
        email = validated_data['email']

        return User.objects.create_user(
            username=email,
            email=email,
            name=name,
            password=password,
        )


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for creating, retrieving, and listing Posts.
    Accepts user_id on write, outputs nested author details and comment count on read.
    """
    author = UserSummarySerializer(source='user', read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True,
        required=True,
        help_text="ID of the user creating the post."
    )
    comment_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'content',
            'author',
            'user_id',
            'comment_count',
            'created_at',
        ]
        read_only_fields = ['id', 'author', 'comment_count', 'created_at']

    def validate_title(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Title cannot be blank or contain only whitespace.")
        if len(cleaned) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long.")
        return cleaned

    def validate_content(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Content cannot be blank or contain only whitespace.")
        return cleaned


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and displaying comments.
    Accepts user_id on write, outputs commenter details on read.
    """
    commenter_name = serializers.CharField(source='user.name', read_only=True)
    author = UserSummarySerializer(source='user', read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True,
        required=True,
        help_text="ID of the user authoring the comment."
    )

    class Meta:
        model = Comment
        fields = [
            'id',
            'post_id',
            'commenter_name',
            'author',
            'user_id',
            'comment_text',
            'created_at',
        ]
        read_only_fields = ['id', 'post_id', 'commenter_name', 'author', 'created_at']

    def validate_comment_text(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Comment text cannot be blank.")
        return cleaned


class TopPostSerializer(serializers.Serializer):
    """
    Serializer for Query 1: Top 3 posts with highest comment counts.
    """
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    total_comments = serializers.IntegerField(read_only=True)


class ActiveUserSerializer(serializers.Serializer):
    """
    Serializer for Query 2 & Query 3: Users annotated with total comments.
    """
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)
    total_comments = serializers.IntegerField(read_only=True)


class MostActiveUserResponseSerializer(serializers.Serializer):
    """
    Documentation schema covering both active user data and the empty database state.
    """
    id = serializers.IntegerField(required=False, allow_null=True)
    name = serializers.CharField(required=False, allow_null=True)
    email = serializers.EmailField(required=False, allow_null=True)
    total_comments = serializers.IntegerField(required=False, allow_null=True)
    detail = serializers.CharField(required=False)
    user = serializers.CharField(required=False, allow_null=True)


class PaginatedPostListSerializer(serializers.Serializer):
    """
    OpenAPI schema for paginated post listings.
    """
    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    results = PostSerializer(many=True)


class PaginatedCommentListSerializer(serializers.Serializer):
    """
    OpenAPI schema for paginated comment listings.
    """
    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True)
    previous = serializers.CharField(allow_null=True)
    results = CommentSerializer(many=True)
