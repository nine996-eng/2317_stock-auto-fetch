import os
import requests
import pandas as pd
from datetime import datetime
import yfinance as yf

def safe_int(value):
    try:
        return int(str(value).replace(',', '').replace('-', '0'))
    except:
        return 0

def get_market_val(df_m, name):
    try:
        row = df_m[df_m.iloc[:, 0] == name]
        if not row.empty:
            return round(float(str(row.iloc[0, 3]).replace(',', '')) / 100000000, 1)
    except:
        pass
    return 0

def get_data():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    date_str = datetime.now().strftime("%Y%m%d")
    
    url_stock = f"https://www.twse.com.tw/fund/T86?response=json&date={date_str}&selectType=ALLBUT0999"
    url_market = f"https://www.twse.com.tw/fund/BFI8U2?response=json&date={date_str}"
    
    try:
        res_s = requests.get(url_stock, headers=headers, timeout=20)
        res_m = requests.get(url_market, headers=headers, timeout=20)
        
        if res_s.status_code == 200 and res_m.status_code == 200:
            data_s, data_m = res_s.json(), res_m.json()
            if 'data' in data_s and 'data' in data_m:
                df_s = pd.DataFrame(data_s['data'], columns=data_s['fields'])
                df_m = pd.DataFrame(data_m['data'], columns=data_m['fields'])
                foxconn = df_s[df_s['證券代號'] == '2317']
                
                if not foxconn.empty:
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
                    pd.DataFrame([output_data]).to_csv("foxconn_data.csv", mode='a', header=not os.path.exists("foxconn_data.csv"), index=False, encoding='utf-8-sig')
                    print("SUCCESS")
                else:
                    print("NO_DATA")
            else:
                print("NO_DATA")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    get_data()
