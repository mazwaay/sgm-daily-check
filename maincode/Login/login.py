import requests
import os
import datetime
from playwright.async_api import async_playwright
import asyncio
from dotenv import load_dotenv
import pytz

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
USERNAME = os.getenv("USERNAME_CRED")
PASSWORD = os.getenv("PASSWORD_CRED")

# Telegram configuration
def send_telegram_message(text, chat_id=CHAT_ID):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=payload)
    return response

def send_telegram_photo(photo_path, chat_id=CHAT_ID, caption=""):
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

# Main async function
async def open_sgm():
    # Get the current time in Jakarta timezone (WIB)
    jakarta_tz = pytz.timezone("Asia/Jakarta")
    timestamp = datetime.datetime.now(jakarta_tz).strftime("%d%m%Y_%H%M%S")
    
    screenshot_filename = f"temp_screenshot_{timestamp}.png"

    report = {
        "timestamp": timestamp,
        "steps": [],
        "status": "*success*"
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        try:
            # Gunakan HTTP Basic Auth pada URL
            auth_url = f"https://{USERNAME}:{PASSWORD}@uat.generasimaju.co.id"
            await page.goto(auth_url)
            report["steps"].append("Open the website with basic auth credentials.")
            print("Open the website with basic auth credentials.")

            # Tunggu sampai halaman benar-benar termuat (jika ada elemen spesifik bisa ditambahkan)
            await page.wait_for_timeout(3000)

            # Screenshot hasil login
            await page.screenshot(path=screenshot_filename, full_page=False)
            report["screenshot"] = screenshot_filename

        except Exception as e:
            report["status"] = "*failed*"
            report["error"] = str(e)
        
        finally:
            await browser.close()
            report["steps"].append("Close the browser.")

            if os.path.exists(screenshot_filename):
                caption_time = datetime.datetime.now(jakarta_tz).strftime("%d-%m-%Y %H:%M:%S")
                caption_steps = "\n".join([f"{idx+1}. {step}" for idx, step in enumerate(report["steps"])])
                caption = f"Update Time Zone Test: {report['status']}\n\nTest step:\n{caption_steps}\n\nCreate on:{caption_time}"
                
                response = send_telegram_photo(screenshot_filename, caption=caption)
                print("Status kirim foto:", response.status_code)
                os.remove(screenshot_filename)

if __name__ == "__main__":
    asyncio.run(open_sgm())
