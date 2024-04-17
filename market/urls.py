from django.urls import path
from . import views

app_name = "market"

urlpatterns = [
    path("list", views.market_list_view, name = "list"),
    
]
