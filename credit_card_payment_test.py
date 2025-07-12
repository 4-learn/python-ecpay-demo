import hashlib
import time
from datetime import datetime

class ECPayAPI:
    def __init__(self):
        self.api_url = "https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5"
        self.merchant_id = '3002607'
        self.hash_key = 'pwFHCqoQZGmho4w6'  
        self.hash_iv = 'EkRm7iFT261dpevs'

    def generate_check_mac_value(self, params):
        """生成檢查碼"""
        if 'CheckMacValue' in params:
            del params['CheckMacValue']
        
        # 按照 key 依 A-Z 排序
        sorted_params = sorted(params.items())
        
        # 組合字串
        query_parts = []
        for key, value in sorted_params:
            query_parts.append(f"{key}={value}")
        query_string = "&".join(query_parts)
        
        # 加上 HashKey 和 HashIV
        raw_string = f"HashKey={self.hash_key}&{query_string}&HashIV={self.hash_iv}"
        
        # URL Encode
        from urllib.parse import quote_plus
        encoded_string = quote_plus(raw_string)
        
        # 字元替換
        encoded_string = encoded_string.replace('%2d', '-')
        encoded_string = encoded_string.replace('%5f', '_')
        encoded_string = encoded_string.replace('%2e', '.')
        encoded_string = encoded_string.replace('%21', '!')
        encoded_string = encoded_string.replace('%2a', '*')
        encoded_string = encoded_string.replace('%28', '(')
        encoded_string = encoded_string.replace('%29', ')')
        
        # 轉為小寫
        encoded_string = encoded_string.lower()
        
        # SHA256 加密並轉大寫
        sha256_hash = hashlib.sha256(encoded_string.encode('utf-8')).hexdigest()
        return sha256_hash.upper()
    
    def create_payment_form(self, order_data):
        """建立付款表單"""
        params = {
            'MerchantID': self.merchant_id,
            'MerchantTradeNo': order_data['trade_no'],
            'MerchantTradeDate': datetime.now().strftime('%Y/%m/%d %H:%M:%S'),
            'PaymentType': 'aio',
            'TotalAmount': str(order_data['amount']),
            'TradeDesc': order_data['description'],
            'ItemName': order_data['item_name'],
            'ReturnURL': 'https://www.ecpay.com.tw/return_url.php',
            'ChoosePayment': 'Credit',  # 指定信用卡付款
            'EncryptType': 1
        }
        
        # 產生檢查碼
        params['CheckMacValue'] = self.generate_check_mac_value(params)
        return params

def generate_payment_html():
    """生成付款 HTML 頁面"""
    ecpay = ECPayAPI()
    
    # 訂單資料
    order_data = {
        'trade_no': f"TEST{int(time.time())}",  # 使用 TEST 開頭
        'amount': 100,
        'description': '信用卡付款測試',
        'item_name': '測試商品'
    }
    
    # 建立付款表單參數
    form_params = ecpay.create_payment_form(order_data)
    
    # 生成 HTML
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>綠界信用卡付款測試</title>
</head>
<body>
    <h2>綠界信用卡付款測試</h2>
    <p>訂單編號：{order_data['trade_no']}</p>
    <p>金額：{order_data['amount']} 元</p>
    
    <form id="ecpay_form" method="post" action="{ecpay.api_url}">
"""
    
    for key, value in form_params.items():
        html += f'        <input type="hidden" name="{key}" value="{value}">\n'
    
    html += """
        <input type="submit" value="前往付款" style="
            background-color: #28a745;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
        ">
    </form>
    
    <script>
        // 自動提交表單（可選）
        // document.getElementById('ecpay_form').submit();
    </script>
</body>
</html>
"""
    
    return html, order_data['trade_no']

# 執行
if __name__ == "__main__":
    print("=== 生成信用卡付款測試頁面 ===")
    
    html_content, trade_no = generate_payment_html()
    
    # 儲存 HTML 檔案
    filename = "credit_card_payment_test.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"✅ 付款測試頁面已生成：{filename}")
    print(f"📝 訂單編號：{trade_no}")
    print(f"💰 測試金額：100 元")
    print("\n🚀 使用步驟：")
    print("1. 開啟生成的 HTML 檔案")
    print("2. 點擊「前往付款」按鈕")
    print("3. 使用測試信用卡完成付款")
    print("4. 完成後查看後台訂單")
