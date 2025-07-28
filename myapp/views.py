from django.shortcuts import render
from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from .services import PesaPalService
from .models import *

# Create your views here.
class PesaPalPaymentView(APIView):
    def post(self, request):
        phone = request.data.get("phone")

        if not phone:
            return Response({"error": "Phone number is required"}, status=400)

        try:
            pesapal = PesaPalService()
            response = pesapal.initiate_payment(phone_number=phone)

            # Optionally log or save transaction record here

            return Response(response)

        except Exception as e:
            print("Error during PesaPal initiation:", e)
            return Response({"error": "Payment initiation failed."}, status=500)





class PesaPalCallbackView(APIView):
    def post(self, request):
        data = request.data

        transaction_id = data.get("transaction_id")
        status = data.get("status")  # "COMPLETED", "FAILED"

        try:
            transaction = Transaction.objects.get(pesapal_transaction_id=transaction_id)
            transaction.status = status.lower()
            transaction.save()
            return Response({"message": "Transaction updated successfully"})
        except Transaction.DoesNotExist:
            return Response({"error": "Transaction not found"}, status=404)
