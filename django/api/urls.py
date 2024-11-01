"""
URL configuration for the Rag N Chat API.

This module defines the URL patterns for the API endpoints:
- /api/ping/ (POST):   Accepts text strings and returns both original and reversed versions
                     Handles input validation and error responses
                     Maximum text length: 1024 characters

- /api/vectorize/ (POST): Vectorizes GitHub repository contents and stores them in Pinecone
                       Accepts repository name in 'owner/repo' format
                       Processes .md and .py files
                       Returns success status and number of processed files
                       Handles invalid inputs and processing errors
"""

from django.urls import path
from . import views

urlpatterns = [
    path('ping/', views.ping, name='ping'),
    path('vectorize/', views.vectorize_repository, name='vectorize_repository'),
]
