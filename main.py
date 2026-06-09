import os
import requests
import pandas as pd
from datetime import datetime
import yfinance as yf
import time

def get_data():
    # 設置模擬瀏覽器的 Header，這是繞過證交所 API 限制的關鍵
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.twse.com.tw/'
    }
    
    date_str = datetime.now().strftime("%Y%m%d")
    url_stock = f"https://www.twse.com.tw/fund/T86?response=json&date={date_str}&selectType=ALLBUT0999"
    url_market = f"https://www.twse.com.tw/fund/BFI8U2?response=json&date={date_str}"
    
    try:
        # 抓取個股資料
        res_s = requests.get(url_stock, headers=headers, timeout=20)
        data_s = res_s.json()
        
        # 抓取大盤資料
        res_m = requests.get(url_market, headers=headers, timeout=20)
        data_m = res_m.json()
        
        if 'data' in data_s and 'data' in data_m:
            df_s = pd.DataFrame(data_s['data'], columns=data_s['fields'])
            foxconn = df_s[df_s['證券代號'] == '2317']
            
            df_m = pd.DataFrame(data_m['data'], columns=data_m['fields'])
            
            def get_market_val(name):
                row = df_m[df_m.iloc[:, 0] == name]
                if not row.empty:
                    val = str(row.iloc[0, 3]).replace(',', '')
                    return round(float(val) / 100000000, 1)
                return 0

            output_data = {
                '日期': datetime.now().strftime("%Y-%m-%d"),
                '鴻海_外資(張)': round(int(foxconn['外陸資買賣超股數(不含外資自營商)'].values[0].replace(',', ''))/1000),
                '鴻海_投信(張)': round(int(foxconn['投信買賣超股數'].values[0].replace(',', ''))/1000),
                '鴻海_自營(張)': round(int(foxconn['自營商買賣超股數'].values[0].replace(',', ''))/1000),
                '鴻海_收盤': round(yf.Ticker("2317.TW").history(period="1d")['Close'].iloc[-1], 2),
                '大盤_外資(億)': get_market_val('外資及陸資'),
                '大盤_投信(億)': get_market_val('投信'),
                '大盤_自營(億)': get_market_val('自營商'),
                '加權指數': round(yf.Ticker("^TWII").history(period="1d")['Close'].iloc[-1], 2)
            }
            
            file_path = "foxconn_data.csv"
            file_exists = os.path.isfile(file_path)
            pd.DataFrame([output_data]).to_csv(file_path, mode='a', header=not file_exists, index=False, encoding='utf-8-sig')
            print(f"資料成功更新: {output_data}")
        else:
            print("今日無交易資料 (非交易日或 API 未更新)")

    except Exception as e:
        print(f"程式執行異常: {e}")

if __name__ == "__main__":
    get_data()
