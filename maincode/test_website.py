import requests
import os
import datetime
import asyncio
from dotenv import load_dotenv
import pytz
import time

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
MONITOR_URL = os.getenv("MONITOR_URL", "https://uat.generasimaju.co.id")
MONITOR_INTERVAL = int(os.getenv("MONITOR_INTERVAL", "60"))  # detik
MONITOR_TIMEOUT = int(os.getenv("MONITOR_TIMEOUT", "10"))    # detik

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

class WebsiteMonitor:
    def __init__(self):
        self.previous_status = None
        self.current_status = None
        self.jakarta_tz = pytz.timezone("Asia/Jakarta")
        self.is_first_check = True

    def get_current_time(self):
        return datetime.datetime.now(self.jakarta_tz).strftime("%d-%m-%Y %H:%M:%S")

    async def check_website_status(self):
        try:
            start_time = time.time()
            response = requests.get(
                MONITOR_URL,
                timeout=MONITOR_TIMEOUT
            )
            response_time = time.time() - start_time
            self.current_status = response.status_code

            # Format message
            status_emoji = "🟢" if self.current_status == 200 else "🔴"
            message = (
                f"{status_emoji} *Website Monitor*\n"
                f"URL: `{MONITOR_URL}`\n"
                f"Status: `{self.current_status}`\n"
                f"Response: `{response_time:.2f}s`\n"
                f"Waktu: `{self.get_current_time()}`"
            )

            # Kirim notifikasi jika status berubah atau pertama kali
            if self.current_status != self.previous_status or self.is_first_check:
                if not self.is_first_check:
                    message += f"\n\nSebelumnya: `{self.previous_status}`"
                send_telegram_message(message)
                print(f"[{self.get_current_time()}] Status changed: {self.current_status}")

            self._log_status(response_time)

        except requests.exceptions.RequestException as e:
            self.current_status = str(e)
            message = (
                f"🔴 *Website Monitor - ERROR*\n"
                f"URL: `{MONITOR_URL}`\n"
                f"Error: `{self.current_status}`\n"
                f"Waktu: `{self.get_current_time()}`"
            )
            
            if self.previous_status != self.current_status or self.is_first_check:
                send_telegram_message(message)
                print(f"[{self.get_current_time()}] Error: {self.current_status}")

        finally:
            self.previous_status = self.current_status
            self.is_first_check = False

    def _log_status(self, response_time=None):
        status_type = "UP" if self.current_status == 200 else "DOWN"
        log_msg = f"[{self.get_current_time()}] {status_type}: {self.current_status}"
        if response_time:
            log_msg += f" | Response: {response_time:.2f}s"
        print(log_msg)

    async def start_monitoring(self):
        print(f"Memulai monitoring website: {MONITOR_URL}")
        print(f"Interval pengecekan: {MONITOR_INTERVAL} detik")
        print(f"Timeout request: {MONITOR_TIMEOUT} detik")
        print("Tekan Ctrl+C untuk menghentikan")
        print("-" * 50)

        try:
            while True:
                await self.check_website_status()
                await asyncio.sleep(MONITOR_INTERVAL)
        except KeyboardInterrupt:
            print("\nMonitoring dihentikan oleh pengguna")
            send_telegram_message(
                f"🛑 *Monitoring Dihentikan*\n"
                f"URL: `{MONITOR_URL}`\n"
                f"Status terakhir: `{self.current_status}`\n"
                f"Waktu: `{self.get_current_time()}`"
            )

async def main():
    monitor = WebsiteMonitor()
    await monitor.start_monitoring()

if __name__ == "__main__":
    asyncio.run(main())