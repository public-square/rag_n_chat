from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
def ping(request):
    """
    Proof of life. Reverses a provided text string.

    This endpoint accepts POST requests with a JSON body containing a text field
    and returns both the original and reversed versions of the string.

    Args:
        request: DRF Request object containing POST data
            {
                "ping": "string to reverse"
            }

    Returns:
        Response: JSON response containing original and reversed strings
            {
                "ping": "string to reverse",
                "pong": "esrever ot gnirts"
            }

    Raises:
        400 Bad Request: If the request body is missing, text field is missing,
                        text is not a string, or text exceeds 1024 characters.
            {
                "error": "<error message>"
            }
    """
    if not request.data or 'ping' not in request.data:
        return Response(
            {'error': 'Please provide a text field in the request body'},
            status=status.HTTP_400_BAD_REQUEST
        )

    input_text = request.data['ping']

    if not isinstance(input_text, str):
        return Response(
            {'error': 'Text field must be a string'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(input_text) > 1024:
        return Response(
            {'error': 'Text must not exceed 1024 characters'},
            status=status.HTTP_400_BAD_REQUEST
        )

    reversed_text = input_text[::-1]

    return Response({
        'ping': input_text,
        'pong': reversed_text
    })