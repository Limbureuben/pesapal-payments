# from django.shortcuts import render
# from rest_framework.views import APIView # type: ignore
# from rest_framework.response import Response # type: ignore
# from .services import PesaPalService
# from .models import *
# from rest_framework import status # type: ignore
# import traceback  # For logging exceptions

# # Create your views here.
# class PesaPalPaymentView(APIView):
#     def post(self, request):
#         phone = request.data.get("phone")

#         if not phone:
#             return Response({"error": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             pesapal = PesaPalService()
#             response = pesapal.initiate_payment(phone_number=phone)

#             # If the service returned an error dict, handle it
#             if isinstance(response, dict) and response.get("error"):
#                 return Response(response, status=status.HTTP_400_BAD_REQUEST)

#             return Response(response, status=status.HTTP_200_OK)

#         except Exception as e:
#             traceback.print_exc()  # logs full error to console
#             return Response({
#                 "error": "Payment initiation failed",
#                 "details": str(e)
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class PesaPalCallbackView(APIView):
#     def post(self, request):
#         data = request.data

#         transaction_id = data.get("transaction_id")
#         status = data.get("status")  # "COMPLETED", "FAILED"

#         try:
#             transaction = Transaction.objects.get(pesapal_transaction_id=transaction_id)
#             transaction.status = status.lower()
#             transaction.save()
#             return Response({"message": "Transaction updated successfully"})
#         except Transaction.DoesNotExist:
#             return Response({"error": "Transaction not found"}, status=404)




from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .pesapal import submit_order
from django.conf import settings

@csrf_exempt
def create_payment(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    body = json.loads(request.body.decode('utf-8'))

    order_data = {
        "id": body.get("merchant_reference", "ORDER12345"),
        "currency": "KES",
        "amount": float(body.get("amount", 100.00)),
        "description": body.get("description", "Testing Pesapal"),
        "callback_url": settings.PESAPAL_CALLBACK_URL,
        "notification_id": settings.PESAPAL_IPN_NOTIFICATION_ID,
        "billing_address": {
            "email_address": body.get("email", "test@example.com"),
            "phone_number": body.get("phone", "0712345678"),
            "country_code": "KE",
            "first_name": body.get("first_name", "John"),
            "last_name": body.get("last_name", "Doe"),
            "line_1": "Pesapal Limited"
        }
    }

    result = submit_order(order_data)
    return JsonResponse(result)




import requests
from django.http import JsonResponse

def test_pesapal_token(request):
    url = "https://sandbox.pesapal.com/v3/api/Auth/RequestToken"
    payload = {
        "consumer_key": "ngW+UEcnDhltUc5fxPfrCD987xMh3Lx8",
        "consumer_secret": "q27RChYs5UkypdcNYKzuUw460Dg="
    }
    headers = {
        "Content-Type": "application/json"
    }

    try:
        res = requests.post(url, json=payload, headers=headers)
        print(res.text)  # Debugging info in terminal
        if res.status_code == 200:
            return JsonResponse(res.json())
        return JsonResponse({"error": "Failed to get token", "status": res.status_code, "body": res.text})
    except Exception as e:
        return JsonResponse({"error": str(e)})
