# Mini Blog REST API

A Django REST Framework backend for a mini blog platform where users can publish posts, leave comments, and query blog analytics.

This project was built for the NovuLabs Python/Django technical assessment, focusing on clean REST API design, efficient Django ORM queries, OpenAPI documentation, and automated testing.

---

## Table of Contents

1. [Overview](#overview)
2. [Tech Stack](#tech-stack)
3. [Features](#features)
4. [Project Structure](#project-structure)
5. [Local Setup & Installation](#local-setup--installation)
6. [API Documentation (Swagger & ReDoc)](#api-documentation-swagger--redoc)
7. [API Endpoints Reference](#api-endpoints-reference)
8. [Sample Requests and Responses](#sample-requests-and-responses)
9. [Django ORM Queries](#django-orm-queries)
10. [Query Optimization & N+1 Prevention](#query-optimization--n1-prevention)
11. [Pagination Behavior](#pagination-behavior)
12. [Automated Testing](#automated-testing)
13. [Deployment Guide](#deployment-guide)

---

## Overview

The application provides a RESTful API for managing blog posts and comments. Key design considerations include:
- A custom User model extending `AbstractUser` with unique email authentication and standard Django password validation.
- Clean separation between models, serializers, views, and ORM query helpers.
- Defensive query design to eliminate N+1 database queries through `select_related` and database-level aggregations (`annotate`, `Count`).
- Accurate OpenAPI 3.0 schema generation using `drf-spectacular`.

---

## Tech Stack

- **Python:** 3.10+
- **Django:** 5.1+ / 6.1
- **Django REST Framework (DRF):** 3.18+
- **drf-spectacular:** 0.30+ (OpenAPI 3.0, Swagger UI, ReDoc)
- **Database:** SQLite 3
- **Static Assets:** WhiteNoise 6.12+
- **WSGI Server:** Gunicorn (production) / Django runserver (development)

---

## Features

- **User Accounts:** Registration with unique email validation, display name, and Django password policy enforcement.
- **Post Management:** Create, list, and retrieve posts with embedded author details and dynamic comment counts.
- **Nested Comments:** Add and list comments under posts, ordered newest first.
- **Analytics Queries:**
  - Query 1: Top 3 posts ranked by comment count (handles ties and zero comments).
  - Query 2: Users who have written more than 3 comments.
  - Query 3: Most active user overall (with deterministic tie-breaking and empty-database handling).
  - Query 4: Retrieve all comments for a post in a single optimized SQL join.
- **Data Seeder:** Management command (`python manage.py seed_data`) to populate mock data for testing and demonstration.

---

## Project Structure

```
DJANGO_HIRING_TASK/
├── config/
│   ├── __init__.py
│   ├── settings.py         # Environment-aware settings
│   ├── urls.py             # Root routing + Swagger/ReDoc
│   ├── wsgi.py             # WSGI entrypoint for production
│   └── asgi.py             # ASGI entrypoint
├── blog/
│   ├── migrations/         # Database migrations
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py # Sample data generator
│   ├── admin.py            # Django Admin configuration
│   ├── apps.py             # App configuration
│   ├── models.py           # Custom User, Post, Comment models
│   ├── pagination.py       # Standard pagination class
│   ├── queries.py          # Dedicated ORM query service functions
│   ├── serializers.py      # DRF serializers and validation
│   ├── tests.py            # 31 automated tests
│   ├── urls.py             # API route definitions
│   └── views.py            # API views with OpenAPI schemas
├── manage.py
├── requirements.txt        # Project dependencies
├── render.yaml             # Render deployment blueprint
├── Procfile                # Gunicorn process definition
├── .env.example            # Environment variables template
├── .gitignore
└── README.md
```

---

## Local Setup & Installation

### 1. Prerequisites
- Python 3.10 or higher
- Git

### 2. Clone the Repository & Set Up Virtual Environment

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Windows (Command Prompt)
.\venv\Scripts\activate.bat
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
# macOS/Linux
cp .env.example .env

# Windows
copy .env.example .env
```

Review `.env`:
```env
SECRET_KEY=django-insecure-mini-blog-dev-secret-key-change-in-production-123456
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

> In development (`DEBUG=True`), a default fallback secret key is permitted. In production (`DEBUG=False`), `SECRET_KEY` must be explicitly provided in the environment.

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Create Superuser (for Django Admin)

```bash
python manage.py createsuperuser
```

### 7. Seed Sample Data

To populate the database with users, posts, and comments for testing all endpoints and ORM queries:

```bash
python manage.py seed_data
```

### 8. Start Development Server

```bash
python manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`.  and live url is `http://34.239.247.1/`

---

## API Documentation (Swagger & ReDoc)

Once the server is running, interactive API documentation is available at:

- **Swagger UI:** `http://34.239.247.1/api/docs/`

- **Raw OpenAPI Schema:** `http://34.239.247.1/api/schema/`
- The root URL (`/`) automatically redirects to Swagger UI (`/api/docs/`).

---

## API Endpoints Reference

| Method | Endpoint | Description | Request Body | Status Codes |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/posts/` | Create a new blog post | `title`, `content`, `user_id` | `201`, `400` |
| `GET` | `/api/posts/` | List posts (paginated) | Query: `page`, `page_size` | `200` |
| `GET` | `/api/posts/{id}/` | Retrieve single post | None | `200`, `404` |
| `POST` | `/api/posts/{id}/comments/` | Post a comment on a post | `user_id`, `comment_text` | `201`, `400`, `404` |
| `GET` | `/api/posts/{id}/comments/` | List comments for post (Query 4) | Query: `page`, `page_size` | `200`, `404` |
| `GET` | `/api/analytics/top-posts/` | Top 3 posts by comments (Query 1) | None | `200` |
| `GET` | `/api/analytics/most-active-user/` | Most active commenter (Query 3) | None | `200` |
| `GET` | `/api/analytics/active-users/` | Users with > 3 comments (Query 2) | None | `200` |
| `POST` | `/api/users/` | Register new user | `name`, `email`, `password` | `201`, `400` |
| `GET` | `/api/users/` | List users (paginated) | Query: `page`, `page_size` | `200` |
| `GET` | `/api/users/{id}/` | Retrieve user details | None | `200`, `404` |

---

## Sample Requests and Responses

### 1. Create a Post (`POST /api/posts/`)

**Request:**
```json
{
  "title": "Understanding Django ORM Annotations",
  "content": "A breakdown of annotate and Count for API developers.",
  "user_id": 1
}
```

**Response (`201 Created`):**
```json
{
  "id": 1,
  "title": "Understanding Django ORM Annotations",
  "content": "A breakdown of annotate and Count for API developers.",
  "author": {
    "id": 1,
    "name": "Alice Johnson",
    "email": "alice@example.com"
  },
  "comment_count": 0,
  "created_at": "2026-11-12T12:00:00Z"
}
```

---

### 2. List Posts (`GET /api/posts/`)

**Response (`200 OK`):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Deep Dive into Django ORM Performance",
      "content": "Discover how annotate(), Count(), and select_related() eliminate N+1 bottlenecks.",
      "author": {
        "id": 1,
        "name": "Alice Johnson",
        "email": "alice@example.com"
      },
      "comment_count": 5,
      "created_at": "2026-11-12T13:00:04Z"
    }
  ]
}
```

---

### 3. Add a Comment (`POST /api/posts/1/comments/`)

**Request:**
```json
{
  "user_id": 2,
  "comment_text": "Great explanation of select_related!"
}
```

**Response (`201 Created`):**
```json
{
  "id": 13,
  "post_id": 1,
  "commenter_name": "Bob Smith",
  "author": {
    "id": 2,
    "name": "Bob Smith",
    "email": "bob@example.com"
  },
  "comment_text": "Great explanation of select_related!",
  "created_at": "2026-11-12T13:05:00Z"
}
```

---

### 4. Fetch Comments for Post 1 (`GET /api/posts/1/comments/`)

**Response (`200 OK`):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 5,
      "post_id": 1,
      "commenter_name": "Evan Wright",
      "author": {
        "id": 5,
        "name": "Evan Wright",
        "email": "evan@example.com"
      },
      "comment_text": "Bookmarked for future reference.",
      "created_at": "2026-11-12T13:00:04Z"
    }
  ]
}
```

---

### 5. Analytics: Top 3 Posts (`GET /api/analytics/top-posts/`)

**Response (`200 OK`):**
```json
[
  {
    "id": 1,
    "title": "Deep Dive into Django ORM Performance",
    "total_comments": 5
  },
  {
    "id": 2,
    "title": "Building High-Throughput REST APIs with DRF",
    "total_comments": 4
  },
  {
    "id": 3,
    "title": "OpenAPI and Swagger Documentation Mastery",
    "total_comments": 2
  }
]
```

---

### 6. Analytics: Most Active User (`GET /api/analytics/most-active-user/`)

**Response (`200 OK` - user found):**
```json
{
  "id": 2,
  "name": "Bob Smith",
  "email": "bob@example.com",
  "total_comments": 5
}
```

**Response (`200 OK` - when no comments exist in the database):**
```json
{
  "detail": "No comments have been written yet.",
  "user": null
}
```

---

### 7. Analytics: Active Users (> 3 comments) (`GET /api/analytics/active-users/`)

**Response (`200 OK`):**
```json
[
  {
    "id": 2,
    "name": "Bob Smith",
    "email": "bob@example.com",
    "total_comments": 5
  },
  {
    "id": 3,
    "name": "Charlie Brown",
    "email": "charlie@example.com",
    "total_comments": 4
  }
]
```

---

## Django ORM Queries

The required ORM operations are isolated in `blog/queries.py`:

### Query 1: Top 3 Posts With Highest Number of Comments
```python
def get_top_three_posts():
    return Post.objects.annotate(
        total_comments=Count('comments')
    ).order_by('-total_comments', '-created_at', '-id')[:3]
```
- Performs a `LEFT OUTER JOIN` against comments so posts with zero comments evaluate to `total_comments = 0`.
- Orders descending by comment count, with `-created_at` and `-id` ensuring deterministic tie-breaking.
- Slices with `[:3]` (`LIMIT 3` in SQL).

### Query 2: Users Who Have Written More Than 3 Comments
```python
def get_users_with_more_than_three_comments():
    return User.objects.annotate(
        total_comments=Count('comments')
    ).filter(
        total_comments__gt=3
    ).order_by('-total_comments', 'id')
```
- Aggregates comments per user and applies `HAVING COUNT("blog_comment"."id") > 3` at the database level.
- Orders descending by total comments, then ascending by `id` for consistent sorting.

### Query 3: Most Active User
```python
def get_most_active_user():
    user = User.objects.annotate(
        total_comments=Count('comments')
    ).order_by('-total_comments', 'id').first()

    if user and user.total_comments > 0:
        return user
    return None
```
- Ranks users by comment count descending with tie-break on `id`.
- Returns `None` if no users exist or no comments exist across the system. The API view returns a structured empty response with HTTP 200.

### Query 4: Fetch All Comments For a Given Post
```python
def get_comments_for_post(post_id):
    post = get_object_or_404(Post, id=post_id)
    return Comment.objects.filter(post=post).select_related('user').order_by('-created_at', '-id')
```
- Validates post existence with `get_object_or_404` (raising `Http404` for invalid IDs).
- Uses `select_related('user')` (`INNER JOIN`) to retrieve commenter details in the same query, eliminating N+1 queries.
- Sorts newest comments first.

---

## Query Optimization & N+1 Prevention

1. **`select_related('user')`:** Applied on post listings, single post retrieval, and comment listings. Joins the user table in the initial query so accessing `post.user.name` or `comment.user.name` requires no extra SQL queries.
2. **`annotate(comment_count=Count('comments'))`:** Computes comment counts in SQL `GROUP BY` rather than evaluating `len(post.comments.all())` in Python.
3. **Composite Database Indexes:**
   - Post: `['-created_at', '-id']` and `['user', '-created_at']`
   - Comment: `['post', '-created_at']` and `['user', '-created_at']`
   Redundant single-column indexes on `created_at` were removed in migration `0002` since the composite indexes already cover leading `created_at` queries.
4. **Query Count Verification:** Tested via `self.assertNumQueries(2)` to verify comment listing executes exactly 1 query to check post existence + 1 query to fetch comments with joined authors.

---

## Pagination Behavior

List endpoints (`/api/posts/`, `/api/posts/{id}/comments/`, `/api/users/`) use standard page-number pagination (`StandardResultsSetPagination`):

- **Default Page Size:** 10
- **Custom Page Size Query Param:** `page_size` (maximum allowed: 100)
- **Response Shape:**
  ```json
  {
    "count": 25,
    "next": "http://34.239.247.1/api/posts/?page=2",
    "previous": null,
    "results": [ ... ]
  }
  ```

---

## Automated Testing

The project includes **31 automated tests** covering user validation, post CRUD, comments, ORM analytics queries, boundary conditions, and query optimization.

### Running Tests

```bash
# Standard test run
python manage.py test blog

# Verbose output
python manage.py test blog -v 2
```

### Test Coverage Highlights

- **User Tests:** Successful registration, duplicate email rejection, blank name rejection, password policy enforcement (Django `validate_password`), password hash verification, pagination.
- **Post Tests:** Creation with `user_id`, missing `user_id` rejection, nonexistent `user_id` rejection, empty title/content rejection, single post retrieval, 404 for nonexistent post, author details & comment count inclusion.
- **Comment Tests:** Comment creation, missing `user_id`, nonexistent `user_id`, nonexistent `post_id` (404), empty comment text rejection, newest-first ordering, pagination.
- **Analytics Tests:** Query 1 top 3 posts, Query 1 zero-comment handling, Query 1 fewer than 3 posts edge case, Query 1 deterministic tie-breaking, Query 2 active users (>3 comments), Query 2 boundary (user with exactly 3 comments excluded), Query 3 most active user, Query 3 equal comment count tie-breaking, Query 3 empty database handling, Query 4 `select_related` query count verification (`assertNumQueries`).

---

