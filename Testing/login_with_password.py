# login_with_password.py
import os
import datetime
from playwright.async_api import async_playwright
import pytz
from dotenv import load_dotenv
import requests

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
USERNAME = os.getenv("USERNAME_CRED")
PASSWORD = os.getenv("PASSWORD_CRED")

async def open_sgm():
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
            auth_url = f"https://{USERNAME}:{PASSWORD}@uat.generasimaju.co.id"
            await page.goto(auth_url)
            report["steps"].append("Open the website with basic auth credentials.")
            await page.wait_for_timeout(3000)
            await page.screenshot(path=screenshot_filename, full_page=False)
            report["screenshot"] = screenshot_filename
        except Exception as e:
            report["status"] = "*fail*"
            report["error"] = str(e)
        finally:
            await browser.close()
            report["steps"].append("Close the browser.")
            if os.path.exists(screenshot_filename):
                os.remove(screenshot_filename)
    
    return report
