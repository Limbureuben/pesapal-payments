# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from rest_framework.views import APIView
# import json
# import requests
# from django.conf import settings
# from .pesapal import submit_order  # Your function that sends order to Pesapal

# @csrf_exempt
# def create_payment(request):
#     if request.method != 'POST':
#         return JsonResponse({'error': 'POST only'}, status=405)

#     try:
#         body = json.loads(request.body.decode('utf-8'))
#     except json.JSONDecodeError:
#         return JsonResponse({"error": "Invalid JSON"}, status=400)

#     order_data = {
#         "id": body.get("merchant_reference", "ORDER12345"),
#         "currency": body.get("currency", "KES"),
#         "amount": float(body.get("amount", 100.00)),
#         "description": body.get("description", "Testing Pesapal"),
#         "callback_url": settings.PESAPAL_CALLBACK_URL,
#         "notification_id": settings.PESAPAL_IPN_NOTIFICATION_ID,
#         "billing_address": {
#             "email_address": body.get("email", "test@example.com"),
#             "phone_number": body.get("phone", "0712345678"),
#             "country_code": body.get("country_code", "KE"),
#             "first_name": body.get("first_name", "John"),
#             "last_name": body.get("last_name", "Doe"),
#             "line_1": "Pesapal Limited"
#         }
#     }

#     # Call your pesapal order submission helper
#     result = submit_order(order_data)
#     return JsonResponse(result)


# @csrf_exempt
# def test_pesapal_token(request):
#     if request.method != 'POST':
#         return JsonResponse({'error': 'POST only'}, status=405)

#     url = "https://cybqa.pesapal.com/pesapalv3/api/Auth/RequestToken"
#     payload = {
#         "consumer_key": settings.PESAPAL_CONSUMER_KEY,
#         "consumer_secret": settings.PESAPAL_CONSUMER_SECRET
#     }
#     headers = {
#         "Content-Type": "application/json"
#     }

#     try:
#         res = requests.post(url, json=payload, headers=headers)
#         print(res.text)  # Debug info in terminal
#         if res.status_code == 200:
#             return JsonResponse(res.json())
#         else:
#             return JsonResponse({
#                 "error": "Failed to get token",
#                 "status": res.status_code,
#                 "body": res.text
#             }, status=res.status_code)
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)




# class InitiatePaymentView(APIView):
#     def post(self, request):
#         try:
#             phone = request.data.get('phone')
#             amount = request.data.get('amount')

#             if not phone or not amount:
#                 return Response({"error": "Phone and amount required"}, status=400)

#             # Get OAuth token first (assuming you have this function)
#             token = get_pesapal_token()
#             if not token:
#                 return Response({"error": "Failed to authenticate with PesaPal"}, status=500)

#             headers = {
#                 "Authorization": f"Bearer {token}",
#                 "Content-Type": "application/json"
#             }

#             data = {
#                 "amount": amount,
#                 "phone_number": phone,
#                 "currency": "TZS",
#                 "description": "Test payment",
#                 # add any additional PesaPal-required fields
#             }

#             res = requests.post("https://pay.pesapal.com/v3/api/Transactions/SubmitOrderRequest", json=data, headers=headers)

#             if res.status_code == 200:
#                 return Response(res.json())
#             else:
#                 return Response({"error": "PesaPal returned error", "details": res.text}, status=500)

#         except Exception as e:
#             return Response({"error": "Internal error", "details": str(e)}, status=500)

    
    
    
# @csrf_exempt
# def pesapal_callback(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             reference = data.get("reference")
#             status = data.get("status")
#             transaction_id = data.get("transaction_id")

#             # Update transaction status in your DB
#             transaction = Transaction.objects.filter(reference=reference).first()
#             if transaction:
#                 transaction.status = status
#                 transaction.pesapal_transaction_id = transaction_id
#                 transaction.save()

#             return JsonResponse({"message": "Received"}, status=200)
#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)
#     return JsonResponse({"error": "Invalid method"}, status=405)



import uuid
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView # type: ignore
from .models import Transaction
import json
from django.utils import timezone

PESAPAL_CONSUMER_KEY = 'ngW+UEcnDhltUc5fxPfrCD987xMh3Lx8'
PESAPAL_CONSUMER_SECRET = 'q27RChYs5UkypdcNYKzuUw460Dg='
TOKEN_URL = "https://cybqa.pesapal.com/pesapalv3/api/Auth/RequestToken"
PAYMENT_URL = "https://cybqa.pesapal.com/pesapalv3/api/Transactions/SubmitOrderRequest"
CALLBACK_URL = "https://44ec6f7dab00.ngrok-free.app/api/pesapal/callback/"  # Replace with your endpoint

# Step 1: Get OAuth token from Pesapal
def get_token():
    payload = {
        "consumer_key": PESAPAL_CONSUMER_KEY,
        "consumer_secret": PESAPAL_CONSUMER_SECRET
    }
    headers = {
        "Content-Type": "application/json"
    }
    try:
        res = requests.post(TOKEN_URL, json=payload, headers=headers)
        if res.status_code == 200:
            return res.json().get("token")
        return None
    except Exception as e:
        print("Token error:", e)
        return None

# Step 2: API to initiate payment
@method_decorator(csrf_exempt, name='dispatch')
class InitiatePaymentView(APIView):
    def post(self, request):
        data = json.loads(request.body)
        phone = data.get("phone")
        amount = data.get("amount")

        if not phone or not amount:
            return JsonResponse({"error": "Phone and amount are required"}, status=400)

        token = get_token()
        if not token:
            return JsonResponse({"error": "Failed to get token"}, status=500)

        reference = str(uuid.uuid4())[:12]

        payload = {
            "id": reference,
            "currency": "TZS",
            "amount": amount,
            "description": "Test Payment",
            "callback_url": CALLBACK_URL,
            "notification_id": "e99b7b28-5dbe-4803-a52f-db84949177ae",  # Optional unless you’ve registered one
            "billing_address": {
                "email_address": "customer@example.com",
                "phone_number": phone,
                "country_code": "TZ",
                "first_name": "John",
                "last_name": "Doe",
            }
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        try:
            res = requests.post(PAYMENT_URL, json=payload, headers=headers)
            if res.status_code == 200:
                data = res.json()
                Transaction.objects.create(
                    phone=phone,
                    amount=amount,
                    reference=reference,
                    pesapal_transaction_id=data.get("order_tracking_id"),
                    status='pending'
                )
                return JsonResponse({"message": "STK Push Sent", "redirect_url": data.get("redirect_url")})
            else:
                return JsonResponse({"error": "Failed to initiate payment", "details": res.text}, status=500)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)




# @csrf_exempt
# def pesapal_callback(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             print("PesaPal callback received:", data)

#             # Extract data from the callback (you might need to adjust field names depending on what PesaPal sends)
#             reference = data.get("order_tracking_id") or data.get("order_reference")
#             status = data.get("status")
#             pesapal_transaction_id = data.get("pesapal_transaction_id")

#             if not reference:
#                 return JsonResponse({"error": "Missing order reference"}, status=400)

#             try:
#                 transaction = Transaction.objects.get(reference=reference)
#             except Transaction.DoesNotExist:
#                 return JsonResponse({"error": "Transaction not found"}, status=404)

#             # Update the transaction
#             transaction.pesapal_transaction_id = pesapal_transaction_id or transaction.pesapal_transaction_id
#             if status:
#                 if status.lower() == "completed":
#                     transaction.status = "completed"
#                 elif status.lower() == "failed":
#                     transaction.status = "failed"
#                 else:
#                     transaction.status = "pending"
#             transaction.updated_at = timezone.now()
#             transaction.save()

#             return JsonResponse({"message": "Transaction updated"}, status=200)

#         except json.JSONDecodeError:
#             return JsonResponse({"error": "Invalid JSON"}, status=400)

#     return JsonResponse({"error": "Invalid request method"}, status=405)




@csrf_exempt
def pesapal_callback(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        print("PesaPal callback received:", data)

        # Extract identifiers
        reference = data.get("merchant_reference") or data.get("order_reference") or data.get("order_tracking_id")
        pesapal_transaction_id = data.get("order_tracking_id") or data.get("pesapal_transaction_id")
        status = data.get("status", "").lower()

        if not reference:
            return JsonResponse({"error": "Missing reference"}, status=400)

        try:
            transaction = Transaction.objects.get(reference=reference)
        except Transaction.DoesNotExist:
            return JsonResponse({"error": "Transaction not found"}, status=404)

        transaction.pesapal_transaction_id = pesapal_transaction_id or transaction.pesapal_transaction_id

        if status == "completed":
            transaction.status = "completed"
        elif status == "failed":
            transaction.status = "failed"
        else:
            transaction.status = "pending"

        transaction.updated_at = timezone.now()
        transaction.save()

        return JsonResponse({"message": "Transaction updated"}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

