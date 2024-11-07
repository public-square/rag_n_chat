from pinecone import Pinecone
import os

pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index(os.getenv('PINECONE_INDEX'))

def list_repositories():
    """
    List all repositories (namespaces) stored in the Pinecone database.

    Returns:
        list: A sorted list of repository namespaces in the format owner/repo/branch

    Raises:
        Exception: If there's an error accessing the database
    """
    # Get list of namespaces from Pinecone
    stats = index.describe_index_stats()
    namespaces = list(stats.namespaces.keys())

    # Sort namespaces for consistent output
    return sorted(namespaces)
