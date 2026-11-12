# Mini Blog Platform REST API

> Technical Hiring Assessment for **Python/Django Developer** at **NovuLabs**.  
> Built with Django 5+, Django REST Framework, SQLite, and drf-spectacular.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Technology Stack](#2-technology-stack)
3. [Key Features](#3-key-features)
4. [Project Architecture & Directory Structure](#4-project-architecture--directory-structure)
5. [Prerequisites & System Requirements](#5-prerequisites--system-requirements)
6. [Local Setup & Installation](#6-local-setup--installation)
   - [Virtual Environment Setup](#virtual-environment-setup)
   - [Dependency Installation](#dependency-installation)
   - [Environment Configuration](#environment-configuration)
   - [Database Migrations](#database-migrations)
   - [Superuser Creation](#superuser-creation)
   - [Sample Data Seeding](#sample-data-seeding)
   - [Starting the Development Server](#starting-the-development-server)
7. [API Documentation (Swagger & ReDoc)](#7-api-documentation-swagger--redoc)
8. [Complete API Endpoints Table](#8-complete-api-endpoints-table)
9. [API Request & Response Examples](#9-api-request--response-examples)
10. [Critical Django ORM Queries & Deep Dive](#10-critical-django-orm-queries--deep-dive)
11. [Query Optimization & Anti-N+1 Strategy](#11-query-optimization--anti-n1-strategy)
12. [Automated Testing Suite](#12-automated-testing-suite)
13. [Production Deployment Guide](#13-production-deployment-guide)
    - [PythonAnywhere Deployment](#pythonanywhere-deployment-persistent-sqlite)
    - [Render Deployment](#render-deployment)
    - [SQLite Storage Considerations](#sqlite-storage-considerations-on-free-tiers)
14. [Live Deployment URL](#14-live-deployment-url)
15. [GitHub Publication Readiness](#15-github-publication-readiness)

---

## 1. Project Overview

The **Mini Blog Platform REST API** is an enterprise-grade backend service enabling users to create and manage blog posts, engage with threaded comments, and compute advanced aggregation metrics through optimized Django ORM queries. 

Designed strictly to fulfill all criteria of the NovuLabs technical hiring assessment, this project emphasizes:
- Clean modular design adhering to standard Django conventions.
- Explicit query optimization preventing N+1 database queries.
- Complete OpenAPI 3.0 (Swagger/ReDoc) interactive documentation.
- Robust validation and deterministic sorting logic.
- Production-readiness with 100% test pass rates across unit and integration tests.

---

## 2. Technology Stack

- **Language:** Python 3.10+ (tested on Python 3.14)
- **Framework:** Django 5.1+ / 6.1
- **API Toolkit:** Django REST Framework (DRF) 3.18+
- **OpenAPI & Swagger:** `drf-spectacular` 0.30+
- **Database:** SQLite 3 (configured with composite indexing)
- **Static Asset Serving:** WhiteNoise 6.12+
- **Environment Management:** `python-dotenv`
- **WSGI / Production Server:** Gunicorn (Linux/Cloud) / WSGI

---

## 3. Key Features

- **Custom Authentication & User Model:** Extends `AbstractUser` with unique email constraints, custom display names, and secure password hashing.
- **Blog Post Management:** Pagination, author relation, and dynamically computed comment counts.
- **Comment System:** Nested commenting under posts with single-query join optimizations.
- **Advanced Django ORM Analytics:**
  - Query 1: Top 3 posts ranked by comment volume (with zero-comment handling).
  - Query 2: Active users who authored more than 3 comments (`total_comments__gt=3`).
  - Query 3: System-wide most active user with deterministic tie-breaking and empty-database resilience.
  - Query 4: Post comments sorted newest-first with `select_related('user')` single-query JOIN.
- **Interactive Documentation:** Live Swagger UI and ReDoc endpoints with schema validation and example payloads.
- **Automated Test Suite:** 23 exhaustive test cases validating CRUD, constraints, query counts (`assertNumQueries`), and boundary conditions.
- **Sample Data Generator:** Custom management command (`python manage.py seed_data`) for instant testing.

---

## 4. Project Architecture & Directory Structure

```
DJANGO_HIRING_TASK/
│
├── config/                         # Django project core configuration
│   ├── __init__.py
│   ├── settings.py                 # Environment-aware settings (WhiteNoise, DRF, Spectacular)
│   ├── urls.py                     # Root URL routing + Swagger/ReDoc endpoints
│   ├── wsgi.py                     # WSGI entrypoint for production servers
│   └── asgi.py                     # ASGI entrypoint
│
├── blog/                           # Core blog application
│   ├── migrations/                 # Schema migrations
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── management/
│   │   └── commands/
│   │       ├── __init__.py
│   │       └── seed_data.py        # Custom database seeding command
│   ├── __init__.py
│   ├── admin.py                    # Django Admin with optimized querysets
│   ├── apps.py                     # App configuration
│   ├── models.py                   # User, Post, and Comment models with indexes
│   ├── pagination.py               # Custom standard pagination
│   ├── queries.py                  # Assessment ORM queries (Query 1 - 4)
│   ├── serializers.py              # Model serializers with validation rules
│   ├── tests.py                    # 23 automated unit and integration tests
│   ├── urls.py                     # App-level routing
│   └── views.py                    # API Views annotated with OpenAPI schemas
│
├── manage.py                       # Django CLI management script
├── requirements.txt                # Production dependency specification
├── render.yaml                     # Render deployment blueprint
├── Procfile                        # Heroku/Render process declaration
├── .env.example                    # Environment variable template
├── .gitignore                      # Git exclusion rules (venv, db.sqlite3, secrets)
└── README.md                       # Comprehensive project documentation
```

---

## 5. Prerequisites & System Requirements

- Python 3.10, 3.11, 3.12, 3.13, or 3.14
- Git
- SQLite3 (bundled with standard Python installations)

---

## 6. Local Setup & Installation

### Virtual Environment Setup

Clone or open the repository workspace and create a virtual environment:

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

### Dependency Installation

Install the required packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Environment Configuration

Create a `.env` file based on the provided `.env.example`:

```bash
# macOS/Linux
cp .env.example .env

# Windows (PowerShell)
Copy-Item .env.example .env
```

Review `.env`:
```env
SECRET_KEY=django-insecure-mini-blog-dev-secret-key-change-in-production-123456
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
```

### Database Migrations

Apply the database migrations to set up the SQLite schema:

```bash
python manage.py migrate
```

### Superuser Creation

To access the Django Admin panel (`/admin/`):

```bash
python manage.py createsuperuser
```

Follow the prompts to enter an email, username, and password.

### Sample Data Seeding

Run the custom seed command to automatically populate the database with realistic sample users, blog posts, and comments:

```bash
python manage.py seed_data
```

*Output:*
```text
Seeding sample data for Mini Blog Platform...
Successfully seeded database:
- 6 Users
- 5 Posts
- 12 Comments
```

### Starting the Development Server

Start the local server:

```bash
python manage.py runserver
```

The application will be accessible at:
- Root Redirect (to Swagger UI): `http://127.0.0.1:8000/`
- Swagger UI Documentation: `http://127.0.0.1:8000/api/docs/`
- ReDoc Documentation: `http://127.0.0.1:8000/api/redoc/`
- OpenAPI Raw Schema: `http://127.0.0.1:8000/api/schema/`
- Django Admin Portal: `http://127.0.0.1:8000/admin/`

---

## 7. API Documentation (Swagger & ReDoc)

Interactive API documentation is generated using `drf-spectacular` adhering to the **OpenAPI 3.0** standard:

| Documentation Interface | URL | Description |
| :--- | :--- | :--- |
| **Swagger UI** | `http://127.0.0.1:8000/api/docs/` | Interactive API explorer to execute live requests |
| **ReDoc** | `http://127.0.0.1:8000/api/redoc/` | Clean, 3-column reference documentation |
| **OpenAPI 3.0 Schema** | `http://127.0.0.1:8000/api/schema/` | Raw YAML / JSON schema specification |

---

## 8. Complete API Endpoints Table

| Method | Endpoint | Description | Query / Body Params | Status Codes |
| :--- | :--- | :--- | :--- | :--- |
| **POST** | `/api/posts/` | Create a new blog post | `title`, `content`, `user_id` | `201 Created`, `400 Bad Request` |
| **GET** | `/api/posts/` | List all blog posts (paginated) | `page`, `page_size` | `200 OK` |
| **GET** | `/api/posts/{id}/` | Retrieve single post details | Path: `{id}` | `200 OK`, `404 Not Found` |
| **POST** | `/api/posts/{id}/comments/` | Post a comment on a blog post | `user_id`, `comment_text` | `201 Created`, `400 Bad Request`, `404 Not Found` |
| **GET** | `/api/posts/{id}/comments/` | List comments for a post (Query 4) | Path: `{id}`, `page`, `page_size` | `200 OK`, `404 Not Found` |
| **GET** | `/api/analytics/top-posts/` | Top 3 posts by comments (Query 1) | None | `200 OK` |
| **GET** | `/api/analytics/most-active-user/`| Most active commenter (Query 3) | None | `200 OK` |
| **GET** | `/api/analytics/active-users/` | Users with > 3 comments (Query 2)| None | `200 OK` |
| **POST** | `/api/users/` | Register a new user | `name`, `email`, `password` | `201 Created`, `400 Bad Request` |
| **GET** | `/api/users/` | List users (paginated) | `page`, `page_size` | `200 OK` |
| **GET** | `/api/users/{id}/` | Retrieve user details | Path: `{id}` | `200 OK`, `404 Not Found` |

---

## 9. API Request & Response Examples

### 1. Create a Post (`POST /api/posts/`)

**Request Payload:**
```json
{
  "title": "Mastering Django ORM Query Optimization",
  "content": "A comprehensive analysis of annotate, Count, and select_related techniques.",
  "user_id": 1
}
```

**Response (`201 Created`):**
```json
{
  "id": 1,
  "title": "Mastering Django ORM Query Optimization",
  "content": "A comprehensive analysis of annotate, Count, and select_related techniques.",
  "author": {
    "id": 1,
    "name": "Alice Johnson",
    "email": "alice@example.com"
  },
  "comment_count": 0,
  "created_at": "2026-11-12T13:00:00.123456Z"
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
      "created_at": "2026-11-12T13:00:04.730000Z"
    },
    {
      "id": 2,
      "title": "Building High-Throughput REST APIs with DRF",
      "content": "A comprehensive guide to serializers, pagination, and viewsets.",
      "author": {
        "id": 2,
        "name": "Bob Smith",
        "email": "bob@example.com"
      },
      "comment_count": 4,
      "created_at": "2026-11-12T13:00:04.732000Z"
    }
  ]
}
```

---

### 3. Add a Comment (`POST /api/posts/1/comments/`)

**Request Payload:**
```json
{
  "user_id": 2,
  "comment_text": "This explanation of select_related is clear and concise!"
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
  "comment_text": "This explanation of select_related is clear and concise!",
  "created_at": "2026-11-12T13:05:00.000000Z"
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
      "created_at": "2026-11-12T13:00:04.778312Z"
    },
    {
      "id": 4,
      "post_id": 1,
      "commenter_name": "Diana Prince",
      "author": {
        "id": 4,
        "name": "Diana Prince",
        "email": "diana@example.com"
      },
      "comment_text": "Count() with annotate is so clean.",
      "created_at": "2026-11-12T13:00:04.769951Z"
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

**Response (`200 OK`):**
```json
{
  "id": 2,
  "name": "Bob Smith",
  "email": "bob@example.com",
  "total_comments": 5
}
```

*(If no comments exist in the system, returns `{"detail": "No comments have been written yet.", "user": null}` with HTTP 200).*

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

## 10. Critical Django ORM Queries & Deep Dive

The four required queries are encapsulated in `blog/queries.py` and strictly utilize the Django ORM without raw SQL.

### Query 1: Top 3 Posts With Highest Number of Comments

```python
def get_top_three_posts():
    return Post.objects.annotate(
        total_comments=Count('comments')
    ).order_by('-total_comments', '-created_at', '-id')[:3]
```

**Technical Explanation:**
- `annotate(total_comments=Count('comments'))`: Performs a `LEFT OUTER JOIN` against the `blog_comment` table and computes an SQL aggregate `COUNT("blog_comment"."id") GROUP BY "blog_post"."id"`. Because a `LEFT OUTER JOIN` is used, posts with zero comments correctly evaluate to `total_comments = 0`.
- Deterministic Ordering: `-total_comments` ranks highest counts first. `-created_at` and `-id` provide stable, repeatable tie-breaking when two posts possess identical comment counts.
- `[:3]`: Translates to SQL `LIMIT 3`.

---

### Query 2: Users Who Have Written More Than 3 Comments

```python
def get_users_with_more_than_three_comments():
    return User.objects.annotate(
        total_comments=Count('comments')
    ).filter(
        total_comments__gt=3
    ).order_by('-total_comments', 'id')
```

**Technical Explanation:**
- `Count('comments')`: Traverses the reverse foreign key `related_name='comments'` from `User` to `Comment`.
- `filter(total_comments__gt=3)`: Because `filter()` is applied after `annotate()`, Django generates an SQL `HAVING COUNT("blog_comment"."id") > 3` clause, performing the filtering in the database engine rather than in Python memory.
- `order_by('-total_comments', 'id')`: Orders the most prolific commenters first, breaking ties deterministically by `id ASC`.

---

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

**Technical Explanation:**
- Aggregation & Ordering: Users are annotated with comment counts and ordered by `-total_comments, id`.
- `.first()`: Appends `LIMIT 1` in SQL and returns either the model instance or `None`.
- Resilience to Empty Data: If no users exist, or if all users have 0 comments, the function returns `None`. The API view inspects this and responds gracefully with HTTP 200 and an explicit notification rather than falsely reporting an inactive user or throwing an unhandled exception.

---

### Query 4: Fetch All Comments For a Given Post

```python
def get_comments_for_post(post_id):
    post = get_object_or_404(Post, id=post_id)
    return Comment.objects.filter(post=post).select_related('user').order_by('-created_at', '-id')
```

**Technical Explanation:**
- `get_object_or_404(Post, id=post_id)`: Guarantees post existence, immediately raising an `Http404` for invalid or nonexistent IDs.
- `select_related('user')`: Performs an SQL `INNER JOIN` with the `blog_user` table. Commenter details (`comment.user.name`, `comment.user.email`) are retrieved in the initial query, eliminating the N+1 query vulnerability when iterating through comments.
- `order_by('-created_at', '-id')`: Enforces reverse chronological ordering (newest comments first).

---

## 11. Query Optimization & Anti-N+1 Strategy

| Optimization Technique | Where Applied | Impact |
| :--- | :--- | :--- |
| **`select_related('user')`** | `PostListCreateView`, `PostDetailView`, `CommentListCreateView` | Eliminates N+1 queries by joining author/user tables into a single SQL statement. |
| **`annotate(comment_count=Count('comments'))`** | `PostListCreateView`, `PostDetailView` | Computes comment counts directly at the database level in a single query rather than firing `len(post.comments.all())` in Python. |
| **Database Indexing** | `models.Index` on `['-created_at', '-id']`, `['post', '-created_at']`, `['user', '-created_at']` | Optimizes sorting and filtering on high-volume read queries. |
| **Pagination** | `StandardResultsSetPagination` (Page size = 10, max = 100) | Prevents runaway memory consumption and unconstrained table scans. |
| **`assertNumQueries` Test Verification** | `blog/tests.py` | Automated tests verify that accessing comments for a post executes exactly 1 query to fetch post + 1 joined query for comments, regardless of comment count. |

---

## 12. Automated Testing Suite

The project includes **23 automated tests** written with DRF `APITestCase`.

### Running the Test Suite

```bash
# Run tests with standard verbosity
python manage.py test blog

# Run tests with detailed verbosity
python manage.py test blog -v 2
```

### Test Suite Coverage Breakdown

```text
Found 23 test(s).
- AnalyticsApiTests:
  [x] test_query1_top_three_posts (Annotate + Count descending)
  [x] test_query1_includes_zero_comments_when_applicable (Zero-comment handling)
  [x] test_query2_users_with_more_than_three_comments (HAVING count > 3)
  [x] test_query2_boundary_exactly_three_comments_excluded (Boundary check at 3)
  [x] test_query3_most_active_user (Deterministic tie-breaking)
  [x] test_query3_most_active_user_no_comments_exist (Empty system resilience)
  [x] test_query4_select_related_optimization (assertNumQueries verify anti-N+1)

- PostApiTests:
  [x] test_create_post_success
  [x] test_create_post_invalid_user_id (400 validation error)
  [x] test_create_post_empty_title_and_content (Validation rules)
  [x] test_list_posts_includes_author_and_comment_count (select_related + annotate)
  [x] test_get_single_post_success
  [x] test_get_single_post_not_found (404 error)

- CommentApiTests:
  [x] test_create_comment_success
  [x] test_create_comment_invalid_post_id (404 error)
  [x] test_create_comment_invalid_user_id (400 error)
  [x] test_create_comment_empty_text_fails (400 error)
  [x] test_list_comments_newest_first_and_query_optimization
  [x] test_list_comments_nonexistent_post_returns_404

- UserApiTests:
  [x] test_create_user_success (Secure password hashing)
  [x] test_create_user_duplicate_email_fails (Unique email constraint)
  [x] test_create_user_blank_name_fails
  [x] test_list_users (Pagination check)

----------------------------------------------------------------------
Ran 23 tests
OK
```

---

## 13. Production Deployment Guide

The project is structured to deploy smoothly to platforms with free-tier hosting such as **PythonAnywhere** or **Render**.

### PythonAnywhere Deployment (Persistent SQLite)

PythonAnywhere provides persistent local disk storage on its free tier, making it well-suited for retaining SQLite database records across web app reloads.

1. **Create Account:** Register at [PythonAnywhere](https://www.pythonanywhere.com/).
2. **Open Bash Console & Clone:**
   ```bash
   git clone <YOUR_GITHUB_REPO_URL> mini_blog_api
   cd mini_blog_api
   ```
3. **Set Up Virtual Environment:**
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 mini-blog-env
   pip install -r requirements.txt
   ```
4. **Configure Environment:**
   Create `.env`:
   ```bash
   nano .env
   ```
   Add:
   ```env
   SECRET_KEY=production-secret-key-replace-me
   DEBUG=False
   ALLOWED_HOSTS=<your-username>.pythonanywhere.com
   ```
5. **Run Migrations & Collect Static:**
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py seed_data
   ```
6. **Configure Web Tab:**
   - Go to the **Web** tab in PythonAnywhere dashboard.
   - Set **Source Code**: `/home/<username>/mini_blog_api`
   - Set **Working Directory**: `/home/<username>/mini_blog_api`
   - Set **Virtualenv**: `/home/<username>/.virtualenvs/mini-blog-env`
   - Edit **WSGI configuration file**:
     ```python
     import os
     import sys
     from dotenv import load_dotenv

     path = '/home/<username>/mini_blog_api'
     if path not in sys.path:
         sys.path.append(path)

     load_dotenv(os.path.join(path, '.env'))

     os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

     from django.core.wsgi import get_wsgi_application
     application = get_wsgi_application()
     ```
7. Click **Reload <username>.pythonanywhere.com**.

---

### Render Deployment

A ready-to-use [`render.yaml`](file:///c:/Users/Ali/Documents/DJANGO_HIRING_TASK/render.yaml) and [`Procfile`](file:///c:/Users/Ali/Documents/DJANGO_HIRING_TASK/Procfile) are included in the repository.

1. Connect your GitHub repository to [Render](https://render.com/).
2. Create a **New Web Service** pointing to the repository.
3. Configure settings:
   - **Environment:** `Python`
   - **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command:** `gunicorn config.wsgi:application`
4. Set Environment Variables:
   - `DEBUG`: `False`
   - `SECRET_KEY`: *(Auto-generated)*
   - `ALLOWED_HOSTS`: `.onrender.com`

---

### SQLite Storage Considerations on Free Tiers

> [!WARNING]
> **Ephemeral Disk Notice on Render Free Tier:**  
> Render's free tier uses ephemeral container instances. Any modifications written to `db.sqlite3` will reset when the instance restarts or spins down due to inactivity.  
> - For a **persistent SQLite database** on a free tier, **PythonAnywhere** is recommended because it allocates persistent filesystem storage.  
> - Alternatively, for persistent cloud deployments on Render, attaching a Render Persistent Disk or switching to a managed PostgreSQL service (e.g., Supabase / Neon / Render Postgres) would be standard for production environments outside the strict SQLite hiring assignment constraint.

---

## 14. Live Deployment URL

- **Status:** Deployment Prepared (Production-ready configuration in place)
- **Deployment Platform:** Ready for Render / PythonAnywhere
- **Live Demo URL:** `https://mini-blog-api-placeholder.onrender.com` *(Pending remote host deployment by repository owner)*
- **Local Interactive URL:** `http://127.0.0.1:8000/api/docs/`

---

## 15. GitHub Publication Readiness

- Repository structure: Clean and modular.
- Secrets: No production keys or credentials committed (`.gitignore` protects `.env` and `db.sqlite3`).
- Documentation: Complete API reference and ORM architectural rationale.
- Git Status: Local repository initialized; ready to push to GitHub when authorized.
