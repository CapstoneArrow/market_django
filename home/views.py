from django.shortcuts import render
from django.http import JsonResponse

def home_view(request):
    return render(request, 'home/home.html')

def health_check(request):
    return JsonResponse({'status': 'ok'})