from playwright.sync_api import sync_playwright
import settings
import re


if __name__ == "__main__":
  with sync_playwright() as p:
    print("Launching " + ("Headless " if settings.headless_browser else "") + "Browser...")

    browser = p.chromium.launch(headless=settings.headless_browser)
    context = browser.new_context(user_agent=settings.user_agent)
    context.set_default_timeout(settings.default_timeout)

    page = browser.new_page()

    print(f"Going to '{settings.MIDJOURNEY_URL}'...")

    # page.goto(settings.MIDJOURNEY_URL, referer="https://google.com")
    page.goto("https://www.google.com/search?q=midjourney+feed")

    breakpoint()

    midjourney_anchor = page.locator('a[href^="https://www.midjourney.com/showcase"]').first
    if not midjourney_anchor.is_visible():
      breakpoint()

    midjourney_anchor.dispatch_event('click')

    breakpoint()

    curr_url = page.url
    not_curr_url_regex = re.compile('^(?!' + curr_url + ')')

    # page.goto(midjourney_anchor.get_attribute("href"))

    # first_result_loc = page.locator(

    page.wait_for_load_state("load")

    page_scroll_selector = '#pageScroll'
    page.wait_for_selector(page_scroll_selector, state='visible')
    page_scroll_loc = page.locator(page_scroll_selector).first

    screenshot_filename = "page.png"
    page.screenshot(path=screenshot_filename)
    print(f"Saved screenshot to '{screenshot_filename}'...")

    with open("get_bg_cover_links.js") as f:
      js_script = f.read()

    breakpoint()

    res = page.evaluate(js_script)

    breakpoint()


    # browser.close()
