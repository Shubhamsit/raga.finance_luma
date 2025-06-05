
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from dotenv import load_dotenv
load_dotenv()

EMAIL ="737rohit.a@gmail.com"
# EMAIL = os.environ.get("EMAIL")
PASSWORD ="RohitNexus1234"
# PASSWORD = os.environ.get("PASSWORD")
print(EMAIL)
print(PASSWORD)

def login_to_luma():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    # chrome_options.add_argument("C:\\Users\\Shubham Kumar\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 2")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(options=chrome_options)

    try:
        print(f"\n Using email: {EMAIL}\n")
        driver.get("https://lu.ma/signin")
        print(" Opened Luma signin page")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("Loaded Luma signin page")

        # Email input
      
        email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="email"]'))
)
        email_input.clear()
        email_input.send_keys(EMAIL)


        # Click Continue
        continue_btn = driver.find_element(By.XPATH, "//button[contains(., 'Continue')]")
        continue_btn.click()
        print("Clicked continue")

      
       
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_input.clear()
        password_input.send_keys(PASSWORD)
        print("Entered password")

        # Click login

        login_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
)

        login_btn.click()
        print("Submitted login")

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        print("Logged in successfully")
        
  

    except Exception as e:
        print(f"\n Login failed: {e}")
    finally:
        return driver
       

        




