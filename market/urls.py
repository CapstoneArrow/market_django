from django.urls import path
from . import views

app_name = "market"

urlpatterns = [
    path('', views.list_view, name = "list"),
    path('search/', views.search_view, name='search'),
    path('detail/<int:market_id>', views.detail_view, name='detail'),
]
