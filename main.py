import os
import requests
import pandas as pd
from datetime import datetime
from io import StringIO
import yfinance as yf

def get_data():
    date_str = datetime.now().strftime("%Y%m%d")
    url = f"https://www.twse.com.tw/exchangeReport/MI_三大法人?response=csv&date={date_str}&selectType=ALL"
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}

    # 1. 初始化資料
    foxconn_buy_sell = 0
    
    # 2. 嘗試抓取法人籌碼 (不強求成功)
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200 and len(res.text) > 1000:
            df_lines = [line for line in res.text.split('\n') if line.count('","') > 5]
            if df_lines:
                df_fund = pd.read_csv(StringIO("\n".join(df_lines)))
                df_fund.columns = df_fund.columns.str.strip().str.replace('"', '')
                row = df_fund[df_fund['證券代號'] == '2317']
                if not row.empty:
                    foxconn_buy_sell = int(str(row['外陸資買賣超股數(不含外資自營商)'].values[0]).replace(',', '')) // 1000
    except:
        print("法人資料抓取暫時不可用，僅記錄股價")

    # 3. 獲取穩定股價 (yfinance 非常穩定)
    try:
        hist = yf.Ticker("2317.TW").history(period="1d")
        if not hist.empty:
            output_data = {
                '日期': datetime.now().strftime("%Y-%m-%d"),
                '鴻海_外資(張)': foxconn_buy_sell,
                '鴻海_收盤': float(round(hist['Close'].iloc[-1], 2)),
                '加權指數': float(round(yf.Ticker("^TWII").history(period="1d")['Close'].iloc[-1], 2))
            }
            
            file_path = "foxconn_data.csv"
            file_exists = os.path.isfile(file_path)
            pd.DataFrame([output_data]).to_csv(file_path, mode='a', header=not file_exists, index=False, encoding='utf-8-sig')
            print(f"成功記錄: {output_data}")
        else:
            print("無法獲取股價資料")
    except Exception as e:
        print(f"致命錯誤: {e}")

if __name__ == "__main__":
    get_data()
