from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from common.chat.prompt import process_chat_prompt

@api_view(['POST'])
def chat_with_gpt_view(request):
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

    repository = request.data.get('repository')
    if repository is not None:
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

    context = request.data.get('context')
    if context is not None:
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



    repository = request.data.get('repository')
    context = request.data.get('context')
    
    try:
        result = process_chat_prompt(prompt, repository, context)
        
        if 'error' in result:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return Response(result)
        
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
