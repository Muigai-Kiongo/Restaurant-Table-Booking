import requests
import json
import base64
from datetime import datetime
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Safaricom Daraja Sandbox Endpoints
OAUTH_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
STK_PUSH_URL = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

def get_access_token():
    consumer_key = getattr(settings, 'MPESA_CONSUMER_KEY', 'placeholder')
    consumer_secret = getattr(settings, 'MPESA_CONSUMER_SECRET', 'placeholder')
    
    try:
        response = requests.get(
            OAUTH_URL, 
            auth=(consumer_key, consumer_secret),
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        return data.get('access_token')
    except requests.exceptions.RequestException as e:
        logger.error(f"Error getting M-Pesa access token: {e}")
        return None

def format_phone_number(phone_number):
    """Format phone number to Safaricom standard 2547XXXXXXXX"""
    phone = phone_number.replace('+', '').replace(' ', '')
    if phone.startswith('0'):
        phone = '254' + phone[1:]
    return phone

def initiate_stk_push(phone_number, amount, account_reference, transaction_desc="Table Reservation"):
    """
    Initiates an STK push.
    amount: Must be an integer.
    """
    access_token = get_access_token()
    if not access_token:
        return {"error": "Failed to get access token"}

    business_short_code = getattr(settings, 'MPESA_BUSINESS_SHORT_CODE', '174379')
    passkey = getattr(settings, 'MPESA_PASSKEY', 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919')
    callback_url = getattr(settings, 'MPESA_CALLBACK_URL', 'https://mydomain.com/mpesa/callback/')
    
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password_str = business_short_code + passkey + timestamp
    password = base64.b64encode(password_str.encode('utf-8')).decode('utf-8')
    formatted_phone = format_phone_number(phone_number)

    payload = {
        "BusinessShortCode": business_short_code,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),
        "PartyA": formatted_phone,
        "PartyB": business_short_code,
        "PhoneNumber": formatted_phone,
        "CallBackURL": callback_url,
        "AccountReference": account_reference,
        "TransactionDesc": transaction_desc
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            STK_PUSH_URL,
            json=payload,
            headers=headers,
            timeout=15
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error initiating STK push: {e}")
        if e.response is not None:
            logger.error(f"Response: {e.response.text}")
        return {"error": str(e)}
