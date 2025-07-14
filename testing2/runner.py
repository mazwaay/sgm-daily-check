import asyncio
from playwright.async_api import async_playwright
import datetime
import pytz
from dotenv import load_dotenv
import os
import requests
import sys
import io

# This script runs multiple test cases using Playwright and sends the results to a Telegram bot.
import login_with_password
import login
import wew

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Telegram notification function
def send_telegram_message(text, chat_id=CHAT_ID):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        response = requests.post(url, data=payload)
        return response
    except Exception as e:
        print(f"Failed to send Telegram message: {str(e)}")
        return None

async def run_all():
    jakarta_tz = pytz.timezone("Asia/Jakarta")
    timestamp = datetime.datetime.now(jakarta_tz).strftime("%d-%m-%Y %H:%M:%S")
    
    # Define test cases
    test_cases = [
        ("Login with Password", login_with_password.open_sgm),
        ("Login", login.open_sgm),
        ("WEW", wew.open_sgm),
    ]
    
    results = []
    total_tests = len(test_cases)
    passed_tests = 0
    failed_tests = 0
    
    async with async_playwright() as p:
        for name, test_func in test_cases:
            try:
                print(f"\nRunning test case: {name}")
                result = await test_func()
                
                if result.get("status") == "*success*":
                    status = "✅ SUCCESS"
                    passed_tests += 1
                else:
                    status = "❌ FAILED"
                    failed_tests += 1
                
                error_msg = f"\n    Error: {result.get('error')}" if result.get("error") else ""
                
                results.append(f"*{name}*: {status}{error_msg}\n")
            except Exception as e:
                status = "❌ FAILED"
                failed_tests += 1
                results.append(f"*{name}*: {status}\n    Error: {str(e)}\n")
                print(f"Error running test {name}: {str(e)}")
    
    summary = (
        f"📊 *Test Automation Report*\n"
        f"⏰ Time: {timestamp}\n"
        f"🔢 Total Tests: {total_tests}\n"
        f"✅ Passed: {passed_tests}\n"
        f"❌ Failed: {failed_tests}\n"
        f"📈 Success Rate: {round((passed_tests/total_tests)*100 if total_tests > 0 else 0)}%\n\n"
        f"*Detailed Results:*\n"
    )
    
    full_report = summary + "\n".join(results)
    console_report = (
        full_report
        .replace("*", "")
        .replace("✅", "[SUCCESS]")
        .replace("❌", "[FAILED]")
        .replace("📊", "[REPORT]")
        .replace("⏰", "[TIME]")
        .replace("🔢", "[COUNT]")
        .replace("📈", "[RATE]")
    )
    
    print("\n" + "="*50)
    print(console_report)
    print("="*50)
    
    send_telegram_message(full_report)

if __name__ == "__main__":
    asyncio.run(run_all())
