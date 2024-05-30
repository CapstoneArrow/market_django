from django.urls import path
from . import views

app_name = "home"

urlpatterns = [
    path("", views.home_view, name = "home"),
    path('health/', views.health_check, name='health_check'),
]
