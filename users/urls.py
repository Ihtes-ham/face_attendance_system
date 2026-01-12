from django.urls import path
from . import views
from . import auth_views

app_name = 'users'

urlpatterns = [
    # -------------------------
    # Face Recognition
    # -------------------------
    path(
        'register-face/',
        views.register_face,
        name='register_face'
    ),

    # -------------------------
    # Employee Management
    # -------------------------
    path(
        'employees/',
        auth_views.employee_list,
        name='employee_list'
    ),

    # -------------------------
    # User Profile
    # -------------------------
    path(
        'profile/',
        auth_views.profile,
        name='profile'
    ),

    # -------------------------
    # Authentication
    # -------------------------
    path(
        'register/',
        auth_views.register,
        name='register'
    ),

    path(
        'change-password/',
        auth_views.change_password,
        name='change_password'
    ),

    path(
        'password-reset/',
        auth_views.password_reset_request,
        name='password_reset'
    ),
]
