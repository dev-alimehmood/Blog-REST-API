"""
URL mappings for the blog application.
"""

from django.urls import path
from .views import (
    UserListCreateView,
    UserDetailView,
    PostListCreateView,
    PostDetailView,
    PostCommentListCreateView,
    TopPostsAnalyticsView,
    MostActiveUserAnalyticsView,
    ActiveUsersAnalyticsView,
)

urlpatterns = [
    # User endpoints (helpers for user management & testing)
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),

    # Posts API
    path('posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),

    # Comments API (nested under posts)
    path('posts/<int:pk>/comments/', PostCommentListCreateView.as_view(), name='post-comment-list-create'),

    # Custom Analytics APIs (ORM assessment queries)
    path('analytics/top-posts/', TopPostsAnalyticsView.as_view(), name='analytics-top-posts'),
    path('analytics/most-active-user/', MostActiveUserAnalyticsView.as_view(), name='analytics-most-active-user'),
    path('analytics/active-users/', ActiveUsersAnalyticsView.as_view(), name='analytics-active-users'),
]

