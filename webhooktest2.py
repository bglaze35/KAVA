import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

URL = "https://investorlift.com"  # Replace this with the actual URL of the website to scrape
DIV_CLASS_TO_CAPTURE = "property-list-item"
XPATH_FOR_LATEST_OPTION = '//*[@id="__layout"]/div/div/div[2]/div/div[1]/div[2]/div/div[1]'
WEBHOOK_URL = "https://flow.zoho.com/793997673/flow/webhook/incoming?zapikey=1001.8044517bbd386ea6910461fda61f22b1.38f9a24e2d2675afbd0852618ffb05b9&isdebug=false"

def select_latest_option(driver):
    try:
        driver.get(URL)
        time.sleep(5)  # Wait for the page to load and JavaScript to execute

        # Find and click the element corresponding to the "Latest" option using the provided XPath
        latest_option = driver.find_element_by_xpath(XPATH_FOR_LATEST_OPTION)
        latest_option.click()

        time.sleep(5)  # Wait for the page to reload with the sorted data

    except Exception as e:
        print("Error occurred while selecting the Latest option:", e)

def scrape_website(driver):
    try:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        property_items = soup.find_all("div", class_=DIV_CLASS_TO_CAPTURE)

        for item in property_items:
            # Data extraction code
            property_url = item.find("a")["href"]
            image_source = item.find("img")["src"]
            price_element = item.find("span", class_="listing-price")
            price = price_element.text.strip() if price_element else "N/A"

            area_element = item.select_one("ul.listing-hidden-content li:contains('Area') span")
            area = area_element.text.strip() if area_element else "N/A"

            beds_element = item.select_one("ul.listing-hidden-content li:contains('Beds') span")
            beds = beds_element.text.strip() if beds_element else "N/A"

            baths_element = item.select_one("ul.listing-hidden-content li:contains('Baths') span")
            baths = baths_element.text.strip() if baths_element else "N/A"

            arv_element = item.select_one("ul.listing-hidden-content li:contains('ARV') span")
            arv = arv_element.text.strip() if arv_element else "N/A"

            county_element = item.select_one("div.listing-compact-title").contents[0].strip()
            county = county_element if county_element else "N/A"

            second_line_address_element = item.select_one("div.listing-compact-title > div.second-line-address")
            second_line_address = second_line_address_element.text.strip() if second_line_address_element else "N/A"

            # Prepare the data payload to be sent to the webhook
            data_payload = {
                "property_url": property_url,
                "image_source": image_source,
                "price": price,
                "area": area,
                "beds": beds,
                "baths": baths,
                "arv": arv,
                "county": county,
                "second_line_address": second_line_address
            }

            # Send the data payload to the webhook URL
            response = requests.post(WEBHOOK_URL, json=data_payload)

            # Check the response status to ensure the data was sent successfully
            if response.status_code == 200:
                print("Data sent successfully to the webhook!")
            else:
                print("Failed to send data to the webhook.")

    except Exception as e:
        print("Error occurred while scraping website:", e)

if __name__ == "__main__":
    # Add the path to the ChromeDriver binary here
    chrome_driver_path = "/home/bitnami/chromedriver"  # Replace this with the actual path on your AWS instance

    # Configure Chrome options for headless mode
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Initialize the ChromeDriver service with the specified path
    service = Service(executable_path=chrome_driver_path)

    # Initialize ChromeDriver with the service and options
    driver = webdriver.Chrome(service=service, options=options)

    try:
        while True:
            select_latest_option(driver)  # Ensure "Latest" option is selected before scraping
            scrape_website(driver)
            time.sleep(120)  # Wait for 120 seconds (2 minutes) before the next execution

    except KeyboardInterrupt:
        driver.quit()  # Close the browser when the script is interrupted
