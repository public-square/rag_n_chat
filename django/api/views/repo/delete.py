from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from common.repo.delete import delete_repository


@api_view(['DELETE'])
def delete_repository_view(request):
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

    result = delete_repository(repository)

    if 'error' in result:
        if 'Repository namespace not found' in result['error']:
            return Response(
                {'error': result['error']},
                status=status.HTTP_404_NOT_FOUND
            )
        if any(err in result['error'] for err in ['Invalid repository', 'must be in format']):
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            {'error': result['error']},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response(result)
