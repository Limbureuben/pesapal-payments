import requests
from django.conf import settings


def initiate_payment(self, phone_number):
    url = f"{self.base_url}/api/Transactions/SubmitOrderRequest"
    headers = {
        "Authorization": f"Bearer {self.token}"
    }
    payload = {
        "id": settings.PESAPAL_NOTIFICATION_ID,
        "currency": "KES",
        "amount": "1",  # For testing; set real amount later
        "description": "E-Commerce Order Payment",
        "callback_url": "https://yourdomain.com/payment/callback",
        "notification_id": settings.PESAPAL_NOTIFICATION_ID,
        "billing_address": {
            "phone_number": phone_number,
            "email_address": "test@example.com",  # Optional
            "country_code": "KE",                # or "TZ" etc.
            "first_name": "Customer",
            "last_name": "Name",
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()
