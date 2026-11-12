"""
URL Configuration for Mini Blog API project.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Admin Interface
    path('admin/', admin.site.urls),

    # API Endpoints
    path('api/', include('blog.urls')),

    # Swagger / OpenAPI Schema Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Redirect root to Swagger UI for seamless developer experience
    path('', RedirectView.as_view(url='/api/docs/', permanent=False), name='root-redirect'),
]

