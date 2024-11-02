"""
URL configuration for the Rag N Chat API.

This module defines the URL patterns for the API endpoints:
- /api/ping/ (POST):   Accepts text strings and returns both original and reversed versions
                     Handles input validation and error responses
                     Maximum text length: 1024 characters

- /api/repo/vectorize/ (POST): Vectorizes GitHub repository contents and stores them in Pinecone
                       Accepts repository string in format 'owner/repo/branch' or 'owner/repo'
                       where 'branch' is optional (defaults to 'main')
                       The leading '/' is optional
                       Examples:
                         - 'microsoft/vscode'
                         - '/microsoft/vscode'
                         - 'microsoft/vscode/develop'
                         - '/microsoft/vscode/main'
                       Processes .md and .py files
                       Returns success status and number of processed files
                       Handles invalid inputs and processing errors

- /api/repo/list/ (GET): Lists all repositories (namespaces) stored in the Pinecone database
                    Returns a sorted list of repositories in format 'owner/repo/branch'
                    No input parameters required

- /api/repo/delete/ (DELETE): Deletes all vectors for a repository from the Pinecone database
                       Accepts repository string in format 'owner/repo/branch' or 'owner/repo'
                       where 'branch' is optional (defaults to 'main')
                       The leading '/' is optional
                       Returns success status on completion
                       Returns 404 if repository not found
"""

from django.urls import path
from . import views

urlpatterns = [
    path('ping/', views.ping, name='ping'),
    path('repo/vectorize/', views.vectorize_repository, name='vectorize_repository'),
    path('repo/list/', views.list_repositories, name='list_repositories'),
    path('repo/delete/', views.delete_repository, name='delete_repository'),
]
