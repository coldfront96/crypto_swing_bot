# config/keys.py - CONFIGURE FOR BINANCE.US LIVE TESTING
# NEVER share or commit this file to public git repositories.

# ===== BINANCE.US LIVE API KEYS =====
# Created in your Binance.US account with "Enable Spot & Margin Trading" ONLY.
BINANCE_API_KEY = "YOURKEYHERE"
BINANCE_API_SECRET = "YOURKEYHERE"

# ===== TELEGRAM BOT KEYS (For iPhone notifications) =====
TELEGRAM_BOT_TOKEN = "yourTOKENHERE"  # From @BotFather
TELEGRAM_CHAT_ID = "YOURIDHERE"      # From @userinfobot

# ===== BOT OPERATION MODE =====
USE_TESTNET = False          # MUST be False for Binance.US live API
STARTING_CAPITAL = 40.0    # Your total account size in USDT for risk calculation
TEST_TRADE_AMOUNT = 1.0      # Amount in USDT to use for initial test trades
RISK_PER_TRADE = 0.015      # <-- ADD THIS LINE (1.5% risk per trade)
MAX_POSITIONS = 1