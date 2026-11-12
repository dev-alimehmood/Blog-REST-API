"""
API Views for Mini Blog Platform.

Includes post management, nested comments, and optimized analytics endpoints.
Fully documented with drf-spectacular OpenAPI schemas and examples.
"""

from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse,
    inline_serializer,
)
from rest_framework import serializers

from .models import User, Post, Comment
from .serializers import (
    UserSerializer,
    UserSummarySerializer,
    PostSerializer,
    CommentSerializer,
    TopPostSerializer,
    ActiveUserSerializer,
)
from .queries import (
    get_top_three_posts,
    get_users_with_more_than_three_comments,
    get_most_active_user,
    get_comments_for_post,
)
from .pagination import StandardResultsSetPagination


# ==============================================================================
# USER MANAGEMENT VIEWS (Helper for evaluation & testing)
# ==============================================================================

@extend_schema_view(
    get=extend_schema(
        tags=['Users'],
        summary="List all users",
        description="Returns a paginated list of registered users.",
        responses={200: UserSerializer(many=True)}
    ),
    post=extend_schema(
        tags=['Users'],
        summary="Register a new user",
        description="Creates a new user with secure password hashing and unique email validation.",
        request=UserSerializer,
        responses={
            201: UserSerializer,
            400: OpenApiResponse(description="Validation error (e.g., duplicate email or missing fields).")
        },
        examples=[
            OpenApiExample(
                "Create User Request",
                value={
                    "name": "Jane Doe",
                    "email": "jane@example.com",
                    "password": "StrongPassword123!"
                },
                request_only=True
            ),
            OpenApiExample(
                "User Created Response",
                value={
                    "id": 1,
                    "name": "Jane Doe",
                    "email": "jane@example.com",
                    "date_joined": "2026-11-12T10:00:00Z"
                },
                response_only=True
            )
        ]
    )
)
class UserListCreateView(ListCreateAPIView):
    """
    Endpoint for listing users and registering new accounts.
    """
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination


@extend_schema(
    tags=['Users'],
    summary="Retrieve user details",
    description="Fetch single user profile by ID.",
    responses={
        200: UserSerializer,
        404: OpenApiResponse(description="User not found.")
    }
)
class UserDetailView(RetrieveAPIView):
    """
    Endpoint for retrieving a specific user by ID.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


# ==============================================================================
# POSTS MANAGEMENT VIEWS
# ==============================================================================

class PostListCreateView(APIView):
    """
    POST /api/posts/ - Create a new post.
    GET  /api/posts/ - List all posts with pagination and comment count.
    """
    pagination_class = StandardResultsSetPagination

    @extend_schema(
        tags=['Posts'],
        summary="List all blog posts",
        description=(
            "Retrieves a paginated list of all blog posts.\n\n"
            "Query Optimization:\n"
            "- Uses `select_related('user')` to fetch author details in a single SQL JOIN.\n"
            "- Uses `annotate(comment_count=Count('comments'))` to calculate total comments per post without N+1 queries."
        ),
        parameters=[
            OpenApiParameter(name='page', type=int, location=OpenApiParameter.QUERY, description='Page number'),
            OpenApiParameter(name='page_size', type=int, location=OpenApiParameter.QUERY, description='Items per page (max 100)'),
        ],
        responses={200: PostSerializer(many=True)},
        examples=[
            OpenApiExample(
                "List Posts Response",
                value={
                    "count": 1,
                    "next": None,
                    "previous": None,
                    "results": [
                        {
                            "id": 1,
                            "title": "Mastering Django ORM",
                            "content": "Deep dive into query optimization and indexing in Django...",
                            "author": {
                                "id": 1,
                                "name": "Jane Doe",
                                "email": "jane@example.com"
                            },
                            "comment_count": 5,
                            "created_at": "2026-11-12T12:00:00Z"
                        }
                    ]
                },
                response_only=True
            )
        ]
    )
    def get(self, request):
        queryset = (
            Post.objects
            .select_related('user')
            .annotate(comment_count=Count('comments'))
            .order_by('-created_at', '-id')
        )
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = PostSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        tags=['Posts'],
        summary="Create a new blog post",
        description="Creates a new blog post. Requires title, content, and valid user ID.",
        request=PostSerializer,
        responses={
            201: PostSerializer,
            400: OpenApiResponse(description="Validation error (e.g., missing fields, nonexistent user).")
        },
        examples=[
            OpenApiExample(
                "Create Post Request",
                value={
                    "title": "Mastering Django ORM",
                    "content": "Deep dive into query optimization and indexing in Django...",
                    "user_id": 1
                },
                request_only=True
            ),
            OpenApiExample(
                "Post Created Response",
                value={
                    "id": 1,
                    "title": "Mastering Django ORM",
                    "content": "Deep dive into query optimization and indexing in Django...",
                    "author": {
                        "id": 1,
                        "name": "Jane Doe",
                        "email": "jane@example.com"
                    },
                    "comment_count": 0,
                    "created_at": "2026-11-12T12:00:00Z"
                },
                response_only=True
            )
        ]
    )
    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save()
            # Re-read post with author select_related and comment count for consistent output
            response_post = (
                Post.objects
                .select_related('user')
                .annotate(comment_count=Count('comments'))
                .get(id=post.id)
            )
            response_serializer = PostSerializer(response_post)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    """
    GET /api/posts/{id}/ - Retrieve a single post with author details and comment count.
    """

    @extend_schema(
        tags=['Posts'],
        summary="Retrieve a single blog post",
        description="Fetches full details of a specific blog post including author information and total comment count.",
        responses={
            200: PostSerializer,
            404: OpenApiResponse(description="Post not found.")
        },
        examples=[
            OpenApiExample(
                "Post Detail Response",
                value={
                    "id": 1,
                    "title": "Mastering Django ORM",
                    "content": "Deep dive into query optimization and indexing in Django...",
                    "author": {
                        "id": 1,
                        "name": "Jane Doe",
                        "email": "jane@example.com"
                    },
                    "comment_count": 3,
                    "created_at": "2026-11-12T12:00:00Z"
                },
                response_only=True
            )
        ]
    )
    def get(self, request, pk):
        try:
            post = (
                Post.objects
                .select_related('user')
                .annotate(comment_count=Count('comments'))
                .get(pk=pk)
            )
        except Post.DoesNotExist:
            return Response(
                {"detail": f"Post with ID {pk} does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = PostSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ==============================================================================
# COMMENTS MANAGEMENT VIEWS
# ==============================================================================

class PostCommentListCreateView(APIView):
    """
    POST /api/posts/{id}/comments/ - Add a comment to a specific post.
    GET  /api/posts/{id}/comments/ - List comments for a post (Query 4).
    """
    pagination_class = StandardResultsSetPagination

    @extend_schema(
        tags=['Comments'],
        summary="List all comments for a post",
        description=(
            "Retrieves all comments written on a specific post sorted newest first.\n\n"
            "Query 4 Requirement:\n"
            "- Uses `select_related('user')` to fetch commenter details without N+1 queries.\n"
            "- Validates post existence, returning 404 if invalid."
        ),
        parameters=[
            OpenApiParameter(name='page', type=int, location=OpenApiParameter.QUERY, description='Page number'),
            OpenApiParameter(name='page_size', type=int, location=OpenApiParameter.QUERY, description='Items per page'),
        ],
        responses={
            200: CommentSerializer(many=True),
            404: OpenApiResponse(description="Post not found.")
        },
        examples=[
            OpenApiExample(
                "List Comments Response",
                value={
                    "count": 1,
                    "next": None,
                    "previous": None,
                    "results": [
                        {
                            "id": 1,
                            "post_id": 1,
                            "commenter_name": "Bob Smith",
                            "author": {
                                "id": 2,
                                "name": "Bob Smith",
                                "email": "bob@example.com"
                            },
                            "comment_text": "Excellent explanation of ORM queries!",
                            "created_at": "2026-11-12T13:00:00Z"
                        }
                    ]
                },
                response_only=True
            )
        ]
    )
    def get(self, request, pk):
        # Query 4: Fetch all comments for a given post using select_related('user')
        try:
            comments_queryset = get_comments_for_post(post_id=pk)
        except Exception:
            return Response(
                {"detail": f"Post with ID {pk} does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(comments_queryset, request)
        serializer = CommentSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        tags=['Comments'],
        summary="Add a comment to a blog post",
        description="Posts a new comment on a specific post. Validates that both the post and user exist.",
        request=CommentSerializer,
        responses={
            201: CommentSerializer,
            400: OpenApiResponse(description="Validation error (e.g., missing comment text or invalid user)."),
            404: OpenApiResponse(description="Post not found.")
        },
        examples=[
            OpenApiExample(
                "Create Comment Request",
                value={
                    "user_id": 2,
                    "comment_text": "Great article! Very clear and helpful."
                },
                request_only=True
            ),
            OpenApiExample(
                "Comment Created Response",
                value={
                    "id": 1,
                    "post_id": 1,
                    "commenter_name": "Bob Smith",
                    "author": {
                        "id": 2,
                        "name": "Bob Smith",
                        "email": "bob@example.com"
                    },
                    "comment_text": "Great article! Very clear and helpful.",
                    "created_at": "2026-11-12T13:00:00Z"
                },
                response_only=True
            )
        ]
    )
    def post(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response(
                {"detail": f"Post with ID {pk} does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(post=post)
            # Re-read with select_related for clean output
            refetched = Comment.objects.select_related('user').get(id=comment.id)
            response_serializer = CommentSerializer(refetched)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==============================================================================
# ANALYTICS VIEWS (CRITICAL ORM QUERIES)
# ==============================================================================

class TopPostsAnalyticsView(APIView):
    """
    GET /api/analytics/top-posts/
    Query 1: Return the top 3 posts with highest number of comments.
    """

    @extend_schema(
        tags=['Analytics'],
        summary="Query 1: Top 3 posts with highest comments",
        description=(
            "Retrieves the top 3 posts with the highest number of comments.\n\n"
            "ORM Implementation:\n"
            "`Post.objects.annotate(total_comments=Count('comments')).order_by('-total_comments', '-created_at', '-id')[:3]`\n\n"
            "- Uses `annotate()` with `Count('comments')`.\n"
            "- Deterministic ordering: `-total_comments`, `-created_at`, `-id`.\n"
            "- Includes posts with zero comments where applicable."
        ),
        responses={200: TopPostSerializer(many=True)},
        examples=[
            OpenApiExample(
                "Top Posts Response",
                value=[
                    {"id": 1, "title": "Advanced Django ORM", "total_comments": 15},
                    {"id": 2, "title": "Building Scalable APIs", "total_comments": 8},
                    {"id": 3, "title": "Python Performance Tuning", "total_comments": 4}
                ],
                response_only=True
            )
        ]
    )
    def get(self, request):
        posts = get_top_three_posts()
        serializer = TopPostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MostActiveUserAnalyticsView(APIView):
    """
    GET /api/analytics/most-active-user/
    Query 3: Return the user who has written the highest number of comments.
    """

    @extend_schema(
        tags=['Analytics'],
        summary="Query 3: Most active user",
        description=(
            "Retrieves the single user who has written the highest number of comments.\n\n"
            "ORM Implementation:\n"
            "`User.objects.annotate(total_comments=Count('comments')).order_by('-total_comments', 'id').first()`\n\n"
            "- Uses aggregation via `annotate()` and `Count()`.\n"
            "- Deterministic tie-breaking using user ID.\n"
            "- Gracefully handles empty database state when no comments exist."
        ),
        responses={
            200: inline_serializer(
                name="MostActiveUserResponse",
                fields={
                    "id": serializers.IntegerField(allow_null=True),
                    "name": serializers.CharField(allow_null=True),
                    "email": serializers.EmailField(allow_null=True),
                    "total_comments": serializers.IntegerField(allow_null=True),
                    "detail": serializers.CharField(required=False),
                }
            )
        },
        examples=[
            OpenApiExample(
                "Active User Found",
                value={
                    "id": 2,
                    "name": "Jane Commenter",
                    "email": "jane@example.com",
                    "total_comments": 12
                },
                response_only=True
            ),
            OpenApiExample(
                "No Comments Written Yet",
                value={
                    "detail": "No comments have been written yet.",
                    "user": None
                },
                response_only=True
            )
        ]
    )
    def get(self, request):
        user = get_most_active_user()
        if not user:
            return Response(
                {
                    "detail": "No comments have been written yet.",
                    "user": None
                },
                status=status.HTTP_200_OK
            )

        serializer = ActiveUserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ActiveUsersAnalyticsView(APIView):
    """
    GET /api/analytics/active-users/
    Query 2: Return users who have written more than 3 comments.
    """

    @extend_schema(
        tags=['Analytics'],
        summary="Query 2: Users with more than 3 comments",
        description=(
            "Retrieves all users who have written more than 3 comments across all posts.\n\n"
            "ORM Implementation:\n"
            "`User.objects.annotate(total_comments=Count('comments')).filter(total_comments__gt=3).order_by('-total_comments', 'id')`\n\n"
            "- Uses `annotate()` and `Count()`.\n"
            "- Filters using `total_comments__gt=3`.\n"
            "- Deterministic ordering by comment count descending, then user ID."
        ),
        responses={200: ActiveUserSerializer(many=True)},
        examples=[
            OpenApiExample(
                "Active Users Response",
                value=[
                    {"id": 2, "name": "Jane Commenter", "email": "jane@example.com", "total_comments": 12},
                    {"id": 5, "name": "Alex Tech", "email": "alex@example.com", "total_comments": 4}
                ],
                response_only=True
            )
        ]
    )
    def get(self, request):
        users = get_users_with_more_than_three_comments()
        serializer = ActiveUserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

