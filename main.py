def get_data():
    # 增加更多偽裝資訊
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.twse.com.tw/zh/page/trading/fund/T86.html',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest'
    }
    # 建立 session，有時候 Session 維持連線比較不容易被擋
    session = requests.Session()
    
    date_str = datetime.now().strftime("%Y%m%d")
    url_stock = f"https://www.twse.com.tw/fund/T86?response=json&date={date_str}&selectType=ALLBUT0999"
    url_market = f"https://www.twse.com.tw/fund/BFI8U2?response=json&date={date_str}"
    
    try:
        # 使用 session 請求
        res_s = session.get(url_stock, headers=headers, timeout=20)
        res_m = session.get(url_market, headers=headers, timeout=20)
        
        # 這裡加入除錯訊息，如果還是失敗，我們可以看到具體是什麼
        if res_s.status_code != 200:
            print(f"DEBUG: 請求失敗，狀態碼: {res_s.status_code}")
            return
            
        data_s = res_s.json()
        data_m = res_m.json()
        # ... 以下代碼不變 ...
