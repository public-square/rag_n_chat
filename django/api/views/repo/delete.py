from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from pinecone import Pinecone
import os

pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index(os.getenv('PINECONE_INDEX'))

def parse_repository_string(repo_string):
    """
    Parse a repository string in the format '/owner/repo/branch' or 'owner/repo/branch'.
    Returns tuple of (owner, repo, branch).
    If branch is not specified, returns 'main' as default.
    Raises ValueError if the format is invalid.
    """
    # Remove leading slash if present
    repo_string = repo_string.lstrip('/')

    # Split the string into parts
    parts = repo_string.split('/')

    if len(parts) < 2 or len(parts) > 3:
        raise ValueError('Repository string must be in format "owner/repo" or "owner/repo/branch"')

    owner = parts[0]
    repo = parts[1]
    branch = parts[2] if len(parts) == 3 else 'main'

    if not owner or not repo:
        raise ValueError('Both owner and repo must be non-empty')

    return owner, repo, branch

@api_view(['DELETE'])
def delete_repository(request):
    """
    Delete all vectors for a repository from the Pinecone database.

    Accepts DELETE requests with a JSON body containing:
    {
        'repository': 'owner/repo/branch'  # branch is optional, defaults to 'main'
    }
    The repository string can optionally start with a forward slash.

    Examples:
        {
            'repository': 'microsoft/vscode'  # Uses 'main' branch
        }
        {
            'repository': 'microsoft/vscode/develop'  # Uses 'develop' branch
        }
        {
            'repository': '/microsoft/vscode/main'  # Leading slash is optional
        }

    Returns:
        200 OK: Successfully deleted repository vectors
            {
                'status': 'success',
                'repository': 'owner/repo/branch'
            }

        400 Bad Request: Invalid input
            {
                'error': '<error message>'
            }

        404 Not Found: Repository namespace not found
            {
                'error': 'Repository namespace not found'
            }

        500 Internal Server Error: Database error
            {
                'error': '<error message>'
            }
    """
    if not request.data:
        return Response(
            {'error': 'Please provide repository string in the request body'},
            status=status.HTTP_400_BAD_REQUEST
        )

    repository = request.data.get('repository')
    if not repository:
        return Response(
            {'error': 'Repository parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        owner, repo, branch = parse_repository_string(repository)
        namespace = f'{owner}/{repo}/{branch}'

        # Check if namespace exists
        stats = index.describe_index_stats()
        if namespace not in stats.namespaces:
            return Response(
                {'error': 'Repository namespace not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Delete all vectors in the namespace
        index.delete(namespace=namespace, delete_all=True)

        return Response({
            'status': 'success',
            'repository': namespace
        })

    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
