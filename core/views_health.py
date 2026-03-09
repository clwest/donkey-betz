import sys
import time
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

_START_TIME = time.monotonic()


@api_view(['GET'])
@permission_classes([AllowAny])
def extended_health(request):
    db_ok = True
    try:
        from django.db import connection
        connection.ensure_connection()
    except Exception:
        db_ok = False

    return Response({
        'server_time': timezone.now().isoformat(),
        'uptime_seconds': round(time.monotonic() - _START_TIME, 2),
        'database_ok': db_ok,
        'python_version': sys.version,
    })
