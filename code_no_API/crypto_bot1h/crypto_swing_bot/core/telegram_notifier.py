"""
Telegram notifications for iPhone
"""
import requests
from datetime import datetime
import logging
from typing import Dict

class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """Send message to Telegram"""
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            logging.error(f"Failed to send Telegram message: {e}")
            return False
    
    def send_trade_alert(self, trade_data: Dict):
        """Send trade entry/exit alert with color-coded bot identifier"""
        
        # Get bot frequency with default
        bot_freq = trade_data.get('bot_frequency', 'MAIN')
        
        # Color-coded emojis for each bot frequency
        emoji_map = {
            '4H': '🐢',      # Turtle = Slow & steady (4-hour)
            '3H': '🚶',      # Walker = Medium pace (3-hour)  
            '2H': '🚴',      # Biker = Faster (2-hour)
            '1H': '🚀',      # Rocket = Fastest (1-hour)
            'MAIN': '🤖'     # Default robot
        }
        
        # Get the appropriate emoji
        bot_emoji = emoji_map.get(bot_freq, '🤖')
        
        if trade_data['action'] == 'ENTRY':
            message = f"""
{bot_emoji} <b>TRADE ENTRY [{bot_freq} Bot]</b>
━━━━━━━━━━━━━━━━━━
<b>Symbol:</b> {trade_data['symbol']}
<b>Side:</b> {trade_data['side']}
<b>Bot:</b> {bot_emoji} {bot_freq} Scan
<b>Entry Price:</b> ${trade_data['entry_price']:.2f}
<b>Quantity:</b> {trade_data['quantity']:.6f}
<b>Stop Loss:</b> ${trade_data.get('stop_loss', 'N/A')}
<b>Take Profit:</b> ${trade_data.get('take_profit', 'N/A')}
━━━━━━━━━━━━━━━━━━
<b>Reason:</b> {trade_data.get('reason', 'N/A')}
<b>Strategy:</b> {trade_data.get('strategy', 'Swing')}
<b>Confidence:</b> {trade_data.get('confidence', 'MEDIUM')}
━━━━━━━━━━━━━━━━━━
<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        else:  # EXIT
            pnl_usd = trade_data.get('pnl_usd', 0)
            pnl_emoji = "📈" if pnl_usd > 0 else "📉"
            
            message = f"""
{bot_emoji} <b>TRADE EXIT [{bot_freq} Bot]</b>
━━━━━━━━━━━━━━━━━━
<b>Symbol:</b> {trade_data['symbol']}
<b>Side:</b> {trade_data['side']}
<b>Bot:</b> {bot_emoji} {bot_freq} Scan
<b>Exit Price:</b> ${trade_data['exit_price']:.2f}
<b>Entry Price:</b> ${trade_data.get('entry_price', 'N/A')}
<b>Duration:</b> {trade_data.get('duration', 'N/A')}
━━━━━━━━━━━━━━━━━━
<b>P&L:</b> {pnl_emoji} ${pnl_usd:.2f}
<b>P&L %:</b> {trade_data.get('pnl_percent', 0):.2f}%
<b>Reason:</b> {trade_data.get('exit_reason', 'N/A')}
━━━━━━━━━━━━━━━━━━
<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>
"""
        return self.send_message(message)