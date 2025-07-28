from django.shortcuts import render
from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from .services import PesaPalService

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
        print("📩 PesaPal Callback Received:", data)

        order_tracking_id = data.get("order_tracking_id")
        status_code = data.get("status")
        payment_method = data.get("payment_method")

        if not order_tracking_id:
            return Response({"error": "Missing tracking ID"}, status=400)

        # ✅ OPTIONAL: update transaction in DB
        # from .models import Transaction
        # Transaction.objects.filter(order_tracking_id=order_tracking_id).update(
        #     status=status_code,
        #     payment_method=payment_method
        # )

        return Response({"message": "Callback received"}, status=200)
