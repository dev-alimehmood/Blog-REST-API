"""
Django ORM Queries implementation for NovuLabs Hiring Assessment.

This module encapsulates all four required ORM queries with proper
annotations, counting, deterministic ordering, and relationship optimizations.
"""

from django.db.models import Count
from django.shortcuts import get_object_or_404
from .models import Post, User, Comment


def get_top_three_posts():
    """
    Query 1: Top 3 Posts With Highest Number of Comments.

    - Uses annotate() and Count('comments') to count total comments per post.
    - Handles posts with zero comments (Count() returns 0).
    - Sorts descending by comment count (-total_comments).
    - Uses -created_at and -id as deterministic tie-breakers when comment counts are equal.
    - Slices to the top 3 posts using [:3].
    """
    return Post.objects.annotate(
        total_comments=Count('comments')
    ).order_by('-total_comments', '-created_at', '-id')[:3]


def get_users_with_more_than_three_comments():
    """
    Query 2: Users Who Have Written More Than 3 Comments.

    - Uses annotate() and Count('comments') on the User model.
    - Filters users with total_comments__gt=3.
    - Deterministic ordering: highest comment count first (-total_comments), then id ASC.
    """
    return User.objects.annotate(
        total_comments=Count('comments')
    ).filter(
        total_comments__gt=3
    ).order_by('-total_comments', 'id')


def get_most_active_user():
    """
    Query 3: Most Active User.

    - Returns the user who has written the highest number of comments.
    - Uses annotate() with Count('comments').
    - Sorts descending by total_comments, then id ASC for deterministic tie-breaking.
    - Gracefully handles empty cases: returns None if no users exist or if total_comments == 0.
    """
    user = User.objects.annotate(
        total_comments=Count('comments')
    ).order_by('-total_comments', 'id').first()

    if user and user.total_comments > 0:
        return user
    return None


def get_comments_for_post(post_id):
    """
    Query 4: Fetch All Comments For a Given Post.

    - Retrieves the post or raises Http404 if invalid/nonexistent.
    - Uses select_related('user') to perform an SQL JOIN, fetching commenter details
      in a single query to eliminate the N+1 problem.
    - Sorts newest comments first (-created_at, -id).
    """
    post = get_object_or_404(Post, id=post_id)
    return Comment.objects.filter(post=post).select_related('user').order_by('-created_at', '-id')

