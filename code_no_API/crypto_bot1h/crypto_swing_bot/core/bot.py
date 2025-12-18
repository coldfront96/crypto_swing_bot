"""
Main trading bot
"""
import schedule
import time
import logging
from datetime import datetime
from typing import Dict, Optional

from core.strategy import SwingStrategy
from core.risk_manager import RiskManager
from core.trade_logger import TradeLogger
from core.telegram_notifier import TelegramNotifier
from config.keys import (
    BINANCE_API_KEY, BINANCE_API_SECRET,
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID,
    USE_TESTNET, STARTING_CAPITAL,
    MAX_POSITIONS, RISK_PER_TRADE
)

from binance.client import Client

class SwingTradingBot:
    def __init__(self):
        # Setup logging
        self.setup_logging()
            
        self.last_api_time = time.time()
     
        # Initialize components
        self.strategy = SwingStrategy()
        self.risk_manager = RiskManager(STARTING_CAPITAL)
        self.risk_manager.risk_per_trade = RISK_PER_TRADE
        self.risk_manager.max_positions = MAX_POSITIONS
        
        self.trade_logger = TradeLogger()
        
        # Connect to Binance.US
        self.client = Client(
            api_key=BINANCE_API_KEY,
            api_secret=BINANCE_API_SECRET,
            tld='us'  # This is crucial for Binance.US
        )
        
        # Setup Telegram
        if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
            self.telegram = TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
            self.telegram.send_message(
                f"🤖 <b>Trading Bot 1h Started</b>\n"
                f"💰 Capital: ${STARTING_CAPITAL}\n"
                f"⚙️  Risk/Trade: {RISK_PER_TRADE*100}%\n"
                f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            self.logger.info("Telegram notifications enabled")
        else:
            self.telegram = None
            self.logger.warning("Telegram notifications disabled")
        
        # Track active trades
        self.active_trades = {}
        self.trade_count = 0
        self.is_running = True
        
        self.logger.info(f"Bot initialized with ${STARTING_CAPITAL} capital")
    
    def setup_logging(self):
        """Configure logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('trading_bot_1h.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def check_account_balance(self):
        """Get current USDT balance"""
        try:
            balance = self.client.get_asset_balance(asset='USDT')
            available = float(balance['free'])
            self.logger.info(f"Available USDT: ${available:.2f}")
            return available
        except Exception as e:
            self.logger.error(f"Balance check failed: {e}")
            return 0
    
    def scan_markets(self):
        """Scan all markets for trading setups"""
        signals = {}
        
        for symbol in self.strategy.pairs:
            try:
                # Fetch market data
                df = self.strategy.fetch_klines(self.client, symbol)
                
                # Analyze for signals
                analysis = self.strategy.analyze(df)
                
                if analysis['signal'] != 'HOLD':
                    signals[symbol] = analysis
                    self.logger.info(f"Signal found: {symbol} - {analysis['signal']}")
                    
            except Exception as e:
                self.logger.error(f"Error analyzing {symbol}: {e}")
        
        return signals
    
    def execute_trade(self, symbol: str, signal: Dict):
        """Execute a trade (SAFE MODE - NO REAL TRADES)"""
        try:
            # Check if already trading this symbol
            if symbol in self.active_trades:
                self.logger.info(f"Already trading {symbol}")
                return
            
            # Calculate position
            entry = signal['entry']
            stop_loss = signal['stop_loss']
            side = "LONG" if signal['signal'] == 'BUY' else 'SHORT'
            
            quantity = self.risk_manager.calculate_position_size(entry, stop_loss)
            if quantity <= 0:
                self.logger.warning(f"Invalid position size for {symbol}")
                return
            
            # Calculate take profit
            take_profit = self.risk_manager.calculate_take_profit(entry, stop_loss, side)
            
            # Prepare trade data
            trade_data = {
                'symbol': symbol,
                'side': side,
                'entry_price': entry,
                'quantity': quantity,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'risk_reward': f"{self.risk_manager.min_risk_reward}:1",
                'reason': signal.get('reason', ''),
                'strategy': 'Swing_Trading',
                'confidence': signal.get('confidence', 'MEDIUM'),
                'notes': f"Paper Trade #{self.trade_count + 1}"
            }
            
            # Log to Excel (but don't actually trade)
            trade_id = self.trade_logger.log_trade_entry(trade_data)
            
            # Send Telegram alert
            if self.telegram:
                alert_data = {
                    'action': 'ENTRY',
                    'symbol': symbol,
                    'side': side,
                    'entry_price': entry,
                    'quantity': quantity,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'reason': signal.get('reason', ''),
                    'strategy': 'Swing',
                    'confidence': signal.get('confidence', 'MEDIUM'),
                    'bot_frequency': '1H'  # 4-hour bot
                }
                self.telegram.send_trade_alert(alert_data)
            
            # SIMULATE TRADE (NO REAL MONEY)
            self.logger.info(f"[SAFE MODE] Would {side} {quantity} {symbol} at ${entry}")
            self.active_trades[symbol] = {
                'trade_id': trade_id,
                'side': side,
                'entry': entry,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'quantity': quantity,
                'timestamp': datetime.now(),
                'simulated': True
            }
            self.trade_count += 1
            
            self.logger.info(f"Paper trade executed: {side} {quantity} {symbol}")
            
        except Exception as e:
            self.logger.error(f"Trade execution failed: {e}")
    
    def monitor_trades(self):
        """Monitor active trades for exit conditions"""
        if not self.active_trades:
            return
        
        for symbol, trade in list(self.active_trades.items()):
            try:
                # Get current price
                ticker = self.client.get_symbol_ticker(symbol=symbol)
                current_price = float(ticker['price'])
                exit_reason = None
                
                # Check stop loss
                if trade['side'] == 'LONG' and current_price <= trade['stop_loss']:
                    exit_reason = "STOP_LOSS"
                elif trade['side'] == 'SHORT' and current_price >= trade['stop_loss']:
                    exit_reason = "STOP_LOSS"
                # Check take profit
                elif trade['side'] == 'LONG' and current_price >= trade['take_profit']:
                    exit_reason = "TAKE_PROFIT"
                elif trade['side'] == 'SHORT' and current_price <= trade['take_profit']:
                    exit_reason = "TAKE_PROFIT"
                
                if exit_reason:
                    self.exit_trade(symbol, exit_reason, current_price)
                    
            except Exception as e:
                self.logger.error(f"Error monitoring {symbol}: {e}")
    
    def exit_trade(self, symbol: str, reason: str, exit_price: float):
        """Exit a trade"""
        try:
            trade = self.active_trades.pop(symbol, None)
            if not trade:
                return
            
            # Calculate P&L
            if trade['side'] == 'LONG':
                pnl_usd = (exit_price - trade['entry']) * trade['quantity']
            else:
                pnl_usd = (trade['entry'] - exit_price) * trade['quantity']
            
            pnl_percent = (pnl_usd / (trade['entry'] * trade['quantity'])) * 100
            duration = datetime.now() - trade['timestamp']
            
            # Log to Excel
            if 'trade_id' in trade:
                exit_data = {
                    'exit_price': exit_price,
                    'pnl_usd': pnl_usd,
                    'pnl_percent': pnl_percent,
                    'notes': f"Exit: {reason}"
                }
                self.trade_logger.log_trade_exit(trade['trade_id'], exit_data)
            
            # Send Telegram alert
            if self.telegram:
                alert_data = {
                    'action': 'EXIT',
                    'symbol': symbol,
                    'side': trade['side'],
                    'exit_price': exit_price,
                    'entry_price': trade['entry'],
                    'quantity': trade['quantity'],
                    'duration': str(duration),
                    'pnl_usd': pnl_usd,
                    'pnl_percent': pnl_percent,
                    'exit_reason': reason
                }
                self.telegram.send_trade_alert(alert_data)
            
            self.logger.info(f"Trade exited: {symbol} - {reason} - P&L: ${pnl_usd:.2f}")
            
        except Exception as e:
            self.logger.error(f"Trade exit failed: {e}")
    
    def run_iteration(self):
        """Single trading iteration"""
        if not self.is_running:
            return
        
        self.logger.info("="*60)
        self.logger.info(f"Trading cycle #{self.trade_count + 1}")
        
        # Check account balance
        balance = self.check_account_balance()
        if balance < 10:
            self.logger.warning(f"Insufficient balance: ${balance:.2f}")
            return
        
        # Monitor existing trades
        self.monitor_trades()
        
        # Scan for new setups if we have capacity
        if len(self.active_trades) < self.risk_manager.max_positions:
            signals = self.scan_markets()
            
            # Execute new trades
            for symbol, signal in signals.items():
                if self.is_running:
                    self.execute_trade(symbol, signal)
        
        self.logger.info(f"Cycle complete. Active trades: {len(self.active_trades)}")
        self.logger.info("="*60)
    
    def run(self):
        """Main bot execution loop"""
        self.logger.info("Starting Swing Trading Bot")
        
        # Schedule to run every 4 hours
        schedule.every(1).hours.do(self.run_iteration)
        
        # Initial run
        self.run_iteration()
        
        # Main loop
        self.logger.info("Bot scheduler started")
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            self.logger.info("Bot stopped by user")
            if self.telegram:
                self.telegram.send_message("🛑 Bot stopped by user command")
        except Exception as e:
            self.logger.error(f"Bot crashed: {e}")
            if self.telegram:
                self.telegram.send_message(f"🚨 Bot crashed: {str(e)[:100]}")