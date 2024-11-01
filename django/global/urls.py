"""
Main URL configuration for the Rag N Chat API project.

This module defines the root URL patterns:
- /admin/: Django admin interface for site administration
- /api/: Rag N Chat API endpoints
    - /api/ping/ (POST): Proof of life
        - Accepts text strings up to 1024 characters
        - Returns original and reversed versions
        - Provides error handling for invalid inputs

See api.urls for detailed API endpoint documentation.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
