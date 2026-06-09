import os
import requests
import pandas as pd
from datetime import datetime
import yfinance as yf

def get_data():
    date_str = datetime.now().strftime("%Y%m%d")
    url = f"https://www.twse.com.tw/fund/T86?response=json&date={date_str}&selectType=ALLBUT0999"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        df = pd.DataFrame(data['data'], columns=data['fields'])
        
        # 輔助：轉為「張」
        def to_sheets(val_str):
            num = int(str(val_str).replace(',', ''))
            return round(num / 1000)

        # 1. 鴻海資料
        foxconn = df[df['證券代號'] == '2317']
        # 2. 大盤資料 (證交所 API 預設就會回傳一筆「總計」數據，我們從該欄位抓取)
        market_total = df[df['證券代號'] == '2408'] # 註：證交所 API 中，大盤法人總計通常在特定行或透過累計計算

        # 為了確保精確，我們直接抓取「三大法人買賣超股數」的總合
        # 其實證交所 API 回傳的 df 中，有一列是專門給「三大法人」總計用的
        # 這裡我們直接計算所有個股的法人買賣超總和 (即大盤)
        total_foreign = df['外陸資買賣超股數(不含外資自營商)'].apply(lambda x: int(str(x).replace(',', ''))).sum()
        total_trust = df['投信買賣超股數'].apply(lambda x: int(str(x).replace(',', ''))).sum()
        total_dealer = df['自營商買賣超股數'].apply(lambda x: int(str(x).replace(',', ''))).sum()

        # 抓取股價
        ticker_2317 = yf.Ticker("2317.TW").history(period="1d")
        ticker_twii = yf.Ticker("^TWII").history(period="1d")
        
        output_data = {
            '日期': datetime.now().strftime("%Y-%m-%d"),
            '鴻海_外資(張)': to_sheets(foxconn['外陸資買賣超股數(不含外資自營商)'].values[0]),
            '鴻海_投信(張)': to_sheets(foxconn['投信買賣超股數'].values[0]),
            '鴻海_自營(張)': to_sheets(foxconn['自營商買賣超股數'].values[0]),
            '鴻海_收盤': round(ticker_2317['Close'].iloc[-1], 2),
            '大盤_外資(張)': round(total_foreign / 1000),
            '大盤_投信(張)': round(total_trust / 1000),
            '大盤_自營(張)': round(total_dealer / 1000),
            '加權指數': round(ticker_twii['Close'].iloc[-1], 2)
        }

     
        
        # 存檔
        file_path = "foxconn_data.csv"
        file_exists = os.path.isfile(file_path)
         pd.DataFrame([output_data]).to_csv(file_path, mode='a', header=not file_exists, index=False, encoding='utf-8-sig')
        # final_df = pd.DataFrame([output_data])
        # final_df.to_csv(file_path, mode='a', header=not file_exists, index=False, encoding='utf-8-sig')
         print(f"資料同步更新: {output_data}")

    except Exception as e:
        print(f"執行錯誤: {e}")

if __name__ == "__main__":
    get_data()
