from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain import hub
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore, PineconeEmbeddings
from pinecone import Pinecone
import os
from common.utils import parse_repository_string
import logging
logger = logging.getLogger('django')

@api_view(['POST'])
def chat_with_gpt(request):
    """
    Chat with OpenAI's GPT model.

    This endpoint accepts POST requests with a JSON body containing a text field
    and returns the GPT model's response.

    Args:
        request: DRF Request object containing POST data
            {
                "prompt": "text to send to GPT",
                "repository": "optional repository name" (optional),
                "context": ["optional array of context strings"] (optional)
            }

    Returns:
        Response: JSON response containing GPT's response
            {
                "response": "GPT's response"
            }

    Raises:
        400 Bad Request: If the request body is missing, text field is missing,
                        text is not a string, or text exceeds 2048 characters.
            {
                "error": "<error message>"
            }
    """
    if not request.data or 'prompt' not in request.data:
        return Response(
            {'error': 'Please provide a prompt field in the request body'},
            status=status.HTTP_400_BAD_REQUEST
        )

    prompt = request.data['prompt']
    if not isinstance(prompt, str):
        return Response(
            {'error': 'Prompt field must be a string'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(prompt) > 2048:
        return Response(
            {'error': 'Prompt must not exceed 2048 characters'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if 'repository' in request.data:
        repository = request.data['repository']
        if not isinstance(repository, str):
            return Response(
                {'error': 'Repository field must be a string'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if len(repository) > 255:
            return Response(
                {'error': 'Repository must not exceed 255 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            owner, repo, branch = parse_repository_string(repository)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        repository = f'{owner}/{repo}/{branch}'
        pc = Pinecone(
            api_key=os.getenv('PINECONE_API_KEY'),
            environment=os.getenv('PINECONE_ENVIRONMENT')
        )

        index = pc.Index(os.getenv('PINECONE_INDEX'))
        #index = pc.Index(index_name)

        if repository not in list(index.describe_index_stats().namespaces.keys()):
            return Response(
                {
                    'error': 'Repository index not found: ' + repository
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    if 'context' in request.data:
        context = request.data['context']
        if not isinstance(context, list):
            return Response(
                {'error': 'Context must be an array'},
                status=status.HTTP_400_BAD_REQUEST
            )
        for item in context:
            if not isinstance(item, str):
                return Response(
                    {'error': 'All context items must be strings'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if len(item) > 255:
                return Response(
                    {'error': 'Context items must not exceed 255 characters'},
                    status=status.HTTP_400_BAD_REQUEST
                )



    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    try:
        llm = ChatOpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            model_name='gpt-4o-mini',
            temperature=0.0
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


    # if a repository is provided, use the Pinecone index
    if 'repository' in request.data:
        try:
            embeddings = OpenAIEmbeddings(
                model="text-embedding-ada-002",
                openai_api_key=os.getenv('OPENAI_API_KEY')
            )
        except ValueError as e:
            logger.info('Failed to instantiate OpenAIEmbeddings: ' + str(e))
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        input_dict = {"input": prompt}
        index_name = os.getenv('PINECONE_INDEX')
        retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
        docsearch = PineconeVectorStore.from_existing_index(
            index_name=index_name,
            namespace=repository,
            embedding=embeddings
        )
        combine_docs_chain = create_stuff_documents_chain(
            llm, retrieval_qa_chat_prompt
        )
        retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
        combine_docs_chain = create_stuff_documents_chain(
            llm, retrieval_qa_chat_prompt
        )
        retriever = docsearch.as_retriever(
            search_kwargs={
                'k': 3,
                'namespace': repository  # Explicitly set namespace
            }
        )
        retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)
        response = retrieval_chain.invoke(input_dict)
        return Response(
            { 'response': response }
        )

    # execute without Pinecone
    try:
        messages = [ HumanMessage( content=prompt ) ]
        response = llm.invoke(messages).content
        return Response(
            { 'response': response }
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
