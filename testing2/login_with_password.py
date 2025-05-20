# login_with_password.py

import os
import datetime
from playwright.async_api import async_playwright
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

async def open_sgm():
    jakarta_tz = pytz.timezone("Asia/Jakarta")
    timestamp = datetime.datetime.now(jakarta_tz).strftime("%d%m%Y_%H%M%S")
    screenshot_filename = f"screenshot_login_with_password_{timestamp}.png"

    report = {
        "timestamp": timestamp,
        "steps": [],
        "status": "*success*",
        "screenshot": None
    }

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(viewport={"width": 1280, "height": 800})
            page = await context.new_page()

            auth_url = f"https://{USERNAME}:{PASSWORD}@uat.generasimaju.co.id"
            await page.goto(auth_url)
            report["steps"].append("Open website with basic auth.")

            await page.wait_for_timeout(3000)
            report["steps"].append("Waited for page to load.")

            await page.screenshot(path=screenshot_filename, full_page=False)
            report["screenshot"] = screenshot_filename
            report["steps"].append("Screenshot taken.")

            await browser.close()
            report["steps"].append("Browser closed.")

    except Exception as e:
        report["status"] = "*fail*"
        report["error"] = str(e)

    # Send screenshot if available
    if report.get("screenshot") and os.path.exists(report["screenshot"]):
        caption = f"*Login with Password*: {report['status']}\n\n"
        caption += "\n".join([f"{i+1}. {step}" for i, step in enumerate(report["steps"])])
        send_telegram_photo(report["screenshot"], caption=caption)
        os.remove(report["screenshot"])  # Optional: remove after sending

    return report

if __name__ == "__main__":
    import asyncio
    asyncio.run(open_sgm())