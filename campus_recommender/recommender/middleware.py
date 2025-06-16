from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework.authtoken.models import Token
import logging

logger = logging.getLogger(__name__)

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # API paths that don't require authentication
        exempt_paths = [
            '/api/admins/login/',
            '/api/students/login/',
            '/api/students/register/',
            '/admin/',
            '/api-auth/'
        ]
        
        # Log the request path for debugging
        logger.debug(f"Request path: {request.path}")
        
        # Check if the request path is exempt
        for path in exempt_paths:
            if request.path.startswith(path):
                logger.debug(f"Path {request.path} is exempt from authentication")
                return self.get_response(request)
            
        # Check if this is an API request
        if request.path.startswith('/api/'):
            # Check for token authentication
            auth_header = request.headers.get('Authorization', '')
            logger.debug(f"Authorization header: {auth_header[:15]}..." if auth_header else "No Authorization header")
            
            if auth_header.startswith('Token '):
                token_key = auth_header.split(' ')[1]
                try:
                    Token.objects.get(key=token_key)
                    # Token is valid, proceed
                    logger.debug("Valid token found")
                    return self.get_response(request)
                except Token.DoesNotExist:
                    logger.debug(f"Invalid token: {token_key[:10]}...")
                    
            # No valid token, return 401 for API requests
            logger.debug(f"Unauthorized access to {request.path}")
            from django.http import JsonResponse
            return JsonResponse({'detail': 'Authentication credentials were not provided.'}, status=401)
            
        # For non-API requests, let Django handle normally
        # The frontend routes should handle authentication
        return self.get_response(request) 