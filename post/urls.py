from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, AttachmentViewSet
from . import views

app_name = "post"

router = DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'attachments', AttachmentViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('create/', views.create_post, name='create_post'),
    path('<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('<int:post_id>/', views.view_post, name='view_post'),
    path('', views.post_list, name='post_list'),
]