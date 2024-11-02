from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from pinecone import Pinecone
import os

pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index(os.getenv('PINECONE_INDEX'))

@api_view(['GET'])
def list_repositories(request):
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
    try:
        # Get list of namespaces from Pinecone
        stats = index.describe_index_stats()
        namespaces = list(stats.namespaces.keys())

        # Sort namespaces for consistent output
        sorted_namespaces = sorted(namespaces)

        return Response({
            'repositories': sorted_namespaces
        })

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
