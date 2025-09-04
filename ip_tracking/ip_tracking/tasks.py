from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import RequestLog, SuspiciousIP


SENSITIVE_PATHS = ["/admin", "/login"]


@shared_task
def detect_suspicious_ips():
    """Detect IPs making >100 requests/hour or hitting sensitive paths."""
    one_hour_ago = timezone.now() - timedelta(hours=1)

    # Check for IPs with >100 requests/hour
    logs_last_hour = (
        RequestLog.objects.filter(timestamp__gte=one_hour_ago)
        .values("ip_address")
        .annotate(count=models.Count("id"))
    )

    for log in logs_last_hour:
        if log["count"] > 100:
            SuspiciousIP.objects.get_or_create(
                ip_address=log["ip_address"],
                reason=f"High request volume: {log['count']} requests in last hour",
            )

    # Check for sensitive path access
    sensitive_logs = RequestLog.objects.filter(
        timestamp__gte=one_hour_ago, path__in=SENSITIVE_PATHS
    ).values_list("ip_address", "path")

    for ip, path in sensitive_logs:
        SuspiciousIP.objects.get_or_create(
            ip_address=ip,
            reason=f"Accessed sensitive path: {path}",
        )
