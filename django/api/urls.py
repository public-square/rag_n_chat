"""
URL configuration for the Rag N Chat API.

This module defines the URL patterns for the string reversal API endpoints:
- /api/ping/ (POST):   Accepts text strings and returns both original and reversed versions
                       Handles input validation and error responses
                       Maximum text length: 1024 characters
"""

from django.urls import path
from . import views

urlpatterns = [
    path('ping/', views.ping, name='ping'),
]
