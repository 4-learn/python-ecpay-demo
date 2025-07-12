#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import urllib.parse
import requests
import time

class ECPayQuery:
    def __init__(self):
        # 測試環境參數
        """
        self.merchant_id = '2000132'
        self.hash_key = '5294y06JbISpM5x9'
        self.hash_iv = 'v77hoKGq4kWxNNIS'
        """
        self.merchant_id = '3002607'
        self.hash_key = 'pwFHCqoQZGmho4w6'  
        self.hash_iv = 'EkRm7iFT261dpevs'
        self.query_url = 'https://payment-stage.ecpay.com.tw/Cashier/QueryTradeInfo/V5'
    
    def generate_check_mac_value(self, params):
        """生成檢查碼 CheckMacValue"""
        # 移除 CheckMacValue 參數（如果存在）
        if 'CheckMacValue' in params:
            del params['CheckMacValue']
        
        # 按照 key 依 A-Z 排序
        sorted_params = sorted(params.items())
        
        # 組合字串，格式：key=value&key=value
        query_parts = []
        for key, value in sorted_params:
            query_parts.append(f"{key}={value}")
        query_string = "&".join(query_parts)
        
        # 前面加上 HashKey、後面加上 HashIV
        raw_string = f"HashKey={self.hash_key}&{query_string}&HashIV={self.hash_iv}"
        
        print(f"加密前字串: {raw_string}")
        
        # URL Encode (使用 Python 的 quote_plus，類似 PHP 的 urlencode)
        from urllib.parse import quote_plus
        encoded_string = quote_plus(raw_string)
        
        # 依照綠界轉換表進行字元替換
        encoded_string = encoded_string.replace('%2d', '-')  # - 
        encoded_string = encoded_string.replace('%5f', '_')  # _
        encoded_string = encoded_string.replace('%2e', '.')  # .
        encoded_string = encoded_string.replace('%21', '!')  # !
        encoded_string = encoded_string.replace('%2a', '*')  # *
        encoded_string = encoded_string.replace('%28', '(')  # (
        encoded_string = encoded_string.replace('%29', ')')  # )
        
        # 轉為小寫
        encoded_string = encoded_string.lower()
        
        print(f"URL Encode 後: {encoded_string}")
        
        # SHA256 加密並轉大寫
        sha256_hash = hashlib.sha256(encoded_string.encode('utf-8')).hexdigest()
        
        return sha256_hash.upper()

    def query_order(self, merchant_trade_no, timestamp=None):
        """查詢訂單狀態"""
        if timestamp is None:
            timestamp = int(time.time())
        
        # 查詢參數
        params = {
            'MerchantID': self.merchant_id,
            'MerchantTradeNo': merchant_trade_no,
            'TimeStamp': timestamp
        }
        
        # 生成檢查碼
        check_mac_value = self.generate_check_mac_value(params.copy())
        params['CheckMacValue'] = check_mac_value
        
        print(f"\n=== 查詢訂單 {merchant_trade_no} ===")
        print(f"查詢參數:")
        for key, value in params.items():
            print(f"  {key}: {value}")
        
        try:
            # 發送查詢請求
            response = requests.post(self.query_url, data=params, timeout=30)
            
            print(f"\n查詢結果 (HTTP {response.status_code}):")
            print(response.text)
            
            if response.status_code == 200:
                # 解析查詢結果
                result = self.parse_query_result(response.text)
                return result
            else:
                print(f"查詢失敗，HTTP 狀態碼: {response.status_code}")
                return None
                
        except requests.RequestException as e:
            print(f"查詢請求失敗: {e}")
            return None
    
    def parse_query_result(self, response_text):
        """解析查詢結果"""
        result = {}
        pairs = response_text.split('&')
        
        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                result[key] = urllib.parse.unquote(value)
        
        return result
    
    def display_order_info(self, result):
        """顯示訂單資訊"""
        if not result:
            print("❌ 無法取得訂單資訊")
            return
        
        print(f"\n📋 訂單詳細資訊:")
        print(f"  訂單編號: {result.get('MerchantTradeNo', 'N/A')}")
        print(f"  綠界交易號: {result.get('TradeNo', 'N/A')}")
        print(f"  交易金額: {result.get('TradeAmt', 'N/A')}")
        print(f"  商品名稱: {result.get('ItemName', 'N/A')}")
        print(f"  交易日期: {result.get('TradeDate', 'N/A')}")
        print(f"  付款日期: {result.get('PaymentDate', 'N/A')}")
        print(f"  付款方式: {result.get('PaymentType', 'N/A')}")
        
        # 交易狀態解析
        trade_status = result.get('TradeStatus', 'N/A')
        status_desc = self.get_status_description(trade_status)
        print(f"  交易狀態: {trade_status} ({status_desc})")
        
        print(f"  手續費: {result.get('HandlingCharge', 'N/A')}")
        print(f"  付款手續費: {result.get('PaymentTypeChargeFee', 'N/A')}")
    
    def get_status_description(self, status):
        """取得狀態描述"""
        status_map = {
            '0': '訂單成立，等待付款',
            '1': '付款成功',
            '2': '失敗',
            '3': '訂單建立失敗',
            '10100073': '訂單已付款或訂單不存在',
            '10200047': '訂單尚未建立',
            '10200073': 'CheckMacValue 錯誤',
            '10500050': '付款方式錯誤'
        }
        
        return status_map.get(str(status), '未知狀態')

def main():
    """主程式"""
    query_tool = ECPayQuery()
    
    print("=== 綠界訂單查詢工具 ===\n")
    
    # 輸入要查詢的訂單編號
    while True:
        merchant_trade_no = input("請輸入訂單編號 (或輸入 'quit' 結束): ").strip()
        
        if merchant_trade_no.lower() == 'quit':
            print("程式結束")
            break
        
        if not merchant_trade_no:
            print("❌ 請輸入有效的訂單編號")
            continue
        
        # 查詢訂單
        result = query_tool.query_order(merchant_trade_no)
        
        # 顯示結果
        if result:
            query_tool.display_order_info(result)
        
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    main()
