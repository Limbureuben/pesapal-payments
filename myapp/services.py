import uuid
import os
import requests
from .models import Transaction


class PesaPalService:
    def __init__(self):
        self.base_url = os.getenv("PESAPAL_BASE_URL")
        self.consumer_key = os.getenv("PESAPAL_CONSUMER_KEY")
        self.consumer_secret = os.getenv("PESAPAL_CONSUMER_SECRET")

    def get_access_token(self):
        url = f"{self.base_url}/api/Auth/RequestToken"
        headers = {"Content-Type": "application/json"}
        payload = {
            "consumer_key": self.consumer_key,
            "consumer_secret": self.consumer_secret,
        }

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json().get("token")

    def initiate_payment(self, phone_number):
        reference = str(uuid.uuid4())

        # Save transaction
        transaction = Transaction.objects.create(
            phone=phone_number,
            reference=reference,
            status='pending'
        )

        # Prepare headers and payload
        access_token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "phoneNumber": phone_number,
            "amount": "100",  # Customize
            "reference": reference,
            "description": "Payment for product/service",
            "currency": "TZS",
            "callbackUrl": os.getenv("PESAPAL_CALLBACK_URL")  # Use from .env
        }

        # Send request to PesaPal
        response = requests.post(
            f"{self.base_url}/api/PostPesapalDirectOrderV4",
            json=payload,
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            transaction.pesapal_transaction_id = data.get("transaction_id")
            transaction.save()
            return data
        else:
            print("Error from PesaPal:", response.text)
            return {"error": "Failed to initiate payment"}
