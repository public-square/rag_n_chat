from django.conf import settings
from common.utils import parse_repository_string
from pinecone import Pinecone

def delete_repository(repository):
    """
    Delete all vectors for a repository from the Pinecone database.

    Args:
        repository (str): Repository string in format 'owner/repo/branch' or 'owner/repo'
                         (branch defaults to 'main')

    Returns Either:
        On success:
            {
                'status': 'success',
                'repository': 'owner/repo/branch'
            }
        On error:
            {
                'error': '<error message>'
            }
    """
    try:
        pc_api_key = settings.PINECONE_API_KEY
        if not pc_api_key:
            return {'error': 'Pinecone API key not found'}

        pc_index_name = settings.PINECONE_INDEX
        if not pc_index_name:
            return {'error': 'Pinecone index name not found'}

        try:
            # Initialize Pinecone client
            pc = Pinecone(pc_api_key)
        except Exception as e:
            return {'error': f'Failed to initialize Pinecone client: {str(e)}'}

        try:
            # Get Pinecone index
            index = pc.Index(pc_index_name)
        except Exception as e:
            return {'error': f'Failed to get Pinecone index: {str(e)}'}

        try:
            owner, repo, branch = parse_repository_string(repository)
            namespace = f'{owner}/{repo}/{branch}'

            # Check if namespace exists
            stats = index.describe_index_stats()
            if namespace not in stats.namespaces:
                return {'error': 'Repository namespace not found'}

            # Delete all vectors in the namespace
            index.delete(namespace=namespace, delete_all=True)

            return {
                'status': 'success',
                'repository': namespace
            }

        except ValueError as e:
            return {'error': str(e)}
        except Exception as e:
            return {'error': f'Failed to delete repository: {str(e)}'}

    except Exception as e:
        return {
            'error': f'Unexpected error: {str(e)}'
        }
