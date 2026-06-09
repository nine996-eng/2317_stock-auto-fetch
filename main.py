import os
import requests
import pandas as pd
from datetime import datetime
import yfinance as yf

def get_data():
    # 增加 Headers 模擬真實瀏覽器，這是避免證交所 API 報錯的關鍵
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.twse.com.tw/'
    }
    
    date_str = datetime.now().strftime("%Y%m%d")
    url_stock = f"https://www.twse.com.tw/fund/T86?response=json&date={date_str}&selectType=ALLBUT0999"
    
    try:
        res = requests.get(url_stock, headers=headers, timeout=20)
        # 檢查是否獲取到有效的 JSON
        if res.status_code == 200:
            data = res.json()
            if 'data' in data:
                df = pd.DataFrame(data['data'], columns=data['fields'])
                foxconn = df[df['證券代號'] == '2317']
                
                if not foxconn.empty:
                    # 組合您需要的資料字典
                    output_data = {
                        '日期': datetime.now().strftime("%Y-%m-%d"),
                        '鴻海_外資(張)': round(safe_int(foxconn['外陸資買賣超股數(不含外資自營商)'].values[0]) / 1000),
                        '鴻海_投信(張)': round(safe_int(foxconn['投信買賣超股數'].values[0]) / 1000),
                        '鴻海_自營(張)': round(safe_int(foxconn['自營商買賣超股數'].values[0]) / 1000),
                        '鴻海_收盤': round(yf.Ticker("2317.TW").history(period="1d")['Close'].iloc[-1], 2),
                        '大盤_外資(億)': get_market_val(df_m, '外資及陸資'),
                        '大盤_投信(億)': get_market_val(df_m, '投信'),
                        '大盤_自營(億)': get_market_val(df_m, '自營商'),
                        '加權指數': round(yf.Ticker("^TWII").history(period="1d")['Close'].iloc[-1], 2)
                    }
                    
                    # 存入 CSV
                    file_path = "foxconn_data.csv"
                    file_exists = os.path.isfile(file_path)
                    pd.DataFrame([output_data]).to_csv(file_path, mode='a', header=not file_exists, index=False, encoding='utf-8-sig')
                    print(f"資料成功寫入: {output_data}")
                else:
                    print("找不到代號 2317 的資料")
            else:
                print("今日無交易資料 (非交易日)")
        else:
            print(f"網頁請求失敗，狀態碼: {res.status_code}")
            
    except Exception as e:
        print(f"程式執行異常: {e}")

if __name__ == "__main__":
    get_data()
