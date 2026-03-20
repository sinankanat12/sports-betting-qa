import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from config.settings import BASE_URL, USER_ID, HEADLESS, IMPLICIT_WAIT
from api.betting_client import BettingClient


@pytest.fixture(scope="session")
def api_client():
    return BettingClient()


@pytest.fixture(scope="session")
def browser():
    chrome_options = Options()
    if HEADLESS:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1440,900")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(IMPLICIT_WAIT)

    yield driver

    driver.quit()


@pytest.fixture(autouse=True)
def reset_balance(api_client):
    """Reset balance before each test to ensure clean state."""
    api_client.reset_balance()


@pytest.fixture
def authenticated_page(browser):
    """Navigate to app with user-id query parameter."""
    browser.get(f"{BASE_URL}?user-id={USER_ID}")
    return browser
