import config

import random
import time

from selenium import webdriver


def convert_list_to_dict(l):
    """Return dict from list """
    return {l[i]: l[i + 1] for i in range(0, len(l), 2)}

def init_webdriver():
    """Init webdriver if not already initiated or return working instance"""

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    options.add_argument('--window-size=1400,1050')
    # unwanted tooling from https://github.com/GoogleChrome/chrome-launcher/blob/main/docs/chrome-flags-for-tools.md
    options.add_argument('--disable-client-side-phishing-detection')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-component-extensions-with-background-pages')
    options.add_argument('--disable-default-apps')
    options.add_argument('--disable-features=InterestFeedContentSuggestions')
    options.add_argument('--disable-features=Translate')
    options.add_argument('--mute-audio')
    options.add_argument('--no-default-browser-check')
    options.add_argument('--no-first-run')
    options.add_argument('--ash-no-nudges')
    options.add_argument('--disable-search-engine-choice-screen')
    options.add_argument('--disable-gpu')
    options.add_argument('--remote-debugging-port=9222')

    # bypass headless check
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    options.add_argument(f'user-agent={user_agent}')

    service = webdriver.ChromeService(executable_path=config.SELENIUM_CHROMEDRIVER)
    driver = webdriver.Chrome(service=service, options=options)
    # driver.implicitly_wait(5)
    return driver


def destroy_webdriver(driver):
    """Cleanup webdriver"""
    driver.quit()


def simulate_human_delay(min_secs=1, max_secs=5):
    """Wait for random few seconds to simulate human delay between clicks in seconds

       This is needed to protect our IP for automat that will discover we are bot
    """
    time.sleep(random.randint(min_secs, max_secs))
