from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from ratelimit.decorators import ratelimit


# Anonymous users: 5 requests/min
@ratelimit(key="ip", rate="5/m", method="POST", block=True)
# Authenticated users: 10 requests/min
@ratelimit(key="user_or_ip", rate="10/m", method="POST", block=True)
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return JsonResponse({"status": "success", "message": "Login successful"})
        else:
            return JsonResponse({"status": "error", "message": "Invalid credentials"}, status=401)

    return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)
