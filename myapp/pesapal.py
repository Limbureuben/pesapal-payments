import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth

PESAPAL_BASE_URL = 'https://cybqa.pesapal.com/pesapalv3/api'

def get_access_token():
    url = f'{PESAPAL_BASE_URL}/Auth/RequestToken'
    response = requests.get(
        url,
        auth=HTTPBasicAuth(settings.PESAPAL_CONSUMER_KEY, settings.PESAPAL_CONSUMER_SECRET)
    )
    data = response.json()
    return data.get('token')

def submit_order(order_data):
    token = get_access_token()
    if not token:
        return {'error': 'Failed to get token'}

    url = f'{PESAPAL_BASE_URL}/Transactions/SubmitOrderRequest'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, json=order_data)

    try:
        return response.json()
    except Exception:
        return {'error': 'Invalid JSON response from PesaPal', 'raw': response.text}
