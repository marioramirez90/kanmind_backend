from django.urls import path
from .views import LoginView, RegistrationView

urlpatterns = [
    path("registration/", RegistrationView.as_view(), name="registration"),
    path("login/", LoginView.as_view(), name="login"),
    path("auth/register/", RegistrationView.as_view(), name="registration-alias"),
    path("auth/login/", LoginView.as_view(), name="login-alias"),
]