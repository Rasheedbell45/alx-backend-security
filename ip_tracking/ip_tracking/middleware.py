from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from .models import RequestLog, BlockedIP
import logging

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ip = self.get_client_ip(request)
        path = request.path

        # Check if IP is blocked
        if BlockedIP.objects.filter(ip_address=ip).exists():
            logger.warning(f"Blocked request from {ip} to {path}")
            return HttpResponseForbidden("Your IP is blocked.")

        # Save request to DB
        RequestLog.objects.create(ip_address=ip, path=path)

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
