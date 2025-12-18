"""
Test Binance.US live connection
"""
import sys
sys.path.append('.')  # Allows importing from config

from config.keys import BINANCE_API_KEY, BINANCE_API_SECRET
from binance.client import Client

print("🔐 Testing Binance.US LIVE Connection...")
print("=" * 50)

try:
    # Initialize the client for Binance.US
    client = Client(
        api_key=BINANCE_API_KEY,
        api_secret=BINANCE_API_SECRET,
        tld='us'  # This is crucial for Binance.US
    )
    
    # Test server time
    print("1. Testing API connectivity...")
    server_time = client.get_server_time()
    print(f"   ✅ Connected. Server time: {server_time['serverTime']}")
    
    # Get USDT balance
    print("2. Checking account balance...")
    balance = client.get_asset_balance(asset='USDT')
    usdt_balance = float(balance['free'])
    print(f"   ✅ Available USDT Balance: ${usdt_balance:.2f}")
    
    # Test market data
    print("3. Testing market data...")
    ticker = client.get_symbol_ticker(symbol="BTCUSDT")
    print(f"   ✅ BTC Price: ${float(ticker['price']):.2f}")
    
    print("=" * 50)
    print("✅ All connection tests passed!")
    print("\n📋 You can now run the bot in SAFE MODE:")
    print("   python run_bot.py")
    
except Exception as e:
    print("=" * 50)
    print(f"❌ Test Failed:")
    print(f"   {type(e).__name__}: {e}")
    print("\n🔧 Troubleshooting:")
    print("   1. Check API keys in config/keys.py")
    print("   2. Ensure you're connected to Binance.US (not binance.com)")
    print("   3. Verify internet connection")