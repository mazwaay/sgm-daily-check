from playwright.sync_api import sync_playwright
import sys

sys.stdout.reconfigure(encoding='utf-8')

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--start-maximized"])
        context = browser.new_context(no_viewport=True)
        page = context.new_page()

        page.goto("https://www.generasimaju.co.id/")
        page.wait_for_load_state("load")

        # Klik cookie
        try:
            page.locator("#footer_tc_privacy_button").click(timeout=5000)
            print("Clicked cookie button.")
        except Exception as e:
            print("Cookie button not found:", str(e))

        # Klik Masuk (ambil elemen pertama)
        try:
            page.locator("text=Masuk").nth(0).click(timeout=5000)
            print("Clicked 'Masuk' button.")
        except Exception as e:
            print("Masuk button not found:", str(e))

        # Input phone number
        try:
            page.locator("#phone-number").fill("081310096543")
            print("Filled phone number.")
        except Exception as e:
            print("Phone input not found:", str(e))

        # Input password
        try:
            page.locator("#password-login").fill("Password1!")
            print("Filled password.")
        except Exception as e:
            print("Password input not found:", str(e))

        # Klik tombol masuk
        try:
            page.locator("#handphone-submit").click(timeout=5000)
            print("Clicked 'Masuk' button.")
        except Exception as e:
            print("Login button not found:", str(e))

        page.wait_for_timeout(5000)
        browser.close()

if __name__ == "__main__":
    main()
