from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from common.repo.vectorize import vectorize_repository

@api_view(['POST'])
def vectorize_repository_view(request):
    """
    Vectorize a GitHub repository's contents and store in Pinecone.

    Accepts POST requests with a JSON body containing:
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
    200 OK: Successfully vectorized repository
    {
        'status': 'success',
        'processed_files': 5,
        'owner': 'owner',
        'repo': 'repo',
        'branch': 'branch'
    }

    400 Bad Request: Invalid input
    {
        'error': '<error message>'
    }

    500 Internal Server Error: Processing error
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
        result = vectorize_repository(repository)
        
        if 'error' in result:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
                if 'github_contents' in result
                else status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
        return Response(result)
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
