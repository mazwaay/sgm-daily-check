import os
import datetime
from playwright.sync_api import sync_playwright
import pytz
import requests
from dotenv import load_dotenv

load_dotenv()
USERNAME = os.getenv("USERNAME_CRED")
PASSWORD = os.getenv("PASSWORD_CRED")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_telegram_photo(photo_path, caption="", chat_id=CHAT_ID):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        with open(photo_path, "rb") as photo:
            files = {"photo": photo}
            payload = {
                "chat_id": chat_id,
                "caption": caption,
                "parse_mode": "Markdown"
            }
            response = requests.post(url, files=files, data=payload)
        return response
    except Exception as e:
        print("Gagal mengirim foto:", e)
        return None

def open_sgm():
    jakarta_tz = pytz.timezone("Asia/Jakarta")
    timestamp = datetime.datetime.now(jakarta_tz).strftime("%d%m%Y_%H%M%S")
    screenshot_filename = f"screenshot_login_{timestamp}.png"

    report = {
        "timestamp": timestamp,
        "steps": [],
        "status": "*success*",
        "screenshot": None
    }

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)  # Jalankan browser visual
            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
            )

            page = context.new_page()

            page.goto("https://generasimaju.co.id", wait_until="load", timeout=60000)
            report["steps"].append("Open the website.")

            print("CAPTCHA mungkin muncul. Silakan selesaikan secara manual.")
            input("Tekan ENTER setelah kamu menyelesaikan CAPTCHA di browser...")

            page.wait_for_timeout(3000)

            page.screenshot(path=screenshot_filename, full_page=False)
            report["screenshot"] = screenshot_filename
            report["steps"].append("Screenshot taken.")

            browser.close()
            report["steps"].append("Browser closed.")

    except Exception as e:
        report["status"] = "*fail*"
        report["error"] = str(e)
        print(f"Terjadi error: {e}")

    # Kirim ke Telegram
    if report.get("screenshot") and os.path.exists(report["screenshot"]):
        caption = f"*Login*: {report['status']}\n\n"
        caption += "\n".join([f"{i+1}. {step}" for i, step in enumerate(report["steps"])])
        send_telegram_photo(report["screenshot"], caption=caption)
        os.remove(report["screenshot"])

    return report

if __name__ == "__main__":
    open_sgm()
