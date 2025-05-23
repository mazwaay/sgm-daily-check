import requests
import os
import datetime
from playwright.async_api import async_playwright
import asyncio
from dotenv import load_dotenv
import pytz
import traceback
from faker import Faker  # Import Faker library

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
USERNAME = os.getenv("USERNAME_CRED")
PASSWORD = os.getenv("PASSWORD_CRED")

# Initialize Faker
fake = Faker('id_ID')  # 'id_ID' untuk data Indonesia

# Telegram configuration
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

def send_telegram_photo(photo_path, chat_id=CHAT_ID, caption=""):
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
        print(f"Failed to send Telegram photo: {str(e)}")
        return None
    finally:
        if os.path.exists(photo_path):
            try:
                os.remove(photo_path)
            except:
                pass

# Main async function
async def open_sgm():
    # Get the current time in Jakarta timezone (WIB)
    jakarta_tz = pytz.timezone("Asia/Jakarta")
    timestamp = datetime.datetime.now(jakarta_tz).strftime("%d%m%Y_%H%M%S")
    
    screenshot_filename = f"temp_screenshot_{timestamp}.png"

    report = {
        "timestamp": timestamp,
        "steps": [],
        "status": "*success*",
        "error": None
    }

    try:
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

                await page.locator("text=Aktifkan Semua Cookie").click()
                report["steps"].append("Click the Aktifkan Semua Cookie button.")
                print("Click the Aktifkan Semua Cookie button.")

                await page.click("text=Daftar")
                report["steps"].append("Click the register button in header.")
                print("Click the register button in header.")

                # Generate random name using Faker
                random_name = fake.name()
                await page.fill("//input[@id='namalengkap']", name)
                report["steps"].append(f"Input nama lengkap: {name}")
                print(f"Input nama lengkap: {name}")

                # Screenshot hasil
                await page.screenshot(path=screenshot_filename, full_page=False)
                report["screenshot"] = screenshot_filename

            except Exception as e:
                report["status"] = "*failed*"
                report["error"] = str(e)
                print(f"Error during execution: {str(e)}")
                traceback.print_exc()  # Print full traceback
                
                # Take screenshot on error
                try:
                    await page.screenshot(path=screenshot_filename, full_page=False)
                    report["screenshot"] = screenshot_filename
                except:
                    report["screenshot"] = None
                    print("Failed to take screenshot on error")

            finally:
                await browser.close()
                report["steps"].append("Close the browser.")

    except Exception as e:
        report["status"] = "*failed*"
        report["error"] = str(e)
        print(f"Error initializing browser: {str(e)}")
        traceback.print_exc()

    # Send report to Telegram
    try:
        caption_time = datetime.datetime.now(jakarta_tz).strftime("%d-%m-%Y %H:%M:%S")
        caption_steps = "\n".join([f"{idx+1}. {step}" for idx, step in enumerate(report["steps"])])
        
        if report["error"]:
            error_msg = f"\n\nError:\n```\n{report['error']}\n```"
        else:
            error_msg = ""
            
        caption = f"Update Time Zone Test: {report['status']}\n\nTest step:\n{caption_steps}{error_msg}\n\nCreate on: {caption_time}"
        
        if report.get("screenshot") and os.path.exists(report["screenshot"]):
            response = send_telegram_photo(report["screenshot"], caption=caption)
            if response and response.status_code != 200:
                print(f"Failed to send photo, status code: {response.status_code}")
                send_telegram_message(caption)  # Fallback to text message
        else:
            print("No screenshot available, sending text message only")
            send_telegram_message(caption)
            
    except Exception as e:
        print(f"Failed to send report to Telegram: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(open_sgm())
    