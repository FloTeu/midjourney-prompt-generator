import time
import streamlit as st

from typing import List
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains

from mid_prompt_gen.session import set_session_state_if_not_exists
from mid_prompt_gen.data_classes import SessionState, CrawlingData, MidjourneyImage
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def login_to_midjourney():
    set_session_state_if_not_exists()
    session_state: SessionState = st.session_state["session_state"]
    driver = session_state.browser.driver
    # Click on home page
    driver.get("https://www.midjourney.com")

    # Sign in
    time.sleep(5)
    click_sign_in(driver)

    # Login in with discord credentials
    wait = WebDriverWait(driver, 10)  # Adjust the timeout as needed
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button[type='submit']")))
    discord_login(driver)

    # Wait until the domain changes
    new_domain = "midjourney.com"
    wait = WebDriverWait(driver, 5)
    wait.until(EC.url_contains(new_domain))

    session_state.status.midjourney_login = True


def click_sign_in(driver: WebDriver):
    sign_in_text = "Sign In"
    button = driver.find_element(By.XPATH, f"//*[contains(text(), '{sign_in_text}')]")
    button.click()

def discord_login(driver: WebDriver):
    """Fill discord login form and simulate submit button click"""
    # Fill in the form fields
    username_input = driver.find_element(By.NAME, "email")
    password_input = driver.find_element(By.NAME, "password")
    username_input.send_keys(st.session_state["mid_email"])
    password_input.send_keys(st.session_state["mid_password"])

    # Submit the form
    submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit_button.click()

    time.sleep(3)
    # TODO: csptca can arrise
    # if not redirect to midjourney happend, we probably need to authorized midjourney to acces the discord account first
    if "discord.com" in driver.current_url:
        authorize_midjourney(driver)


def authorize_midjourney(driver: WebDriver):
    # TODO how to handle other countries?
    auth_button = driver.find_elements(By.XPATH, f"//button")[1]
    auth_button.click()


def midjourney_community_feed(driver: WebDriver):
    driver.get("https://www.midjourney.com/app/feed/")

def midjourney_search_prompts(search_term: str, driver: WebDriver):
    search_input = driver.find_element(By.CSS_SELECTOR, 'input[name="search"]')
    search_input.send_keys(search_term)

    time.sleep(1)
    # Find the parent element of the search input
    parent_element = search_input.find_element(By.XPATH, './..')
    search_button = parent_element.find_element(By.XPATH, './following-sibling::button')
    search_button.click()

def extract_midjourney_images(driver: WebDriver) -> List[MidjourneyImage]:
    midjourney_images: List[MidjourneyImage] = []
    gridcells = driver.find_elements(By.CSS_SELECTOR, 'div[role="gridcell"]')
    gridcells.reverse() # last html element is displayed on top of page
    # Create an instance of ActionChains
    actions = ActionChains(driver)

    # Iterate through the gridcells
    for gridcell in gridcells:
        try:
            ## Extract image url
            # Extract the image URL from the href attribute
            image_url = gridcell.find_element(By.TAG_NAME, 'link').get_attribute('href')
            assert ".webp" in image_url, f"image_url {image_url}, is not in the expected webp format"
            # Transform string to get upscaled image
            image_url_splitted = image_url.split("_N.webp")[0].split("_")
            image_url_splitted[-1] = "640" # midjourney stores upscaled images with 640 and not 32
            image_url = "_".join(image_url_splitted) + "_N.webp"

            ## Extract prompt
            # Hover over the gridcell
            actions.move_to_element(gridcell).perform()
            # extract prompt from text area
            prompt = driver.find_element(By.CSS_SELECTOR, "p._promptText_").text
            midjourney_images.append(MidjourneyImage(image_url=image_url, prompt=prompt))
        except Exception as e:
            print(str(e))

    return midjourney_images


def crawl_midjourney():
    session_state: SessionState = st.session_state["session_state"]
    driver = session_state.browser.driver
    time.sleep(1)
    midjourney_community_feed(driver)
    time.sleep(1)
    midjourney_search_prompts(session_state.crawling_request.search_term, driver)
    time.sleep(3)
    session_state.crawling_data = CrawlingData(midjourney_images=extract_midjourney_images(driver))

