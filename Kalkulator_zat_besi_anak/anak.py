from playwright.sync_api import sync_playwright
import sys
import json
import os

sys.stdout.reconfigure(encoding='utf-8')

COOKIE_PATH = "cookies.json"
ZAT_BESI_URL = "https://www.generasimaju.co.id/tools/kalkulator-zat-besi"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--start-maximized"])
        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        # Load cookies
        if os.path.exists(COOKIE_PATH):
            try:
                with open(COOKIE_PATH, "r", encoding="utf-8") as f:
                    cookies = json.load(f)
                context.add_cookies(cookies)
                print("Loaded cookies from file.")
            except Exception as e:
                print("Failed to load cookies:", str(e))

        # Masuk ke halaman kalkulator
        page.goto(ZAT_BESI_URL)
        page.wait_for_load_state("load")

        # Isi berat badan (dalam kg)
        try:
            page.locator("input[name='weight']").fill("9")
            print("Filled weight: 9 kg")
        except Exception as e:
            print("Failed to fill weight:", str(e))

        # Pilih usia (8 bulan)
        try:
            page.locator("select[name='age']").select_option("8")
            print("Selected age: 8 bulan")
        except Exception as e:
            print("Failed to select age:", str(e))

        # Klik tombol "Hitung Kebutuhan"
        try:
            page.locator("button:has-text('Hitung Kebutuhan')").click()
            print("Clicked 'Hitung Kebutuhan'")
        except Exception as e:
            print("Failed to click 'Hitung Kebutuhan':", str(e))

        # Tunggu hasil muncul (misalnya ditampilkan dalam div hasil)
        page.wait_for_timeout(3000)

        try:
            result_text = page.locator("div.result-container").inner_text()
            print("\n=== HASIL KALKULATOR ===")
            print(result_text)
        except:
            print("Hasil tidak ditemukan atau belum muncul.")

        page.wait_for_timeout(5000)
        browser.close()

if __name__ == "__main__":
    main()
