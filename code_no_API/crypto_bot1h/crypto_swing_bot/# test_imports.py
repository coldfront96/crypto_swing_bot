# test_imports.py
# Copy and paste these lines into your VS Code terminal to test each package.
import pandas as pd
print(f"✅ Pandas {pd.__version__}")

import numpy as np
print(f"✅ NumPy {np.__version__}")

from binance.client import Client
print("✅ python-binance")

import talib
print("✅ TA-Lib")

from telegram import Bot
print("✅ python-telegram-bot")

import schedule
print("✅ schedule")

import openpyxl
print("✅ openpyxl")

import requests
print("✅ requests")

from dotenv import load_dotenv
print("✅ python-dotenv")

print("\n🎉 All core packages imported successfully!")