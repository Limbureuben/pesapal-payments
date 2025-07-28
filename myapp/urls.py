from . import views
from django.urls import path
from .views import *
urlpatterns = [
    # path('pesapal/initiate/', create_payment),
    # path('test-token/', test_pesapal_token),
    path('pesapal/initiate/', InitiatePaymentView.as_view(), name='pesapal-initiate'),
    path('api/pesapal/callback/', views.pesapal_callback, name='pesapal_callback'),
]
