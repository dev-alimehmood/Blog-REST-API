"""
Management command to populate the database with realistic sample data
for demonstration and verification of all APIs and ORM queries.
"""

from django.core.management.base import BaseCommand
from blog.models import User, Post, Comment


class Command(BaseCommand):
    help = "Populates the database with realistic sample users, posts, and comments."

    def handle(self, *args, **options):
        self.stdout.write("Seeding sample data for Mini Blog Platform...")

        # Clear existing data
        Comment.objects.all().delete()
        Post.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        # Create Users
        users_data = [
            {"username": "alice", "email": "alice@example.com", "name": "Alice Johnson"},
            {"username": "bob", "email": "bob@example.com", "name": "Bob Smith"},
            {"username": "charlie", "email": "charlie@example.com", "name": "Charlie Brown"},
            {"username": "diana", "email": "diana@example.com", "name": "Diana Prince"},
            {"username": "evan", "email": "evan@example.com", "name": "Evan Wright"},
            {"username": "fiona", "email": "fiona@example.com", "name": "Fiona Gallagher"},
        ]

        created_users = {}
        for data in users_data:
            user, created = User.objects.get_or_create(
                email=data["email"],
                defaults={
                    "username": data["username"],
                    "name": data["name"],
                }
            )
            user.set_password("Password123!")
            user.save()
            created_users[data["username"]] = user

        # Create Posts
        posts_data = [
            {
                "id_key": "post_1",
                "title": "Deep Dive into Django ORM Performance",
                "content": "Discover how annotate(), Count(), and select_related() eliminate N+1 bottlenecks.",
                "user": created_users["alice"]
            },
            {
                "id_key": "post_2",
                "title": "Building High-Throughput REST APIs with DRF",
                "content": "A comprehensive guide to serializers, pagination, and viewsets.",
                "user": created_users["bob"]
            },
            {
                "id_key": "post_3",
                "title": "OpenAPI and Swagger Documentation Mastery",
                "content": "Leverage drf-spectacular for rich, interactive OpenAPI 3.0 specifications.",
                "user": created_users["charlie"]
            },
            {
                "id_key": "post_4",
                "title": "Deploying Django Applications Seamlessly",
                "content": "Best practices for containerization, environment variables, and static files.",
                "user": created_users["alice"]
            },
            {
                "id_key": "post_5",
                "title": "Clean Architecture in Python",
                "content": "Structuring maintainable applications with clean boundaries and test coverage.",
                "user": created_users["diana"]
            },
        ]

        created_posts = {}
        for p in posts_data:
            post = Post.objects.create(
                title=p["title"],
                content=p["content"],
                user=p["user"]
            )
            created_posts[p["id_key"]] = post

        # Create Comments
        # Distribution:
        # Post 1: 5 comments
        # Post 2: 4 comments
        # Post 3: 2 comments
        # Post 4: 1 comment
        # Post 5: 0 comments
        #
        # User comment counts:
        # Bob: 5 comments (> 3 -> Active user, and Most Active User)
        # Charlie: 4 comments (> 3 -> Active user)
        # Diana: 2 comments
        # Evan: 1 comment
        # Alice: 0 comments
        # Fiona: 0 comments

        comments_data = [
            # Post 1 comments (5 comments)
            (created_posts["post_1"], created_users["bob"], "Fantastic overview of Django ORM!"),
            (created_posts["post_1"], created_users["bob"], "Especially loved the explanation of select_related."),
            (created_posts["post_1"], created_users["charlie"], "Really helpful examples, thank you!"),
            (created_posts["post_1"], created_users["diana"], "Count() with annotate is so clean."),
            (created_posts["post_1"], created_users["evan"], "Bookmarked for future reference."),

            # Post 2 comments (4 comments)
            (created_posts["post_2"], created_users["bob"], "DRF pagination is so easy to configure."),
            (created_posts["post_2"], created_users["charlie"], "Great post on serializer validation rules."),
            (created_posts["post_2"], created_users["charlie"], "Could you cover generic views next?"),
            (created_posts["post_2"], created_users["bob"], "Looking forward to part 2!"),

            # Post 3 comments (2 comments)
            (created_posts["post_3"], created_users["bob"], "drf-spectacular works like a charm."),
            (created_posts["post_3"], created_users["charlie"], "Swagger UI makes testing endpoints a breeze."),

            # Post 4 comments (1 comment)
            (created_posts["post_4"], created_users["diana"], "WhiteNoise made static file hosting trivial."),
        ]

        for post, user, text in comments_data:
            Comment.objects.create(
                post=post,
                user=user,
                comment_text=text
            )

        self.stdout.write(self.style.SUCCESS(
            f"Successfully seeded database:\n"
            f"- {User.objects.count()} Users\n"
            f"- {Post.objects.count()} Posts\n"
            f"- {Comment.objects.count()} Comments"
        ))

