from django.utils.deprecation import MiddlewareMixin
from .models import RequestLog
import logging

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip = self.get_client_ip(request)
        path = request.path
        timestamp = request.timestamp if hasattr(request, "timestamp") else None

        # Save to DB
        RequestLog.objects.create(
            ip_address=ip,
            path=path
        )

        # Log to console/file
        logger.info(f"Request from {ip} to {path}")

    def get_client_ip(self, request):
        """Retrieve client IP address from headers or META."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
