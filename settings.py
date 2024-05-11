
MIDJOURNEY_URL = "https://www.midjourney.com/showcase"

# USER_AGENT = "Mozilla/5.0 (Linux; Android 8.0.0; MI 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.101 Mobile Safari/537.36"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36"
HEADLESS_BROWSER = False
THEME = 'dark'  # 'dark'/'light'
DEFAULT_TIMEOUT = 0
OUTPUT_FOLDER = 'images/'  # or specify one with -o <output_folder>

# viewport
VIEWPORT_WIDTH = 1280
VIEWPORT_HEIGHT = 720

# resize
RESIZE_WIDTH = 1920
RESIZE_HEIGHT = 1080

# scaling
SCALING_KEEP_TEMP = True
SCALING_ALGO = "lanczos"

# image handling
HIDE_SIDEBAR = True

IMAGE_OFFSET_X = 0
IMAGE_OFFSET_Y = 76
IMAGE_WIDTH = 1146
IMAGE_HEIGHT = 644

# print warning if screenshot file size is below the threshold
WARN_SIZE_FACTOR = .25
WARN_SIZE_THRESHOLD = IMAGE_WIDTH * IMAGE_HEIGHT * 4 * WARN_SIZE_FACTOR

# other settings
MAX_LINKS_TO_PROCESS = -1  # set it to -1 to process them all

SAVE_INITIAL_FULL_PAGE = True

FFMPEG_QUIET = True

