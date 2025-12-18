# crypto_swing_bot
practice run for a crypto swing bot
# Crypto Swing Trading Bot

A Python-based swing trading bot for Binance.US with Telegram notifications and Excel logging.

## Features
- 4-hour swing trading strategy for BTC/USDT and ETH/USDT
- Risk management (1.5% per trade, 2:1 reward:risk)
- Telegram notifications for trade alerts
- Excel logging of all trades with P&L tracking
- Multiple scanning frequencies (1H, 2H, 3H, 4H)

## Setup
1. Clone repository: `git clone https://github.com/YOUR_USERNAME/crypto-swing-bot.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Configure `config/keys.py` with your API keys
4. Run: `python run_bot.py`

## Security Warning
**Never commit API keys!** The `config/keys.py` file is ignored by git.

## License
Private - For personal use only.
