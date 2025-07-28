import uuid
from .models import Transaction
import requests
import os

class PesaPalService:
    def initiate_payment(self, phone_number):
        reference = str(uuid.uuid4())

        # Save transaction
        transaction = Transaction.objects.create(
            phone=phone_number,
            reference=reference,
            status='pending'
        )

        # Prepare headers and payload
        access_token = self.get_access_token()  # You must have this method
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "phoneNumber": phone_number,
            "amount": "100",  # Customize amount
            "reference": reference,
            "description": "Payment for product/service",
            "currency": "TZS",
            "callbackUrl": "https://your-domain.com/api/pesapal/callback"
        }

        # Call PesaPal API to trigger STK Push
        response = requests.post(
            f"{os.getenv('PESAPAL_BASE_URL')}/api/PostPesapalDirectOrderV4",
            json=payload,
            headers=headers
        )

        # Process response
        if response.status_code == 200:
            data = response.json()
            transaction.pesapal_transaction_id = data.get("transaction_id")
            transaction.save()
            return data
        else:
            print("Error from PesaPal:", response.text)
            return {"error": "Failed to initiate payment"}
