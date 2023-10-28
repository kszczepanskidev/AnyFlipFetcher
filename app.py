from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from requests import get, packages
from PIL import Image

import sys
from argparse import ArgumentParser
from os import path, environ, makedirs, remove
from time import sleep
from re import search
from traceback import print_exc
from glob import glob

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = path.dirname(__file__)
    return path.join(base_path, relative_path)

# Read .env variables
load_dotenv()
firefoxPath = environ.get('FIREFOX_PATH', '')

# Read Launch Params
parser = ArgumentParser()
parser.add_argument('--url', help='AnyFlip URL for the document.')
args = parser.parse_args()

anyflip_url = args.url
if not (anyflip_url.startswith('http://') or anyflip_url.startswith('https://')):
    anyflip_url = 'https://' + anyflip_url

try:
    # Setup web environment
    packages.urllib3.disable_warnings()
    binary = FirefoxBinary(firefoxPath)
    driver = webdriver.Firefox(firefox_binary=binary, executable_path=resource_path('.\driver\geckodriver.exe'))

    # Setup image directory
    makedirs('pages/', exist_ok=True)

    # Get document page, page count and document title
    driver.get(anyflip_url)
    page_regex_result = search(r'pages: "(\d+)",',  driver.page_source).groups(1)
    last_page = int(page_regex_result[0] if type(page_regex_result) is tuple else page_regex_result)
    document_title = driver.find_element_by_css_selector('.show-info-middle-title').text

    # Setup focus on document frame
    driver.switch_to.frame('show-iFrame-book')
    sleep(5)

    # Start fetching document pages
    def save_image(page, url):
        with open(f'pages/page{page}.jpg', 'wb') as file:
            file.write(get(url, verify=False).content)

    page = 1
    page_range = range(2, last_page)
    while page<=last_page:
        # Wait for and download left page image
        left_page = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, f'#page{page} img'))).get_attribute("src")
        save_image(page, left_page)

        if page in page_range:
            # Download right page image
            right_page = driver.find_element_by_css_selector(f'#page{page+1} img').get_attribute("src")
            save_image(page+1, right_page)

        # Proceed to next page
        driver.find_element_by_xpath("//span[contains(text(), 'Next Page')]/ancestor::div[@class='button']").click()
        page += (2 if page in page_range else 1)
        sleep(1)

    # Convert all images to PDF file
    page_images = [Image.open(f"pages/page{p}.jpg") for p in range(1, last_page+1)]
    page_images[0].save(f'{document_title}.pdf', "PDF", resolution=100.0, save_all=True, append_images=page_images[1:])

    # Cleanup images
    for image in glob('pages/*.jpg'):
        remove(image)

except:
    # Print exception info
    print_exc()

# Close browser env
driver.quit()
