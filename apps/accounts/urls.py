from django.urls import path
from django.contrib.auth import views as auth_views
from .views import register_view, profile_view, simple_logout_view

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', simple_logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
]


