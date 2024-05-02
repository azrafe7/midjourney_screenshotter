from playwright.sync_api import sync_playwright, ViewportSize
from playwright_stealth import stealth_sync

import argparse
import settings
import os
import re
from pathlib import Path
import shutil
import dateutil
import ffmpeg
import json


VIEWPORT_WIDTH = 1600
VIEWPORT_HEIGHT = 900

RESIZE_WIDTH = 1920
RESIZE_HEIGHT = 1080
SCALING_KEEP_TEMP = True
SCALING_ALGO = "lanczos"

HIDE_SIDEBAR = True
IMAGE_OFFSET_X = 0
IMAGE_OFFSET_Y = 80
IMAGE_WIDTH = 1442
IMAGE_HEIGHT = 810

MAX_LINKS_TO_PROCESS = -1  # set it to -1 to process them all

FFMPEG_QUIET = True


def set_preferred_theme(page, preferred_theme):
    page.locator('html').evaluate('(node, preferred_theme) => { node.classList.remove("dark", "light"); node.classList.add(preferred_theme); }', arg=preferred_theme)

def print_ffmpeg_cmd(cmd):
    print(f"FFMPEG> " + " ".join(cmd.compile()))

def delete_files(self, files):
    try:
        for f in files:
            os.unlink(f)
    except FileNotFoundError as e:
        print("File not found: " + e.filename)
    except OSError:
        print("OSError")

def ffmpeg_resize_image(input_file, output_file, width, height, scaling_algo="bicubic", keep_temp=False):
    # breakpoint()
    input_file_path = Path(input_file)
    original_input_file_path = input_file_path
    output_file_path = Path(output_file)
    needs_temp_file = input_file_path == output_file_path
    if needs_temp_file:
        stem = Path(input_file_path).stem
        input_file_path = Path(input_file_path).with_stem(stem + '_temp')
        shutil.copy(original_input_file_path, input_file_path)  # copy to temp

    cmd = (
        ffmpeg.input(input_file_path.as_posix())
        .filter('scale', width, height)
        .output(
            output_file_path.as_posix(),
            **{
                "update": "true",
                "sws_flags": scaling_algo,
            },
        )
        .overwrite_output()
    )

    print(f"Resizing to {width}:{height} ({scaling_algo})...")
    print_ffmpeg_cmd(cmd)
    cmd.run(quiet=FFMPEG_QUIET)

    # overwrite original output_file if needed
    if needs_temp_file:
        if not keep_temp:
            input_file_path.unlink()

    return str(output_file_path)

def date_id_from_string(date_str):
    parsed_date = dateutil.parser.parse(date_str)
    date_id = parsed_date.strftime('%Y%m%d:%H%M%S')
    return date_id


if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument("-o", "--output", type=str, default=settings.output_folder, help=f"output folder (defaults to settings.output_folder: '{settings.output_folder}')")
  args = parser.parse_args()

  # breakpoint()

  # override output_folder
  if args.output:
    settings.output_folder = args.output

  with sync_playwright() as p:
    print("Launching " + ("Headless " if settings.headless_browser else "") + "Browser...")

    browser = p.chromium.launch(headless=settings.headless_browser)
    context = browser.new_context(
        user_agent=settings.user_agent,
        viewport=ViewportSize(width=VIEWPORT_WIDTH, height=VIEWPORT_HEIGHT)
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

    # scroll to top and hide scrollbar
    page.evaluate("""
        scrollElem = document.querySelector('#pageScroll');
        scrollElem.scroll(0,0);
        scrollElem.style.overflowY = 'hidden';
    """)
    # add date string below textArea
    capture_date_str = page.evaluate("""
        () => {
            textArea = document.querySelector('textarea');
            headerDiv = textArea.parentElement.parentElement.parentElement.parentElement;
            div = document.createElement('div');
            now = new Date();
            captureDateString = now.toUTCString();
            // div.textContent = 'MidJourney Showcase - captured by [AzLabs] ' + captureDateString;
            div.style = 'text-align:center; margin-top: 8px; font-variant: all-small-caps;';
            div.innerHTML = `<span style="font-weight:700;">MidJourney</span> Showcase - assembled by <span style="font-weight:700; color:orangered;">[AzLabs]</span> - ${captureDateString}`;
            headerDiv.appendChild(div);
            return captureDateString;
        }
    """)
    capture_date_id = date_id_from_string(capture_date_str)
    print(f"Capture date: '{capture_date_str}' ({capture_date_id})")

    # set image_clip_rect
    image_clip_rect = { "x":IMAGE_OFFSET_X, "y":IMAGE_OFFSET_Y, "width":IMAGE_WIDTH, "height":IMAGE_HEIGHT }

    # metadata
    metadata = {
        "capture_date_str": capture_date_str,
        "capture_date_id": capture_date_id,
        "viewport": {
            "width": VIEWPORT_WIDTH,
            "height": VIEWPORT_HEIGHT,
        },
        "resize": {
            "width": RESIZE_WIDTH,
            "height": RESIZE_HEIGHT,
            "scaling_algo": SCALING_ALGO,
            "keep_temp": SCALING_KEEP_TEMP,
        },
        "hide_sidebar": HIDE_SIDEBAR,
        "image_clip_rect": image_clip_rect,
        "max_links": MAX_LINKS_TO_PROCESS,
        "links_info": links_info,
    }
    metadata_file_path = output_folder / Path("metadata.json")
    print(f'Writing metadata to "{metadata_file_path.as_posix()}"...')
    with open(metadata_file_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(metadata, indent=2))

    suggested_filename = f'image_{(0):>03d}.png'
    screenshot_filename = output_folder / Path(suggested_filename)
    print(f"Saving page screenshot to '{screenshot_filename}'...")
    # breakpoint()
    # try setting env var PW_TEST_SCREENSHOT_NO_FONTS_READY=1 if it gets stuck taking screenshot
    page.screenshot(path=screenshot_filename)
    ffmpeg_resize_image(screenshot_filename, screenshot_filename, width=RESIZE_WIDTH, height=RESIZE_HEIGHT, scaling_algo=SCALING_ALGO, keep_temp=SCALING_KEEP_TEMP)

    # load createDownloadAnchorFor() function
    with open("create_download_anchor_for.js") as f:
      js_create_download = f.read()

    num_items = len(links_info)

    links_to_process = links_info[:]
    num_links_to_process = len(links_to_process)

    # process links
    print(f"Using image_clip_rect: {image_clip_rect}")
    num_links_to_process = MAX_LINKS_TO_PROCESS if MAX_LINKS_TO_PROCESS >= 0 else num_links_to_process
    print(f"Links to process: {num_links_to_process}/{num_items}")

    for idx, item in enumerate(links_to_process[:num_links_to_process]):

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

      if HIDE_SIDEBAR:
          page.evaluate('document.querySelector("nav").style.display = "none";')

      if idx == 0:
          suggested_filename = f'test_fullpage.png'
          filename = output_folder / Path(suggested_filename)
          print(f"Saving test screenshot to '{filename}'...")
          page.screenshot(path=filename)

      suggested_filename = f'image_{(idx + 1):>03d}.png'
      filename = output_folder / Path(suggested_filename)
      print(f"Saving screenshot to '{filename}'...")
      page.screenshot(clip=image_clip_rect, path=filename)
      ffmpeg_resize_image(filename, filename, width=RESIZE_WIDTH, height=RESIZE_HEIGHT, scaling_algo=SCALING_ALGO, keep_temp=SCALING_KEEP_TEMP)

    print("")
    print(f"{num_links_to_process} links processed. Exiting...")

    context.close()
    browser.close()
