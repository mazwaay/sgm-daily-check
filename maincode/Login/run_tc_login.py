import asyncio
from playwright.async_api import async_playwright

# Import semua file Playwright
import login_with_password
import login_only_input_password
import login_only_input_phoneNumber
import login_with_invalid_phoneNumber
import login_with_invalid_phoneNumber2

# Fungsi untuk menjalankan setiap file Playwright
async def run_all():
    async with async_playwright() as p:
        await login_with_password.open_sgm()
        await login_only_input_password.open_sgm()
        await login_only_input_phoneNumber.open_sgm()
        await login_with_invalid_phoneNumber.open_sgm()
        await login_with_invalid_phoneNumber2.open_sgm()

if __name__ == "__main__":
    asyncio.run(run_all())