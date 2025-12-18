"""
Trading strategy logic - 4-hour swing trading
"""
import pandas as pd
import talib
from typing import Dict, Optional

class SwingStrategy:
    def __init__(self):
        self.timeframe = "4h"
        self.pairs = ["BTCUSDT", "ETHUSDT"]
        
    def analyze(self, df: pd.DataFrame) -> Dict:
        """Analyze 4h chart for swing trade setups"""
        if len(df) < 100:
            return {"signal": "HOLD", "reason": "Insufficient data"}
        
        # Calculate indicators
        df['EMA_20'] = talib.EMA(df['close'], timeperiod=20)
        df['EMA_50'] = talib.EMA(df['close'], timeperiod=50)
        df['RSI'] = talib.RSI(df['close'], timeperiod=14)
        
        # Get latest values
        current_close = df['close'].iloc[-1]
        current_rsi = df['RSI'].iloc[-1]
        prev_rsi = df['RSI'].iloc[-2]
        
        # 1. Trend Filter
        is_uptrend = df['EMA_20'].iloc[-1] > df['EMA_50'].iloc[-1]
        
        # 2. Support/Resistance Levels
        recent_low = df['low'].iloc[-20:].min()
        recent_high = df['high'].iloc[-20:].max()
        
        # 3. RSI Conditions
        is_oversold = current_rsi < 35 and prev_rsi < current_rsi
        is_overbought = current_rsi > 65 and prev_rsi > current_rsi
        
        # 4. Generate Signals
        if is_uptrend and is_oversold and current_close <= recent_low * 1.02:
            stop_loss = recent_low * 0.99
            return {
                "signal": "BUY",
                "reason": "Uptrend pullback to support with RSI oversold",
                "entry": current_close,
                "stop_loss": stop_loss,
                "confidence": "MEDIUM"
            }
        elif not is_uptrend and is_overbought and current_close >= recent_high * 0.98:
            stop_loss = recent_high * 1.01
            return {
                "signal": "SELL",
                "reason": "Resistance test with RSI overbought",
                "entry": current_close,
                "stop_loss": stop_loss,
                "confidence": "MEDIUM"
            }
        
        return {"signal": "HOLD", "reason": "No quality setup found"}
    
    def fetch_klines(self, client, symbol: str, limit: int = 100) -> pd.DataFrame:
        """Fetch kline data from Binance"""
        klines = client.get_klines(
            symbol=symbol,
            interval=self.timeframe,
            limit=limit
        )
        
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base', 'taker_buy_quote', 'ignore'
        ])
        
        # Convert to numeric
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = pd.to_numeric(df[col])
        
        return df