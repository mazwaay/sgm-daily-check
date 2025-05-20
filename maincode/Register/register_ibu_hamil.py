import requests
import os
import datetime
from playwright.async_api import async_playwright
import asyncio
from dotenv import load_dotenv
import pytz
import traceback
from faker import Faker

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
USERNAME = os.getenv("USERNAME_CRED")
PASSWORD = os.getenv("PASSWORD_CRED")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
USERNAME_CRED = os.getenv("USERNAME_CRED")
PASSWORD_CRED = os.getenv("PASSWORD_CRED")

# Initialize Faker
fake = Faker('id_ID')

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

async def open_sgm():
    jakarta_tz = pytz.timezone("Asia/Jakarta")
    timestamp = datetime.datetime.now(jakarta_tz).strftime("%d%m%Y_%H%M%S")
    screenshot_filename = f"temp_screenshot_{timestamp}.png"

    report = {
        "timestamp": timestamp,
        "steps": [],
        "status": "*success*",
        "error": None,
        "failed_step": None
    }

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(viewport={"width": 1920, "height": 1080})
            page = await context.new_page()

            try:
                # Step 1: Open website with basic auth
                current_step = 1
                step_desc = "Open the website with basic auth credentials"
                auth_url = f"https://{USERNAME_CRED}:{PASSWORD_CRED}@uat.generasimaju.co.id"
                await page.goto(auth_url)
                report["steps"].append(f"{current_step}. {step_desc}")
                print(f"Step {current_step}: {step_desc}")

                # Step 2: Wait for page to load
                current_step = 2
                step_desc = "Wait for page to load"
                await page.wait_for_timeout(3000)
                report["steps"].append(f"{current_step}. {step_desc}")
                print(f"Step {current_step}: {step_desc}")

                # Step 3: Click cookie button
                current_step = 3
                step_desc = "Click the Aktifkan Semua Cookie button"
                await page.locator("text=Aktifkan Semua Cookie").click()
                report["steps"].append(f"{current_step}. {step_desc}")
                print(f"Step {current_step}: {step_desc}")

                # Step 4: Click register button
                current_step = 4
                step_desc = "Click the register button in header"
                await page.click("text=Daftar")
                report["steps"].append(f"{current_step}. {step_desc}")
                print(f"Step {current_step}: {step_desc}")

                # Step 5: Fill nama lengkap with random name
                current_step = 5
                random_name = fake.name()
                step_desc = f"Input nama lengkap: {random_name}"
                await page.fill("//input[@id='namalengkap']", random_name)
                report["steps"].append(f"{current_step}. {step_desc}")
                print(f"Step {current_step}: {step_desc}")

                current_step = 6
                step_desc = f"Input nomor ponsel: (secret)"
                await page.fill('//*[@id="handphone"]', PHONE_NUMBER)
                report["steps"].append(f"{current_step}. {step_desc}")
                print(f"Step {current_step}: {step_desc}")

                current_step = 7
                step_desc = f"Input password: (secret)"
                await page.fill('//*[@id="password-register"]', PASSWORD)
                report["steps"].append(f"{current_step}. {step_desc}")
                print(f"Step {current_step}: {step_desc}")

                current_step = 8
                step_desc = f"Select kondisi bunda: sedang hamil"
                await page.getByRole('kondisi-bunda').fill('Sedang Hamil')
                report["steps"].append(f"{current_step}. {step_desc}")
                print(f"Step {current_step}: {step_desc}")

                # Screenshot hasil
                await page.screenshot(path=screenshot_filename, full_page=False)
                report["screenshot"] = screenshot_filename

            except Exception as e:
                report["status"] = "*failed*"
                report["error"] = str(e)
                report["failed_step"] = current_step
                print(f"ERROR at Step {current_step}: {step_desc}")
                print(f"Error details: {str(e)}")
                traceback.print_exc()
                
                try:
                    await page.screenshot(path=screenshot_filename, full_page=False)
                    report["screenshot"] = screenshot_filename
                except:
                    report["screenshot"] = None
                    print("Failed to take screenshot on error")

            finally:
                await browser.close()
                report["steps"].append(f"{current_step+1}. Close the browser")

    except Exception as e:
        report["status"] = "*failed*"
        report["error"] = str(e)
        print(f"Error initializing browser: {str(e)}")
        traceback.print_exc()

    # Send report to Telegram
    try:
        caption_time = datetime.datetime.now(jakarta_tz).strftime("%d-%m-%Y %H:%M:%S")
        caption_steps = "\n".join(report["steps"])
        
        if report["error"]:
            error_msg = f"\n\nError at Step {report['failed_step']}:\n```\n{report['error']}\n```"
        else:
            error_msg = ""
            
        caption = f"Update Time Zone Test: {report['status']}\n\nTest steps:\n{caption_steps}{error_msg}\n\nCreate on: {caption_time}"
        
        if report.get("screenshot") and os.path.exists(report["screenshot"]):
            response = send_telegram_photo(report["screenshot"], caption=caption)
            if response and response.status_code != 200:
                print(f"Failed to send photo, status code: {response.status_code}")
                send_telegram_message(caption)
        else:
            print("No screenshot available, sending text message only")
            send_telegram_message(caption)
            
    except Exception as e:
        print(f"Failed to send report to Telegram: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(open_sgm())