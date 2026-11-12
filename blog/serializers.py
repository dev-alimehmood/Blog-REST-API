"""
Serializers for Mini Blog REST API.

Provides serialization, deserialization, and field-level validation
for Users, Posts, Comments, and Analytics queries.
"""

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
    Serializer for full User creation and listing.
    Ensures password is write-only and safely hashed.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={'input_type': 'password'},
        help_text="Password must be at least 8 characters long."
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

    def create(self, validated_data):
        password = validated_data.pop('password')
        name = validated_data.get('name', '').strip()
        email = validated_data['email']
        username = email  # Use email as default username

        user = User(
            username=username,
            email=email,
            name=name
        )
        user.set_password(password)
        user.save()
        return user


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving and listing Posts.
    Includes nested author details and aggregated comment_count.
    """
    author = UserSummarySerializer(source='user', read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True,
        required=False,
        help_text="ID of the user creating the post."
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        help_text="Alternative parameter for author user ID."
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
            'user',
            'comment_count',
            'created_at'
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

    def validate(self, attrs):
        # Resolve either user_id or user
        user = attrs.get('user')
        if not user:
            raise serializers.ValidationError({
                "user_id": "User ID is required to create a post."
            })
        attrs['user'] = user
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and displaying comments.
    Includes commenter details and timestamp.
    """
    commenter_name = serializers.CharField(source='user.name', read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True,
        required=False,
        help_text="ID of the user authoring the comment."
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        required=False,
        help_text="Alternative parameter for user ID."
    )
    author = UserSummarySerializer(source='user', read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'post_id',
            'commenter_name',
            'author',
            'user_id',
            'user',
            'comment_text',
            'created_at'
        ]
        read_only_fields = ['id', 'post_id', 'commenter_name', 'author', 'created_at']

    def validate_comment_text(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Comment text cannot be blank.")
        return cleaned

    def validate(self, attrs):
        user = attrs.get('user')
        if not user:
            raise serializers.ValidationError({
                "user_id": "User ID is required to post a comment."
            })
        attrs['user'] = user
        return attrs


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

