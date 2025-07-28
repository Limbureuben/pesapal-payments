from django.shortcuts import render
from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from .services import PesaPalService
from .models import *
from rest_framework import status # type: ignore
import traceback  # For logging exceptions

# Create your views here.
class PesaPalPaymentView(APIView):
    def post(self, request):
        phone = request.data.get("phone")

        if not phone:
            return Response({"error": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            pesapal = PesaPalService()
            response = pesapal.initiate_payment(phone_number=phone)

            # If the service returned an error dict, handle it
            if isinstance(response, dict) and response.get("error"):
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            traceback.print_exc()  # logs full error to console
            return Response({
                "error": "Payment initiation failed",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
