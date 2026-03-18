from django.shortcuts import render

# Create your views here.
# battle/views.py

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@login_required
def delete_profile(request):
    if request.method == "DELETE":
        user = request.user
        user.delete()
        return JsonResponse({"message": "Profile deleted successfully"})
    
    return JsonResponse({"error": "Invalid request method"}, status=400)