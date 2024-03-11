from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
# from undetected_playwright import stealth_sync
import settings


if __name__ == "__main__":
  with sync_playwright() as p:
    print("Launching " + ("Headless " if settings.headless_browser else "") + "Browser...")

    browser = p.chromium.launch(headless=settings.headless_browser)
    context = browser.new_context(user_agent=settings.user_agent)
    context.set_default_timeout(settings.default_timeout)

    stealth_sync(context)
    page = context.new_page()

    nav_webdriver = page.evaluate("navigator.webdriver")
    print(f"navigator.webdriver: {nav_webdriver}")

    print(f"Going to '{settings.MIDJOURNEY_URL}'...")

    # stealth_sync(page)
    page.goto(settings.MIDJOURNEY_URL)

    nav_webdriver = page.evaluate("navigator.webdriver")
    print(f"navigator.webdriver: {nav_webdriver}")

    page.wait_for_load_state("load")

    page_scroll_selector = '#pageScroll'
    page.wait_for_selector(page_scroll_selector, state='visible')
    page_scroll_loc = page.locator(page_scroll_selector).first

    screenshot_filename = "page.png"
    page.screenshot(path=screenshot_filename)
    print(f"Saved screenshot to '{screenshot_filename}'...")

    with open("get_bg_cover_links.js") as f:
      js_script = f.read()

    # breakpoint()

    res = page.evaluate(js_script)

    # breakpoxint()

    print("MAYBE REACHED END AND SCRAPED?!")

    browser.close()
