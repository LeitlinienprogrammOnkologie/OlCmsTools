import os
import time
import requests
import qrcode
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By

# Define the Chrome webdriver options
options = webdriver.ChromeOptions()
options.add_argument("--headless") # Set the Chrome webdriver to run in headless mode for scalability

# By default, Selenium waits for all resources to download before taking actions.
# However, we don't need it as the page is populated with dynamically generated JavaScript code.
options.page_load_strategy = "none"

# Pass the defined options objects to initialize the web driver
driver = Chrome(options=options)
# Set an implicit wait of 5 seconds to allow time for elements to appear before throwing an exception
driver.implicitly_wait(5)

url = "https://www.leitlinienprogramm-onkologie.de/leitlinien/uebersicht"

driver.get(url)

html = driver.page_source
elems = driver.find_elements(By.TAG_NAME, "a")

s3ll = {}

for elem in elems:
    href = elem.get_attribute('href')
    if href is not None:
        text = elem.get_attribute('innerHTML').replace("/","").strip()
        if '/leitlinien/' in href and 'patientenleitlinien' not in href and 'uebersicht' not in href and href not in s3ll:
            qrcode_name = "QR_%s.png" % text
            qrcode_path = "./qrcodes/s3ll/%s" % qrcode_name
            img = qrcode.make(href)
            img.save(qrcode_path, "PNG")

url = "https://www.leitlinienprogramm-onkologie.de/patientenleitlinien/uebersicht"

driver.get(url)

html = driver.page_source
images = driver.find_elements(By.TAG_NAME, "img")

for image in images:
    elem = image.find_element(By.XPATH, "..").find_element(By.XPATH, "..")
    href = elem.find_element(By.TAG_NAME, "a").get_attribute('href')
    text = elem.find_element(By.TAG_NAME, "a").get_attribute('innerText')
    href_arr = href.split("/")

    if len(text) > 0 and href_arr[3] == "patientenleitlinien":
        img_elem = elem.find_element(By.TAG_NAME, "img")
        if img_elem is not None:
            img_url = img_elem.get_attribute("src")
            image = requests.get(img_url).content
            extension = os.path.splitext(img_url)[1]
            img_path = "./qrcodes/pll/%s%s" % (text, extension)
            with open(img_path, "wb") as img_file:
                img_file.write(image)
            qrcode_name = "%s.png" % text
            qrcode_path = "./qrcodes/pll/QR_%s" % qrcode_name
            img = qrcode.make(href)
            img.save(qrcode_path, "PNG")