import uuid
import os
import requests
from .models import Transaction

class PesaPalService:
    def __init__(self):
        self.base_url = os.getenv("PESAPAL_BASE_URL")  # sandbox or live URL
        self.consumer_key = os.getenv("PESAPAL_CONSUMER_KEY")
        self.consumer_secret = os.getenv("PESAPAL_CONSUMER_SECRET")
        self.callback_url = os.getenv("PESAPAL_CALLBACK_URL")

    def get_access_token(self):
        url = f"{self.base_url}/api/Auth/RequestToken"
        payload = {
            "consumer_key": self.consumer_key,
            "consumer_secret": self.consumer_secret,
        }
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        token = response.json().get("token")
        if not token:
            raise Exception("Access token not received")
        return token

    def initiate_payment(self, phone_number, amount):
        reference = str(uuid.uuid4())
        transaction = Transaction.objects.create(
            phone=phone_number,
            reference=reference,
            amount=amount,
            status='pending'
        )

        access_token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "phoneNumber": phone_number,
            "amount": str(amount),
            "reference": reference,
            "description": "Payment for product/service",
            "currency": "TZS",
            "callbackUrl": self.callback_url
        }

        response = requests.post(f"{self.base_url}/api/PostPesapalDirectOrderV4", json=payload, headers=headers)

        if response.status_code == 200:
            data = response.json()
            transaction.pesapal_transaction_id = data.get("order_tracking_id") or data.get("transaction_id")
            transaction.save()
            return data
        else:
            return {"error": f"Failed to initiate payment: {response.text}"}
