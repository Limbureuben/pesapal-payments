from .views import *
from django.urls import path

urlpatterns = [
    path('pesapal/initiate/', create_payment),
]
