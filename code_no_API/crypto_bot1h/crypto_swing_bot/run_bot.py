#!/usr/bin/env python3
"""
Main bot launcher
"""
import sys
import os
import signal

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\n🛑 Bot stopped by user (Ctrl+C)")
    sys.exit(0)

def print_banner():
    """Print startup banner"""
    from config.keys import STARTING_CAPITAL, RISK_PER_TRADE
    
    banner = f"""
    {'🚀'*20}
    ╔═══════════════════════════════════════════════════╗
    ║        CRYPTO SWING TRADING BOT - $100 Edition    ║
    ║             SAFE MODE (Paper Trading)             ║
    ╚═══════════════════════════════════════════════════╝
    {'💰'*20}
    
    📊 Configuration:
    • Mode: SAFE MODE (No real trades)
    • Capital: ${STARTING_CAPITAL}
    • Risk/Trade: {RISK_PER_TRADE*100}%
    • Max Positions: 1
    
    ⚠️  Warnings:
    • Bot is running in PAPER TRADING mode
    • No real orders will be placed
    • Check trading_bot.log for details
    
    📱 Controls:
    • Ctrl+C to stop the bot
    • Check Telegram for trade alerts
    • Monitor Excel file for logs
    
    {'🔧'*20}
    """
    print(banner)

def main():
    """Main entry point"""
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Print banner
    print_banner()
    
    # Start the bot
    print("\n" + "="*60)
    print("Starting trading bot in SAFE MODE...")
    print("="*60)
    
    try:
        from core.bot import SwingTradingBot
        bot = SwingTradingBot()
        bot.run()
        
    except KeyboardInterrupt:
        print("\n\nBot stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()