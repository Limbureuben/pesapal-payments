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

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            token = data.get("token")
            if not token:
                raise ValueError("Access token not found in response")
            return token
        except requests.exceptions.RequestException as e:
            print("RequestException during token request:", e)
            raise
        except ValueError as ve:
            print("ValueError:", ve)
            raise
        except Exception as e:
            print("Unknown error during get_access_token:", e)
            raise

    def initiate_payment(self, phone_number):
        reference = str(uuid.uuid4())

        transaction = Transaction.objects.create(
            phone=phone_number,
            reference=reference,
            status='pending'
        )

        try:
            access_token = self.get_access_token()
        except Exception as e:
            return {"error": f"Token generation failed: {str(e)}"}

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "phoneNumber": phone_number,
            "amount": "100",  # Make this dynamic if needed
            "reference": reference,
            "description": "Payment for product/service",
            "currency": "TZS",
            "callbackUrl": os.getenv("PESAPAL_CALLBACK_URL")
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/PostPesapalDirectOrderV4",
                json=payload,
                headers=headers
            )

            if response.status_code == 200:
                try:
                    data = response.json()
                    pesapal_transaction_id = data.get("transaction_id") or data.get("order_tracking_id")
                    if pesapal_transaction_id:
                        transaction.pesapal_transaction_id = pesapal_transaction_id
                        transaction.save()
                    return data
                except ValueError:
                    print("JSON decoding error. Raw response text:", response.text)
                    return {"error": "Invalid JSON response from PesaPal"}
            else:
                print(f"PesaPal API returned {response.status_code}: {response.text}")
                return {
                    "error": "Failed to initiate payment",
                    "status": response.status_code,
                    "details": response.text
                }

        except requests.exceptions.RequestException as e:
            print("RequestException during payment initiation:", e)
            return {"error": "Payment request failed", "details": str(e)}
