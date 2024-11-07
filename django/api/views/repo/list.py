from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from common.repo.list import list_repositories

@api_view(['GET'])
def list_repositories_view(request):
    """
    List all repositories (namespaces) stored in the Pinecone database.

    This endpoint accepts GET requests and returns a list of all available
    repository namespaces in the format owner/repo/branch.

    Returns:
        Response: JSON response containing the list of repositories
            {
                'repositories': [
                    'owner1/repo1/branch1',
                    'owner2/repo2/branch2',
                    ...
                ]
            }

    Raises:
        500 Internal Server Error: If there's an error accessing the database
            {
                'error': '<error message>'
            }
    """
    result = list_repositories()

    if 'error' in result:
        return Response(
            {'error': result['error']},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response(result)
