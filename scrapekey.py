from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

options = Options()
options.binary_location = 'C:\Program Files\Mozilla Firefox\firefox.exe'
options.add_argument("--headless") # Use the --headless argument instead of the headless property

while True:
    driver = webdriver.Firefox(options=options)
    while True:
        try:
            # Navigate to the webpage
            driver.get('https://liaobots.com/en')

            # Find the SVG element using XPATH
            svg_button = WebDriverWait(driver, 6).until(EC.presence_of_element_located(
                (By.XPATH, '//*[@id="__next"]/div/div[3]/div/div/main/div/div/div[1]/div[1]/div[2]/div/code/span[1]')))
            svg_button.click()

            # Wait for the auth code element to be loaded
            # Fetch the code block by its class name
            code_element = WebDriverWait(driver, 2).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'Chat_code__y6WXR')))

            # Fetch the auth code
            auth_code = code_element.text
            print(f"The auth code is: {auth_code}")

            with open("liaobotskeys.txt", "a") as f:
                f.write(auth_code + "\n")

            break  # The page was loaded successfully and the code was retrieved, exit the inner loop.

        except TimeoutException:
            print("Page load timed out, retrying")
            continue  # The page load failed, retry loading the page in the next iteration of the inner loop.

    driver.quit()  # This driver session has finished its job, close it before starting a new one in the next iteration of the outer loop.
