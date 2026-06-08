import os
import requests
import pandas as pd
from datetime import datetime
import yfinance as yf

def get_data():
    date_str = datetime.now().strftime("%Y%m%d")
    url_stock = f"https://www.twse.com.tw/fund/T86?response=json&date={date_str}&selectType=ALLBUT0999"
    url_market = f"https://www.twse.com.tw/fund/BFI8U2?response=json&date={date_str}"
    
    headers = {'User-Agent': 'Mozilla/5.0'} # 偽裝成瀏覽器，避免被證交所阻擋
    
    try:
        # 抓取並確保連線成功
        res_s = requests.get(url_stock, headers=headers, timeout=15)
        if res_s.status_code != 200:
            print(f"無法存取個股資料，狀態碼: {res_s.status_code}")
            return
            
        data_s = res_s.json()
        if 'data' not in data_s:
            print("目前網頁無個股交易資料 (可能尚未結算)")
            return
            
        df_s = pd.DataFrame(data_s['data'], columns=data_s['fields'])
        foxconn = df_s[df_s['證券代號'] == '2317']
        
        # 抓大盤
        res_m = requests.get(url_market, headers=headers, timeout=15)
        data_m = res_m.json()
        df_m = pd.DataFrame(data_m['data'], columns=data_m['fields'])
        
        def get_market_val(name):
            row = df_m[df_m.iloc[:, 0] == name]
            if not row.empty:
                val = str(row.iloc[0, 3]).replace(',', '')
                return round(float(val) / 100000000, 1)
            return 0

        # 整理輸出
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
        
        # 存檔
        file_path = r"D:\StockProject\foxconn_data.csv"
        file_exists = os.path.isfile(file_path)
        pd.DataFrame([output_data]).to_csv(file_path, mode='a', header=not file_exists, index=False, encoding='utf-8-sig')
        print(f"資料成功更新: {output_data}")

    except Exception as e:
        print(f"今日資料尚未準備好或網路連線異常: {e}")

if __name__ == "__main__":
    get_data()