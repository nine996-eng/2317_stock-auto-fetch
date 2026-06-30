import os
import requests
import pandas as pd
from datetime import datetime
from io import StringIO
import yfinance as yf

def get_data():
    date_str = datetime.now().strftime("%Y%m%d")
    # 證交所三大法人買賣超統計表 (CSV 格式)
    url = f"https://www.twse.com.tw/exchangeReport/MI_三大法人?response=csv&date={date_str}&selectType=ALL"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    }

    try:
        # 1. 取得法人買賣超資料
        res = requests.get(url, headers=headers, timeout=20)
        # 過濾 CSV 開頭的無效說明文字
        df_lines = [line for line in res.text.split('\n') if line.count('","') > 5]
        df_fund = pd.read_csv(StringIO("\n".join(df_lines)))
        
        # 清理欄位名稱
        df_fund.columns = df_fund.columns.str.strip().str.replace('"', '')
        
        # 尋找鴻海 (2317)
        foxconn_fund = df_fund[df_fund['證券代號'] == '2317']
        
        # 2. 獲取股價資料
        hist = yf.Ticker("2317.TW").history(period="1d")
        
        if not foxconn_fund.empty and not hist.empty:
            # 取得外資買賣超 (需移除逗號並轉為整數)
            foreign_buy_sell = str(foxconn_fund['外陸資買賣超股數(不含外資自營商)'].values[0]).replace(',', '')
            
            output_data = {
                '日期': datetime.now().strftime("%Y-%m-%d"),
                '鴻海_外資(張)': int(int(foreign_buy_sell) / 1000),
                '鴻海_收盤': float(round(hist['Close'].iloc[-1], 2)),
                '加權指數': float(round(yf.Ticker("^TWII").history(period="1d")['Close'].iloc[-1], 2))
            }
            
            # 寫入 CSV
            file_path = "foxconn_data.csv"
            file_exists = os.path.isfile(file_path)
            pd.DataFrame([output_data]).to_csv(file_path, mode='a', header=not file_exists, index=False, encoding='utf-8-sig')
            print(f"成功記錄數據: {output_data}")
        else:
            print("今日無鴻海交易資料")
            
    except Exception as e:
        print(f"程式運行異常: {e}")

if __name__ == "__main__":
    get_data()
