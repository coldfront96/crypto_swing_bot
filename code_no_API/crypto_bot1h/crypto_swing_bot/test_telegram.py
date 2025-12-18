# test_telegram.py
import requests
import json

# UPDATE THESE WITH YOUR ACTUAL VALUES
BOT_TOKEN = "yourtokenhere"  # Example: "701234567:AAHExample123"
CHAT_ID = "youridhere"      # Example: "1234567890"

def test_telegram():
    print("🤖 Testing Telegram connection...")
    print(f"Token (first 10 chars): {BOT_TOKEN[:10]}...")
    print(f"Chat ID: {CHAT_ID}")
    print("-" * 50)
    
    try:
        # Build the URL
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        
        # Prepare the message data
        data = {
            "chat_id": CHAT_ID,
            "text": "✅ Hello from your Trading Bot!",
            "parse_mode": "HTML"
        }
        
        print(f"Sending request to: {url[:50]}...")
        
        # Send the request
        response = requests.post(url, json=data, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Message sent. Check your Telegram app.")
            result = response.json()
            print(f"Message ID: {result.get('result', {}).get('message_id', 'Unknown')}")
        else:
            print("❌ Request failed.")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out. Check your internet connection.")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Check your internet.")
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")

if __name__ == "__main__":

    test_telegram()
