import requests
import os
import datetime
import asyncio
from dotenv import load_dotenv
import pytz
import time
import sys

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")  
CHAT_ID = os.getenv("CHAT_ID")
MONITOR_URL = os.getenv("MONITOR_URL", "https://www.generasimaju.co.id/")
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
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"Gagal mengirim notifikasi Telegram: {response.text}")
    except Exception as e:
        print(f"Error saat mengirim ke Telegram: {str(e)}")

class WebsiteMonitor:
    def __init__(self):
        self.previous_status = None
        self.current_status = None
        self.jakarta_tz = pytz.timezone("Asia/Jakarta")
        self.is_first_check = True
        self.last_down_notification_time = 0
        self.down_notification_interval = 3600  # Kirim notifikasi down setiap 1 jam

    def get_current_time(self):
        return datetime.datetime.now(self.jakarta_tz).strftime("%d-%m-%Y %H:%M:%S")

    def create_status_message(self, response_time=None):
        if self.current_status == 200:
            status_emoji = "🟢"
            status_text = f"Status: `{self.current_status}`"
        else:
            status_emoji = "🔴"
            status_text = f"Status: `{self.current_status}`" if isinstance(self.current_status, int) else f"Error: `{self.current_status}`"
        
        if response_time is not None:
            status_text += f" | Response: `{response_time:.2f}s`"
        
        message = (
            f"{status_emoji} *Website Monitor*\n"
            f"URL: `{MONITOR_URL}`\n"
            f"{status_text}\n"
            f"Waktu: `{self.get_current_time()}`"
        )
        
        if self.previous_status is not None and self.current_status != self.previous_status:
            message += f"\n\nSebelumnya: `{self.previous_status}`"
            
        return message

    async def check_website_status(self):
        try:
            start_time = time.time()
            response = requests.get(
                MONITOR_URL,
                timeout=MONITOR_TIMEOUT
            )
            response_time = time.time() - start_time
            self.current_status = response.status_code

            # Kirim notifikasi jika:
            # 1. Status berubah (dari up ke down atau sebaliknya)
            # 2. Ini pengecekan pertama
            # 3. Masih down dan sudah lewat interval notifikasi
            should_notify = (
                self.current_status != self.previous_status or
                self.is_first_check or
                (self.current_status != 200 and 
                 time.time() - self.last_down_notification_time >= self.down_notification_interval)
            )

            if should_notify:
                message = self.create_status_message(response_time)
                send_telegram_message(message)
                
                if self.current_status != 200:
                    self.last_down_notification_time = time.time()

            self._log_status(response_time)

        except requests.exceptions.RequestException as e:
            self.current_status = str(e)
            
            # Kirim notifikasi error jika:
            # 1. Status berubah
            # 2. Ini pengecekan pertama
            # 3. Sudah lewat interval notifikasi
            should_notify = (
                self.previous_status != self.current_status or
                self.is_first_check or
                time.time() - self.last_down_notification_time >= self.down_notification_interval
            )
            
            if should_notify:
                message = self.create_status_message()
                send_telegram_message(message)
                self.last_down_notification_time = time.time()
                
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

        # Kirim notifikasi mulai monitoring
        send_telegram_message(
            f"🚀 *Memulai Monitoring*\n"
            f"URL: `{MONITOR_URL}`\n"
            f"Interval: `{MONITOR_INTERVAL} detik`\n"
            f"Waktu: `{self.get_current_time()}`"
        )

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