import hashlib
import time
from datetime import datetime
import requests
from urllib.parse import quote_plus


class ECPayAPI:
    def __init__(self):
        self.api_url = "https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5"
        self.merchant_id = '3002607'
        self.hash_key = 'pwFHCqoQZGmho4w6'
        self.hash_iv = 'EkRm7iFT261dpevs'

    def generate_check_mac_value(self, params):
        """產生檢查碼"""
        params = {k: v for k, v in params.items() if k != 'CheckMacValue'}
        sorted_params = sorted(params.items())
        raw = '&'.join([f"{k}={v}" for k, v in sorted_params])
        raw_string = f"HashKey={self.hash_key}&{raw}&HashIV={self.hash_iv}"
        encoded = quote_plus(raw_string).lower()
        for k, v in {
            '%2d': '-', '%5f': '_', '%2e': '.', '%21': '!',
            '%2a': '*', '%28': '(', '%29': ')'
        }.items():
            encoded = encoded.replace(k, v)
        return hashlib.sha256(encoded.encode('utf-8')).hexdigest().upper()

    def create_payment_form(self, order_data):
        params = {
            'MerchantID': self.merchant_id,
            'MerchantTradeNo': order_data['trade_no'],
            'MerchantTradeDate': datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
            'PaymentType': 'aio',
            'TotalAmount': str(order_data['amount']),
            'TradeDesc': order_data['description'],
            'ItemName': order_data['item_name'],
            'ReturnURL': 'https://www.ecpay.com.tw/return_url.php',
            'ClientBackURL': 'https://www.ecpay.com.tw',
            'OrderResultURL': 'https://www.ecpay.com.tw/receive.php',
            'NeedExtraPaidInfo': 'N',
            'EncryptType': 1,
            'ChoosePayment': 'Credit'
        }
        params['CheckMacValue'] = self.generate_check_mac_value(params)
        return params


def send_payment_request():
    ecpay = ECPayAPI()
    order_data = {
        'trade_no': f"ORDER{int(time.time())}",
        'amount': 100,
        'description': '測試商品',
        'item_name': '測試商品 x 1'
    }
    form_params = ecpay.create_payment_form(order_data)

    response = requests.post(ecpay.api_url, data=form_params)
    if response.status_code == 200 and 'html' in response.headers.get('Content-Type', ''):
        with open("payment_page.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"✅ 付款頁面已儲存為 payment_page.html")
        print(f"🧾 訂單編號：{order_data['trade_no']}")
    else:
        print(f"❌ 發送失敗：{response.status_code}")
        print(response.text)


if __name__ == "__main__":
    send_payment_request()

