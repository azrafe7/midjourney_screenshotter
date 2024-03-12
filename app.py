from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

import argparse
import settings
import re
from pathlib import Path


if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument("-o", "--output", type=str, default=settings.output_folder, help=f"output folder (defaults to settings.output_folder: '{settings.output_folder}')")
  args = parser.parse_args()

  # override output_folder
  if args.output:
    settings.output_folder = args.output

  with sync_playwright() as p:
    print("Launching " + ("Headless " if settings.headless_browser else "") + "Browser...")

    browser = p.chromium.launch(headless=settings.headless_browser)
    context = browser.new_context(user_agent=settings.user_agent)
    context.set_default_timeout(settings.default_timeout)

    # use stealth mode
    stealth_sync(context)
    page = context.new_page()

    print(f"Going to '{settings.MIDJOURNEY_URL}'...")

    # stealth_sync(page)
    page.goto(settings.MIDJOURNEY_URL)

    nav_webdriver = page.evaluate("navigator.webdriver")
    print(f"navigator.webdriver: {nav_webdriver}") # should be None if stealth mode is working

    page.wait_for_load_state("load")

    page_scroll_selector = '#pageScroll'
    page.wait_for_selector(page_scroll_selector, state='visible')
    page_scroll_loc = page.locator(page_scroll_selector).first

    output_folder = Path(settings.output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    print(f"Output folder: '{output_folder}'")

    screenshot_filename = output_folder / Path("page.png")
    page.screenshot(path=screenshot_filename)
    print(f"Saved page screenshot to '{screenshot_filename}'...")

    print("Scrolling to collect links...")

    # inject code to scroll and collect links
    with open("get_bg_cover_links.js") as f:
      js_script = f.read()

    links_info = page.evaluate(js_script)

    print("Reached end of page. Creating download links...")

    # load createDownloadAnchorFor() function
    with open("create_download_anchor_for.js") as f:
      js_create_download = f.read()

    num_items = len(links_info)
    for idx, item in enumerate(links_info[:]):
      imgURL = item['urls'][-1]
      print(f"[{idx+1}/{num_items}] Fetching '{imgURL}'...")

      download_anchor_id = page.evaluate(js_create_download, [imgURL, None])
      download_loc = page.locator('#' + download_anchor_id).first

      # start waiting for the download
      with page.expect_download() as download_info:
        # perform the action that initiates download
        download_loc.click()
      download = download_info.value

      # wait for the download process to complete and save the downloaded file
      filename = output_folder / Path(download.suggested_filename)
      download.save_as(filename)
      print(f"Saved to '{filename}'")

    print("")
    print(f"{num_items} links processed. Exiting...")

    context.close()
    browser.close()
