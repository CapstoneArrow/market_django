from django.urls import path
from . import views
from .views import get_csrf_token

app_name = "user"

urlpatterns = [
    path('api/csrf_token/', get_csrf_token),
    path("api/login/", views.login_api_view),
    path("api/logout/", views.logout_api_view),
    path("api/signup/", views.signup_api_view),
    path("api/find_username/", views.find_username_api_view),
    path("api/find_password/", views.find_password_api_view),
    path("api/update_profile/", views.update_profile_api_view),

    path("login/", views.login_view, name = "login"),
    path("logout/", views.logout_view,  name = "logout"),
    path("signup/", views.signup_view, name = "signup"),
    path("find_username/", views.find_username_view, name = "find_username"),
    path("find_password/", views.find_password_view, name = "find_password"),
    path("update_profile/", views.update_profile_view, name = "update_profile")
]
