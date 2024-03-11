# from playwright.sync_api import sync_playwright
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import settings
import re


if __name__ == "__main__":
    print("Launching " + ("Headless " if settings.headless_browser else "") + "Browser...")

    options = webdriver.ChromeOptions()
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-extensions")
    options.headless = settings.headless_browser
    options.capabilities["timeouts"] = {
      "implicit": settings.default_timeout,
      "pageLoad": settings.default_timeout,
      "script": settings.default_timeout
    }

    # driver = webdriver.Chrome(options=options)
    driver = uc.Chrome(options=options)

    print(f"Going to '{settings.MIDJOURNEY_URL}'...")

    # breakpoint()

    driver.get(settings.MIDJOURNEY_URL)
    # driver.get("https://www.google.com/search?q=midjourney+feed")
    navigator_webdriver = driver.execute_script('return navigator.webdriver')
    print(f"navigator.webdriver: {navigator_webdriver}")

    # breakpoint()

    # curr_url = page.url
    # not_curr_url_regex = re.compile('^(?!' + curr_url + ')')

    # # page.goto(midjourney_anchor.get_attribute("href"))

    # # first_result_loc = page.locator(

    # page.wait_for_load_state("load")

    # page_scroll_selector = '#pageScroll'
    # page.wait_for_selector(page_scroll_selector, state='visible')
    # page_scroll_loc = page.locator(page_scroll_selector).first

    # screenshot_filename = "page.png"
    # page.screenshot(path=screenshot_filename)
    # print(f"Saved screenshot to '{screenshot_filename}'...")

    with open("get_bg_cover_links.js") as f:
      js_script = f.read()

    # breakpoint()

    driver.set_script_timeout(30)
    res = driver.execute_script(js_script)

    # breakpoint()

    wait = WebDriverWait(driver, 5)
    element_locator = (By.CSS_SELECTOR, '#__hidden_bg_text_area')
    element = wait.until(EC.presence_of_element_located(element_locator))

    # now `res` is actionable... (or can be grabbed via textarea)
    print("Scraped:")
    print(res)

    print()
