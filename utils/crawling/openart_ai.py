import time
import streamlit as st

from typing import List
from contextlib import suppress
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
    driver.find_element(By.CLASS_NAME, 'MuiFormControlLabel-root').click()
    time.sleep(preiod_wait_in_sec)
    # deactivate Stable Diffusion
    driver.find_elements(By.CLASS_NAME, 'MuiFormControlLabel-root')[1].click()
    time.sleep(preiod_wait_in_sec)
    # deactivate DALL-E 2
    driver.find_elements(By.CLASS_NAME, 'MuiFormControlLabel-root')[2].click()

def extract_midjourney_images(driver: WebDriver) -> List[MidjourneyImage]:
    midjourney_images: List[MidjourneyImage] = []

    expand_prompt_text(driver)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    expand_prompt_text(driver)
    time.sleep(1)

    # bring grid elements in right order to screen scrolling
    columns = driver.find_elements(By.XPATH, "//*[contains(@style, 'flex-direction: column')]")
    grid_columns = []
    for column in columns:
        grid_columns.append(column.find_elements(By.CLASS_NAME, 'MuiCard-root'))
    gridcells = []
    for i in range(len(grid_columns[0])):
        for grid_column in grid_columns:
            with suppress(IndexError):
                gridcells.append(grid_column[i])

    for gridcell in gridcells:
        # skip i its not a midjourney image
        if len(driver.find_elements(By.XPATH, "//span[text()='Midjourney']")) == 0:
            continue

        try:
            # Scroll to the element using JavaScript
            driver.execute_script("arguments[0].scrollIntoView();", gridcell)
            # Wait until image tag is loaded
            # Define the locator for the image element
            image_locator = (By.CSS_SELECTOR, "img[src$='.webp'], img[src$='.jpg'], img[src$='.jpeg'], img[src$='.png']")
            # Wait until the image element is visible
            wait = WebDriverWait(gridcell, 4)
            image_element = wait.until(EC.visibility_of_element_located(image_locator))
            # Extract image webp element
            image_url = image_element.get_attribute('src')
            assert any(image_url.endswith(ending) for ending in [".webp", ".jpg", "jpeg", ".png"]) , f"image_url {image_url}, is not in the expected image format"
            # extract prompt from text area
            prompt = gridcell.find_element(By.CLASS_NAME, "MuiTypography-body2").text
            if not check_if_image_exists(midjourney_images, image_url):
                midjourney_images.append(MidjourneyImage(image_url=image_url, prompt=prompt))
        except Exception as e:
            print("Could not extract image and prompt", str(e))
            continue

    return midjourney_images


def expand_prompt_text(driver):
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


def crawl_openartai():
    session_state: SessionState = st.session_state["session_state"]
    driver = session_state.browser.driver
    time.sleep(1)
    get_openartai_discovery(driver)
    time.sleep(2)
    openartai_search_prompts(session_state.crawling_request.search_term, driver)
    time.sleep(1)
    apply_filters(driver)
    time.sleep(2)
    session_state.crawling_data = CrawlingData(midjourney_images=extract_midjourney_images(driver))

