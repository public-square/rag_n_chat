import logging
from django.conf import settings
from common.utils import parse_repository_string
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain import hub
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone


logger = logging.getLogger('django')

def process_chat_prompt(prompt, repository=None, context=None):
    """
    Process a chat prompt with OpenAI's GPT model, optionally using repository context.

    Args:
        prompt (str): The prompt text to send to GPT
        repository (str, optional): Repository string in format 'owner/repo/branch'
        context (list, optional): Additional context strings

    Returns:
        dict: A dictionary containing:
            On success:
                {
                    'response': 'GPT response text'
                }
            On error:
                {
                    'error': 'error message'
                }

    Raises:
        ValueError: If input validation fails
        Exception: If there's an error processing the chat
    """
    try:
        llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model_name='gpt-4o-mini',
            temperature=0.0
        )
    except Exception as e:
        return {'error': str(e)}

    # If repository context is provided, use Pinecone
    if repository:
        try:
            owner, repo, branch = parse_repository_string(repository)
            repository = f'{owner}/{repo}/{branch}'

            pc = Pinecone(
                api_key=settings.PINECONE_API_KEY,
                environment=settings.PINECONE_ENVIRONMENT
            )

            index = pc.Index(settings.PINECONE_INDEX)

            if repository not in list(index.describe_index_stats().namespaces.keys()):
                return {
                    'error': 'Repository index not found: ' + repository
                }

            try:
                embeddings = OpenAIEmbeddings(
                    model="text-embedding-ada-002",
                    openai_api_key=settings.OPENAI_API_KEY
                )
            except ValueError as e:
                logger.info('Failed to instantiate OpenAIEmbeddings: ' + str(e))
                return {'error': str(e)}

            input_dict = {"input": prompt}
            index_name = settings.PINECONE_INDEX
            retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
            docsearch = PineconeVectorStore.from_existing_index(
                index_name=index_name,
                namespace=repository,
                embedding=embeddings
            )
            combine_docs_chain = create_stuff_documents_chain(
                llm, retrieval_qa_chat_prompt
            )
            retriever = docsearch.as_retriever(
                search_kwargs={
                    'k': 3,
                    'namespace': repository
                }
            )
            retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)
            chat_response = retrieval_chain.invoke(input_dict)
            return {'response': chat_response['answer']}

        except Exception as e:
            return {'error': str(e)}

    # Execute without Pinecone
    try:
        messages = [HumanMessage(content=prompt)]
        response = llm.invoke(messages).content
        return {'response': response}
    except Exception as e:
        return {'error': str(e)}
