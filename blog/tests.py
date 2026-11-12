"""
Comprehensive Automated Test Suite for Mini Blog Platform API.

Covers:
- Custom User management & validation
- Post CRUD & pagination
- Nested comment creation & listing
- Django ORM analytics queries & tie-breaking
- Error handling, boundary cases & query count optimization
"""

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from blog.models import User, Post, Comment
from blog.queries import (
    get_top_three_posts,
    get_users_with_more_than_three_comments,
    get_most_active_user,
    get_comments_for_post,
)


class BaseTestCase(APITestCase):
    """
    Common setup for API tests with pre-populated users.
    """
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='alice@example.com',
            email='alice@example.com',
            name='Alice Johnson',
            password='Password123!'
        )
        self.user2 = User.objects.create_user(
            username='bob@example.com',
            email='bob@example.com',
            name='Bob Smith',
            password='Password123!'
        )
        self.user3 = User.objects.create_user(
            username='charlie@example.com',
            email='charlie@example.com',
            name='Charlie Brown',
            password='Password123!'
        )


class UserApiTests(BaseTestCase):
    """Tests for User registration and listing."""

    def test_create_user_success(self):
        url = reverse('user-list-create')
        payload = {
            'name': 'Diana Prince',
            'email': 'diana@example.com',
            'password': 'StrongPassword123!'
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Diana Prince')
        self.assertEqual(response.data['email'], 'diana@example.com')
        self.assertNotIn('password', response.data)
        self.assertTrue(User.objects.filter(email='diana@example.com').exists())

    def test_create_user_duplicate_email_fails(self):
        url = reverse('user-list-create')
        payload = {
            'name': 'Alice Copy',
            'email': 'alice@example.com',
            'password': 'Password123!'
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_create_user_blank_name_fails(self):
        url = reverse('user-list-create')
        payload = {
            'name': '   ',
            'email': 'blankname@example.com',
            'password': 'Password123!'
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_list_users(self):
        url = reverse('user-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data['count'], 3)


class PostApiTests(BaseTestCase):
    """Tests for Post CRUD and validation."""

    def test_create_post_success(self):
        url = reverse('post-list-create')
        payload = {
            'title': 'Test Post Title',
            'content': 'This is the test content for the blog post.',
            'user_id': self.user1.id
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], payload['title'])
        self.assertEqual(response.data['content'], payload['content'])
        self.assertEqual(response.data['author']['id'], self.user1.id)
        self.assertEqual(response.data['comment_count'], 0)

    def test_create_post_invalid_user_id(self):
        url = reverse('post-list-create')
        payload = {
            'title': 'Test Post',
            'content': 'Valid content',
            'user_id': 99999  # nonexistent
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('user_id', response.data)

    def test_create_post_empty_title_and_content(self):
        url = reverse('post-list-create')
        payload = {
            'title': '   ',
            'content': '',
            'user_id': self.user1.id
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
        self.assertIn('content', response.data)

    def test_list_posts_includes_author_and_comment_count(self):
        post = Post.objects.create(
            title='Post with Comment',
            content='Some content',
            user=self.user1
        )
        Comment.objects.create(post=post, user=self.user2, comment_text='Great!')

        url = reverse('post-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('results' in response.data)
        first_post = response.data['results'][0]
        self.assertEqual(first_post['comment_count'], 1)
        self.assertEqual(first_post['author']['name'], 'Alice Johnson')

    def test_get_single_post_success(self):
        post = Post.objects.create(
            title='Single Post Test',
            content='Detailed post content.',
            user=self.user1
        )
        url = reverse('post-detail', kwargs={'pk': post.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], post.id)
        self.assertEqual(response.data['title'], 'Single Post Test')
        self.assertEqual(response.data['comment_count'], 0)

    def test_get_single_post_not_found(self):
        url = reverse('post-detail', kwargs={'pk': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)


class CommentApiTests(BaseTestCase):
    """Tests for Comment creation, validation, and listing."""

    def setUp(self):
        super().setUp()
        self.post = Post.objects.create(
            title='Discussion Post',
            content='Content for commenting',
            user=self.user1
        )

    def test_create_comment_success(self):
        url = reverse('post-comment-list-create', kwargs={'pk': self.post.id})
        payload = {
            'user_id': self.user2.id,
            'comment_text': 'This is a thoughtful comment.'
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['comment_text'], payload['comment_text'])
        self.assertEqual(response.data['commenter_name'], self.user2.name)
        self.assertEqual(response.data['post_id'], self.post.id)

    def test_create_comment_invalid_post_id(self):
        url = reverse('post-comment-list-create', kwargs={'pk': 99999})
        payload = {
            'user_id': self.user2.id,
            'comment_text': 'A comment on a nonexistent post.'
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_comment_invalid_user_id(self):
        url = reverse('post-comment-list-create', kwargs={'pk': self.post.id})
        payload = {
            'user_id': 99999,  # Nonexistent user
            'comment_text': 'Valid comment text'
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('user_id', response.data)

    def test_create_comment_empty_text_fails(self):
        url = reverse('post-comment-list-create', kwargs={'pk': self.post.id})
        payload = {
            'user_id': self.user2.id,
            'comment_text': '   '
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('comment_text', response.data)

    def test_list_comments_newest_first_and_query_optimization(self):
        # Create 3 comments
        c1 = Comment.objects.create(post=self.post, user=self.user1, comment_text='First comment')
        c2 = Comment.objects.create(post=self.post, user=self.user2, comment_text='Second comment')
        c3 = Comment.objects.create(post=self.post, user=self.user3, comment_text='Third comment')

        url = reverse('post-comment-list-create', kwargs={'pk': self.post.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 3)

        # Confirm newest first order
        self.assertEqual(results[0]['id'], c3.id)
        self.assertEqual(results[1]['id'], c2.id)
        self.assertEqual(results[2]['id'], c1.id)

        # Check commenter names
        self.assertEqual(results[0]['commenter_name'], self.user3.name)
        self.assertEqual(results[1]['commenter_name'], self.user2.name)

    def test_list_comments_nonexistent_post_returns_404(self):
        url = reverse('post-comment-list-create', kwargs={'pk': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class AnalyticsApiTests(BaseTestCase):
    """Tests for the 4 critical ORM Analytics queries."""

    def setUp(self):
        super().setUp()
        # Create 4 posts
        self.p1 = Post.objects.create(title='Post 1', content='C1', user=self.user1)
        self.p2 = Post.objects.create(title='Post 2', content='C2', user=self.user1)
        self.p3 = Post.objects.create(title='Post 3', content='C3', user=self.user1)
        self.p4 = Post.objects.create(title='Post 4 (Zero Comments)', content='C4', user=self.user1)

        # Comments distribution:
        # Post 1: 5 comments (Bob: 3, Charlie: 2)
        # Post 2: 3 comments (Bob: 2, Charlie: 1)
        # Post 3: 1 comment  (Charlie: 1)
        # Post 4: 0 comments
        #
        # User total comments:
        # Bob: 5 comments
        # Charlie: 4 comments
        # Alice: 0 comments

        for _ in range(3):
            Comment.objects.create(post=self.p1, user=self.user2, comment_text='Bob on P1')
        for _ in range(2):
            Comment.objects.create(post=self.p1, user=self.user3, comment_text='Charlie on P1')

        for _ in range(2):
            Comment.objects.create(post=self.p2, user=self.user2, comment_text='Bob on P2')
        Comment.objects.create(post=self.p2, user=self.user3, comment_text='Charlie on P2')

        Comment.objects.create(post=self.p3, user=self.user3, comment_text='Charlie on P3')

    def test_query1_top_three_posts(self):
        url = reverse('analytics-top-posts')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        self.assertEqual(len(data), 3)

        # Check comment counts and descending order
        self.assertEqual(data[0]['id'], self.p1.id)
        self.assertEqual(data[0]['total_comments'], 5)

        self.assertEqual(data[1]['id'], self.p2.id)
        self.assertEqual(data[1]['total_comments'], 3)

        self.assertEqual(data[2]['id'], self.p3.id)
        self.assertEqual(data[2]['total_comments'], 1)

    def test_query1_includes_zero_comments_when_applicable(self):
        # Clear all comments
        Comment.objects.all().delete()
        url = reverse('analytics-top-posts')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        for post_item in response.data:
            self.assertEqual(post_item['total_comments'], 0)

    def test_query2_users_with_more_than_three_comments(self):
        url = reverse('analytics-active-users')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        # Bob has 5 comments (> 3), Charlie has 4 comments (> 3)
        # Alice has 0 (not included)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['name'], 'Bob Smith')
        self.assertEqual(data[0]['total_comments'], 5)
        self.assertEqual(data[1]['name'], 'Charlie Brown')
        self.assertEqual(data[1]['total_comments'], 4)

    def test_query2_boundary_exactly_three_comments_excluded(self):
        # Create a user with exactly 3 comments
        user_boundary = User.objects.create_user(
            username='boundary@example.com',
            email='boundary@example.com',
            name='Boundary User'
        )
        for _ in range(3):
            Comment.objects.create(post=self.p1, user=user_boundary, comment_text='Boundary comment')

        url = reverse('analytics-active-users')
        response = self.client.get(url)
        user_ids = [u['id'] for u in response.data]
        self.assertNotIn(user_boundary.id, user_ids)

    def test_query3_most_active_user(self):
        url = reverse('analytics-most-active-user')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Bob has 5 comments, Charlie has 4
        self.assertEqual(response.data['id'], self.user2.id)
        self.assertEqual(response.data['name'], 'Bob Smith')
        self.assertEqual(response.data['total_comments'], 5)

    def test_query3_most_active_user_no_comments_exist(self):
        # Clear all comments
        Comment.objects.all().delete()
        url = reverse('analytics-most-active-user')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
        self.assertIsNone(response.data['user'])

    def test_query4_select_related_optimization(self):
        # 1 query to validate post existence + 1 query to fetch all comments with joined users.
        # Without select_related('user'), each comment's user access would trigger an additional query (N+1).
        # With 5 comments, this would be 1 + 1 + 5 = 7 queries.
        # With select_related, exactly 2 queries are executed.
        with self.assertNumQueries(2):
            comments = list(get_comments_for_post(self.p1.id))
            for c in comments:
                _ = c.user.name  # Accessing commenter name does not trigger any extra queries
        self.assertEqual(len(comments), 5)

