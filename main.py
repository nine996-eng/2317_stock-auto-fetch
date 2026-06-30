import os
import pandas as pd
from datetime import datetime
import yfinance as yf

def get_data():
    date_str = datetime.now().strftime("%Y%m%d")
    # 改用 CSV 格式網址，通常比 JSON 接口更穩定
    url = f"https://www.twse.com.tw/exchangeReport/MI_MARGN?response=csv&date={date_str}&selectType=ALL"
    
    try:
        # 直接利用 pandas 讀取網址的 CSV，這種方式最像瀏覽器請求
        df = pd.read_csv(url, header=1, encoding='cp950')
        
        # 簡單清理資料
        df.columns = df.columns.str.strip()
        foxconn = df[df['股票代號'] == '2317']
        
        if not foxconn.empty:
            output_data = {
                '日期': datetime.now().strftime("%Y-%m-%d"),
                '鴻海_收盤': round(yf.Ticker("2317.TW").history(period="1d")['Close'].iloc[-1], 2),
                '加權指數': round(yf.Ticker("^TWII").history(period="1d")['Close'].iloc[-1], 2)
            }
            
            file_path = "foxconn_data.csv"
            file_exists = os.path.isfile(file_path)
            pd.DataFrame([output_data]).to_csv(file_path, mode='a', header=not file_exists, index=False, encoding='utf-8-sig')
            print(f"資料成功更新: {output_data}")
        else:
            print("今日無代號 2317 的交易資料")
            
    except Exception as e:
        print(f"程式運行異常: {e}")

if __name__ == "__main__":
    get_data()
