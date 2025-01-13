import pandas as pd
import pandas_ta as ta
from binance.client import Client
from binance.exceptions import BinanceAPIException
from pushbullet import Pushbullet
import time

# Binance API keys
api_key = "0Jy9n0YBJR1dO0JfSK1EqCE1Wy4bjPPib6Te8LJmlZEsMLeeiLyLB1l1syV9Pqpd"
api_secret = "SGBCuUZklmnwKPxTOkDJD4GzHXDoVpRhL531SJBeo5HcZG33hazfPTyF02r1fEgC"

# Pushbullet API token
pushbullet_api_token = "o.q0ccdh4IoWKycJpPucyUjfnfvbEwO9S3"

# Initialize Binance client
client = Client(api_key, api_secret)

# Initialize Pushbullet client
pb = Pushbullet(pushbullet_api_token)

# Symbols to track
symbols = ["XRPUSDT", "SOLUSDT"]

# Function to send a notification
def send_push_notification(title, message):
    push = pb.push_note(title, message)
    print(f"Notification sent: {title} - {message}")

for symbol in symbols:
    try:
        # Fetch klines for the symbol (4-hour interval)
        klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_4HOUR)

        # Convert to DataFrame
        df = pd.DataFrame(klines, columns=[
            "open_time", "open", "high", "low", "close", "volume", "close_time",
            "quote_asset_volume", "number_of_trades", "taker_buy_base_volume", 
            "taker_buy_quote_volume", "ignore"
        ])
        df['close'] = pd.to_numeric(df['close'])

        # Calculate EMAs
        df['EMA_4'] = ta.ema(df['close'].iloc[:], length=4)
        df['EMA_9'] = ta.ema(df['close'].iloc[:], length=9)
        df['EMA_18'] = ta.ema(df['close'].iloc[:], length=18)

        print(f"{symbol} EMA calculations completed.")
        
        # Check for crossover conditions
        if len(df) >= 2:  # Ensure we have at least two rows to compare
            prev_row = df.iloc[-2]
            latest_row = df.iloc[-1]

            # Buy Signal: EMA 4 crosses above EMA 9 and EMA 18, and EMA 9 crosses above EMA 18
            if (
                prev_row['EMA_4'] <= prev_row['EMA_9'] and
                latest_row['EMA_4'] > latest_row['EMA_9'] and
                latest_row['EMA_4'] > latest_row['EMA_18'] and
                prev_row['EMA_9'] <= prev_row['EMA_18'] and
                latest_row['EMA_9'] > latest_row['EMA_18']
            ):
                send_push_notification(f"{symbol} Buy Signal", "EMA 4 crossed above EMA 9 and EMA 18, and EMA 9 crossed above EMA 18.")

            # Sell Signal: EMA 4 crosses below EMA 9 and EMA 18, and EMA 9 crosses below EMA 18
            elif (
                prev_row['EMA_4'] >= prev_row['EMA_9'] and
                latest_row['EMA_4'] < latest_row['EMA_9'] and
                latest_row['EMA_4'] < latest_row['EMA_18'] and
                prev_row['EMA_9'] >= prev_row['EMA_18'] and
                latest_row['EMA_9'] < latest_row['EMA_18']
            ):
                send_push_notification(f"{symbol} Sell Signal", "EMA 4 crossed below EMA 9 and EMA 18, and EMA 9 crossed below EMA 18.")

    except BinanceAPIException as e:
        print(f"Error fetching data for {symbol}: {e}")
        time.sleep(10)  # Retry after a delay if needed
    except Exception as e:
        print(f"Unexpected error for {symbol}: {e}")
