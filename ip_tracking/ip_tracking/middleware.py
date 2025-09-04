from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from ipgeolocation import IpGeoLocation
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

        # Get geolocation (cached for 24h)
        geo_data = cache.get(f"geo_{ip}")
        if not geo_data:
            try:
                geo = IpGeoLocation(ip)
                geo_data = {
                    "country": geo.country_name or "",
                    "city": geo.city or "",
                }
                cache.set(f"geo_{ip}", geo_data, timeout=60 * 60 * 24)  # 24 hours
            except Exception as e:
                logger.error(f"Geolocation lookup failed for {ip}: {e}")
                geo_data = {"country": "", "city": ""}

        # Save request to DB
        RequestLog.objects.create(
            ip_address=ip,
            path=path,
            country=geo_data["country"],
            city=geo_data["city"],
        )

        # Log to console/file
        logger.info(f"Request from {ip} ({geo_data['country']}, {geo_data['city']}) to {path}")

    def get_client_ip(self, request):
        """Retrieve client IP address from headers or META."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
