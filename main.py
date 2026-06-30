import os
import pandas as pd
from datetime import datetime
import yfinance as yf

def get_data():
    try:
        foxconn = yf.Ticker("2317.TW")
        twii = yf.Ticker("^TWII")
        
        hist_f = foxconn.history(period="1d")
        hist_t = twii.history(period="1d")
        
        if not hist_f.empty and not hist_t.empty:
            data_f = hist_f.iloc[-1]
            
            output_data = {
                '日期': datetime.now().strftime("%Y-%m-%d"),
                '鴻海_開盤': float(round(data_f['Open'], 2)),
                '鴻海_最高': float(round(data_f['High'], 2)),
                '鴻海_最低': float(round(data_f['Low'], 2)),
                '鴻海_收盤': float(round(data_f['Close'], 2)),
                '鴻海_成交量': int(data_f['Volume']),
                '加權指數': float(round(hist_t['Close'].iloc[-1], 2))
            }
            
            file_path = "foxconn_data.csv"
            file_exists = os.path.isfile(file_path)
            pd.DataFrame([output_data]).to_csv(file_path, mode='a', header=not file_exists, index=False, encoding='utf-8-sig')
            
            print(f"資料擴充更新: {output_data}")
        else:
            print("無法獲取數據")
    except Exception as e:
        print(f"程式運行異常: {e}")

if __name__ == "__main__":
    get_data()
