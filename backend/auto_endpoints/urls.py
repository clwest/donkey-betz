from django.urls import path
from django.http import HttpRequest, JsonResponse

def healthcheck(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"ok": True})

urlpatterns = [
    path("health/", healthcheck),
]
