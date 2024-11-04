from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import os
from api.utils import *

@api_view(['POST'])
def vectorize_repository(request):
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
        owner, repo, branch = parse_repository_string(repository)
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        contents = utils.get_github_contents(owner, repo, branch)
        vectorized_files = []

        for file_info in contents:
            try:
                result = process_file_contents(file_info)

                if result:
                    vectorized_files.append(result)
            except Exception as e:
                # Log the error but continue processing other files
                print(f'Error processing {file_info["name"]}: {str(e)}')

        if not vectorized_files:
            return Response(
                {
                    'error': 'No valid files to process in repository: '
                    + f'{owner}/{repo}/{branch}',
                    'github_contents': contents
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        namespace = f'{owner}/{repo}/{branch}'
        vectors_to_upsert = [{
            'id': f'{namespace}/{file["file_name"]}',
            'values': file['embedding'],
            'metadata': {
                'file_name': file['file_name'],
                'owner': owner,
                'repo': repo,
                'branch': branch,
                'download_url': file['download_url'],
                'content': file['content']
            }
        } for file in vectorized_files]

        batch_size = 100
        for i in range(0, len(vectors_to_upsert), batch_size):
            batch = vectors_to_upsert[i:i + batch_size]
            index.upsert(vectors=batch, namespace=namespace)

        return Response({
            'status': 'success',
            'processed_files': len(vectorized_files),
            'owner': owner,
            'repo': repo,
            'branch': branch
        })

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
