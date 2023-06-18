import time
import streamlit as st

from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from utils.session import set_session_state_if_not_exists
from utils.data_classes import SessionState, CrawlingData, MidjourneyImage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



def get_openartai_discovery(driver: WebDriver):
    driver.get("https://openart.ai/discovery")

def openartai_search_prompts(search_term: str, driver: WebDriver):
    search_input = driver.find_element(By.CSS_SELECTOR, 'input[id=":Rpklammdalm:"]')
    # Click on input field
    search_input.click()
    # Put text in input
    search_input.send_keys(search_term)
    # Simulate pressing the Enter key
    search_input.send_keys(Keys.ENTER)

def check_if_image_exists(images: List[MidjourneyImage], image_url: str) -> bool:
    for img in images:
        if img.image_url == image_url:
            return True
    return False

def apply_filters(driver: WebDriver, preiod_wait_in_sec=1):
    # Open model selection filter field
    driver.find_element(By.CLASS_NAME, 'css-dpjbap').click()
    time.sleep(preiod_wait_in_sec)
    # deactivate Stable Diffusion
    driver.find_elements(By.CLASS_NAME, 'css-dpjbap')[1].click()
    time.sleep(preiod_wait_in_sec)
    # deactivate DALL-E 2
    driver.find_elements(By.CLASS_NAME, 'css-dpjbap')[2].click()
    time.sleep(preiod_wait_in_sec)

def extract_midjourney_images(driver: WebDriver) -> List[MidjourneyImage]:
    midjourney_images: List[MidjourneyImage] = []
    gridcells = driver.find_elements(By.CLASS_NAME, 'css-sul2l0')

    # Click on all more to make prompt completly visible
    more_elements = driver.find_elements(By.XPATH, "//span[text()='[more]']")
    for i, more_element in enumerate(more_elements):
        try:
            # Scroll to the element using JavaScript
            driver.execute_script("arguments[0].scrollIntoView();", more_element)
            more_element.click()
        except:
            print(f"more element number {i} is not clickable")
            continue

    for gridcell in gridcells:
        # skip i its not a midjourney image
        if len(driver.find_elements(By.XPATH, "//span[text()='Midjourney']")) == 0:
            continue

        try:
            # TODO: extracted Image url ist not always the correct one
            gridcell_image = gridcell.find_element(By.CLASS_NAME, "css-1fw0bmn")
            # Scroll to the element using JavaScript
            driver.execute_script("arguments[0].scrollIntoView();", gridcell_image)
            time.sleep(0.5)
            image_url = gridcell_image.find_elements(By.TAG_NAME, 'img')[-1].get_attribute('src')
            assert any(image_url.endswith(ending) for ending in [".webp", ".jpg", "jpeg", ".png"]) , f"image_url {image_url}, is not in the expected image format"
            # extract prompt from text area
            prompt = gridcell.find_element(By.CLASS_NAME, "css-18l0n8d").text
            if not check_if_image_exists(midjourney_images, image_url):
                midjourney_images.append(MidjourneyImage(image_url=image_url, prompt=prompt))
        except Exception as e:
            print("Could not extract image and prompt", str(e))
            continue

    return midjourney_images


def crawl_openartai():
    session_state: SessionState = st.session_state["session_state"]
    driver = session_state.browser.driver
    time.sleep(1)
    get_openartai_discovery(driver)
    time.sleep(2)
    openartai_search_prompts(session_state.crawling_request.search_term, driver)
    time.sleep(1)
    apply_filters(driver)
    session_state.crawling_data = CrawlingData(midjourney_images=extract_midjourney_images(driver))

