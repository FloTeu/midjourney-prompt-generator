import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver

class SeleniumBrowser():
    def __init__(self) -> None:
        self.driver = None
        self.is_ready = False
        self.data_dir_path = None
        self.headless = None

    def setup(self, headless=False, data_dir_path=None):
        self.driver = init_selenium_driver(headless=headless, data_dir_path=data_dir_path)
        self.headless = headless
        self.data_dir_path = data_dir_path
        self.is_ready = True

    def close_driver(self):
        self.driver.close()
        self.is_ready = False

    def quit_driver(self):
        self.driver.quit()
        self.is_ready = False

    def reset_driver(self):
        """ If possible quits the existing selenium driver and starts a new one"""
        try:
            delete_files_in_path(self.data_dir_path)
            self.quit_driver()
        except:
            pass
        self.driver = init_selenium_driver(headless=self.headless, data_dir_path=self.data_dir_path)
        self.is_ready = True

def init_selenium_driver(headless=True, data_dir_path=None) -> WebDriver:
    """Instantiate a WebDriver object (in this case, using Chrome)"""
    options = Options() #either firefox or chrome options
    options.add_argument('--disable-gpu')
    # sandbox may cause error on environments like Docker containers
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-extensions")
    #options.add_argument('--blink-settings=imagesEnabled=false')
    options.add_argument('--disk-cache-size=10000000')  # Set cache size to 10 MB
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-features=NetworkService")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--lang=en");
    if data_dir_path:
        options.add_argument(f'--user-data-dir={data_dir_path}')
    if headless:
        options.add_argument('--headless')
    return webdriver.Chrome(options=options)


def delete_files_in_path(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            os.remove(file_path)



