from .views import *
from django.urls import path

urlpatterns = [
    path('pay/', PesaPalPaymentView.as_view(), name='pesapal-pay'),
    path('payment/callback/', PesaPalCallbackView.as_view(), name='pesapal-callback'),
]
