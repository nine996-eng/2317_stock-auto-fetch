import os
import pandas as pd
from datetime import datetime
import yfinance as yf

def get_data():
    try:
        # 使用 yfinance 同步獲取鴻海與大盤數據
        # 這是目前在 GitHub Actions 環境下最穩定的方式，避開了證交所的爬蟲封鎖
        foxconn = yf.Ticker("2317.TW")
        twii = yf.Ticker("^TWII")
        
        hist_f = foxconn.history(period="1d")
        hist_t = twii.history(period="1d")
        
        if not hist_f.empty and not hist_t.empty:
            output_data = {
                '日期': datetime.now().strftime("%Y-%m-%d"),
                '鴻海_收盤': round(hist_f['Close'].iloc[-1], 2),
                '加權指數': round(hist_t['Close'].iloc[-1], 2)
            }
            
            # 寫入 CSV
            file_path = "foxconn_data.csv"
            file_exists = os.path.isfile(file_path)
            pd.DataFrame([output_data]).to_csv(file_path, mode='a', header=not file_exists, index=False, encoding='utf-8-sig')
            
            print(f"資料成功更新: {output_data}")
        else:
            print("無法從 Finance API 獲取數據")
            
    except Exception as e:
        print(f"程式運行異常: {e}")

if __name__ == "__main__":
    get_data()
