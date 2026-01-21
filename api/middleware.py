import logging
import time
import json
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('api.requests')


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware pour logger toutes les requêtes HTTP reçues par l'API.
    Enregistre : méthode, URL, utilisateur, temps de réponse, status code.
    """
    
    def process_request(self, request):
        """Appelé au début de chaque requête"""
        request.start_time = time.time()
        
        user = request.user if hasattr(request, 'user') else 'Anonymous'
        logger.info(
            f"[REQUEST] {request.method} {request.path} | User: {user} | IP: {self.get_client_ip(request)}"
        )
        
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                if request.content_type == 'application/json' and request.body:
                    body = json.loads(request.body)
                    safe_body = self.sanitize_sensitive_data(body)
                    logger.debug(f"[REQUEST BODY] {json.dumps(safe_body, indent=2)}")
            except (json.JSONDecodeError, Exception) as e:
                logger.debug(f"[REQUEST BODY] Unable to parse body: {str(e)}")
    
    def process_response(self, request, response):
        """Appelé après chaque réponse"""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
        else:
            duration = 0
        
        user = request.user if hasattr(request, 'user') else 'Anonymous'
        
        log_level = self.get_log_level(response.status_code)
        
        logger.log(
            log_level,
            f"[RESPONSE] {request.method} {request.path} | "
            f"Status: {response.status_code} | "
            f"User: {user} | "
            f"Duration: {duration:.3f}s"
        )
        
        if response.status_code >= 400:
            try:
                if hasattr(response, 'data'):
                    logger.warning(f"[RESPONSE ERROR] {json.dumps(response.data, indent=2)}")
            except Exception:
                pass
        
        return response
    
    def process_exception(self, request, exception):
        """Appelé en cas d'exception"""
        user = request.user if hasattr(request, 'user') else 'Anonymous'
        logger.error(
            f"[EXCEPTION] {request.method} {request.path} | "
            f"User: {user} | "
            f"Error: {str(exception)}",
            exc_info=True
        )
        return None
    
    @staticmethod
    def get_client_ip(request):
        """Récupère l'IP réelle du client (gère les proxies)"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def get_log_level(status_code):
        """Détermine le niveau de log selon le status code"""
        if status_code >= 500:
            return logging.ERROR
        elif status_code >= 400:
            return logging.WARNING
        else:
            return logging.INFO
    
    @staticmethod
    def sanitize_sensitive_data(data):
        """Masque les données sensibles dans les logs"""
        if not isinstance(data, dict):
            return data
        
        sensitive_fields = ['password', 'token', 'secret', 'api_key', 'authorization']
        sanitized = data.copy()
        
        for key in sanitized:
            if any(field in key.lower() for field in sensitive_fields):
                sanitized[key] = '***MASKED***'
            elif isinstance(sanitized[key], dict):
                sanitized[key] = RequestLoggingMiddleware.sanitize_sensitive_data(sanitized[key])
        
        return sanitized