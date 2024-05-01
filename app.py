from playwright.sync_api import sync_playwright, ViewportSize
from playwright_stealth import stealth_sync

import argparse
import settings
import re
from pathlib import Path
import ffmpeg

RESIZE_WIDTH = 1920
RESIZE_HEIGHT = 1080
IMAGE_WIDTH = 1102
IMAGE_HEIGHT = 620

def set_preferred_theme(page, preferred_theme):
    page.locator('html').evaluate('(node, preferred_theme) => { node.classList.remove("dark", "light"); node.classList.add(preferred_theme); }', arg=preferred_theme)


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
    context = browser.new_context(
        user_agent=settings.user_agent, 
        #viewport=ViewportSize(width=RESIZE_WIDTH, height=RESIZE_HEIGHT)
    )
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

    preferred_theme = 'dark'
    print(f"Setting preferred theme to '{preferred_theme}'...")
    set_preferred_theme(page, preferred_theme)

    page_scroll_selector = '#pageScroll'
    page.wait_for_selector(page_scroll_selector, state='visible')
    page_scroll_loc = page.locator(page_scroll_selector).first

    output_folder = Path(settings.output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    print(f"Output folder: '{output_folder}'")

    print("Scrolling to collect links...")

    # inject code to scroll and collect links
    with open("get_bg_cover_links.js") as f:
      js_script = f.read()

    links_info = page.evaluate(js_script)

    print("Reached end of page. Creating download links...")

    suggested_filename = f'image_{(0):>03d}.png'
    screenshot_filename = output_folder / Path(suggested_filename)
    print(f"Saving page screenshot to '{screenshot_filename}'...")
    # clip_rect = { "x":0, "y":0, "width":1102, "height":620 }
    
    # scroll to top and hide scrollbar
    page.evaluate("""
        scrollElem = document.querySelector('#pageScroll');
        scrollElem.scroll(0,0);
        scrollElem.style.overflowY = 'hidden';
    """)
    # add date string below textArea
    page.evaluate("""
        textArea = document.querySelector('textarea');
        headerDiv = textArea.parentElement.parentElement.parentElement.parentElement;
        div = document.createElement('div');
        // div.textContent = 'MidJourney Showcase - assembled by [AzLabs] ' + new Date().toUTCString();
        dateString = new Date().toUTCString();
        div.style = 'text-align:center; margin-top: 8px; font-variant: all-small-caps;';
        div.innerHTML = `<span style="font-weight:700;">MidJourney</span> Showcase - assembled by <span style="font-weight:700; color:orangered;">[AzLabs]</span> - ${dateString}`;
        headerDiv.appendChild(div);
    """)
    
    page.screenshot(path=screenshot_filename)
    breakpoint()

    # load createDownloadAnchorFor() function
    with open("create_download_anchor_for.js") as f:
      js_create_download = f.read()

    num_items = len(links_info)
    
    links_to_process = links_info[:]
    num_links_to_process = len(links_to_process)

    clip_rect = { "x":82, "y":88, "width":IMAGE_WIDTH, "height":IMAGE_HEIGHT }
    print(f"Using clip_rect: {clip_rect}")

    for idx, item in enumerate(links_to_process):

      ## try to download images directly
      #imgURL = item['urls'][-1]
      #print(f"[{idx + 1}/{num_links_to_process}] Fetching '{imgURL}'...")
      #
      #download_anchor_id = page.evaluate(js_create_download, [imgURL, None])
      #download_loc = page.locator('#' + download_anchor_id).first
      #
      ## start waiting for the download
      #with page.expect_download() as download_info:
      #  # perform the action that initiates download
      #  download_loc.click()
      #download = download_info.value
      #
      ## wait for the download process to complete and save the downloaded file
      #filename = output_folder / Path(download.suggested_filename)
      #download.save_as(filename)
      #print(f"Saved to '{filename}'")

      print(f"[{idx + 1}/{num_links_to_process}] Going to '{item['href']}'...")

      page.goto(item['href'])
      set_preferred_theme(page, preferred_theme)
      page.wait_for_load_state("load")
      
      suggested_filename = f'image_{(idx + 1):>03d}.png'
      filename = output_folder / Path(suggested_filename)
      print(f"Saving screenshot to '{filename}'...")
      page.screenshot(clip=clip_rect, path=filename)

    print("")
    print(f"{num_links_to_process} links processed. Exiting...")

    context.close()
    browser.close()
