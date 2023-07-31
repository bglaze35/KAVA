import time
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re

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

        # Scroll down using the down arrow key to load more data
        body_element = driver.find_element_by_tag_name("body")
        scroll_iterations = 200  # Adjust this number as needed
        for _ in range(scroll_iterations):
            body_element.send_keys(Keys.ARROW_DOWN)

        time.sleep(5)  # Wait for the page to reload with the sorted data

    except Exception as e:
        print("Error occurred while selecting the Latest option:", e)

def scrape_website(driver, previous_property_urls):
    try:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        property_items = soup.find_all("div", class_=DIV_CLASS_TO_CAPTURE)
        new_properties_found = 0

        for item in property_items:
            property_url = "https://investorlift.com" + item.find("a")["href"]

            # Check if the property URL is in the list of previously scraped property URLs
            if property_url not in previous_property_urls:
                new_properties_found += 1
                # Data extraction code
                image_source = item.find("img")["src"]
                price_element = item.find("span", class_="listing-price")
                price = price_element.text.strip() if price_element else "N/A"

                # Extract only the numeric part from the "Price" value using regular expressions
                price_numeric = int(re.sub(r'\D', '', price)) if re.sub(r'\D', '', price) else "N/A"

                area_element = item.select_one("ul.listing-hidden-content li:-soup-contains('Area') span")
                area = area_element.text.strip() if area_element else "N/A"

                # Check if the "area" value contains non-numeric characters
                area_numeric = int(re.sub(r'\D', '', area)) if re.sub(r'\D', '', area) else "N/A"

                beds_element = item.select_one("ul.listing-hidden-content li:-soup-contains('Beds') span")
                beds = beds_element.text.strip() if beds_element else "N/A"

                baths_element = item.select_one("ul.listing-hidden-content li:-soup-contains('Baths') span")
                baths = baths_element.text.strip() if baths_element else "N/A"

                arv_element = item.select_one("ul.listing-hidden-content li:-soup-contains('ARV') span")
                arv = arv_element.text.strip() if arv_element else "N/A"

                # Extract only the numeric part from the ARV value using regular expressions
                arv_numeric = int(re.sub(r'\D', '', arv)) if re.sub(r'\D', '', arv) else 0

                county_element = item.select_one("div.listing-compact-title").contents[0].strip()
                county = county_element if county_element else "N/A"

                second_line_address_element = item.select_one("div.listing-compact-title > div.second-line-address")
                second_line_address = second_line_address_element.text.strip() if second_line_address_element else "N/A"

                # Split the second line address into City, State, and Zip Code
                address_parts = second_line_address.split(",")  # Split by comma
                city = address_parts[0].strip()
                state = address_parts[1].strip() if len(address_parts) > 1 else "N/A"  # Remove leading/trailing spaces
                zip_code = address_parts[2].strip() if len(address_parts) > 2 else "N/A"  # Remove leading/trailing spaces

                # Print the details for each new property (optional)
                print("Property URL:", property_url)
                print("Image Source:", image_source)
                print("Price (Numeric):", price_numeric)
                print("Area (Numeric):", area_numeric)
                print("Beds:", beds)
                print("Baths:", baths)
                print("ARV (Numeric):", arv_numeric)
                print("County:", county)
                print("City:", city)
                print("State:", state)
                print("Zip Code:", zip_code)
                print("------------------------")

                # Prepare the data payload to be sent to the webhook
                data_payload = {
                    "property_url": property_url,
                    "image_source": image_source,
                    "price": price_numeric,  # Use the numeric value for "price"
                    "area": area_numeric,   # Use the numeric value for "area"
                    "beds": beds,
                    "baths": baths,
                    "arv": arv_numeric,     # Use the numeric value for "arv"
                    "county": county,
                    "city": city,
                    "state": state,
                    "zip_code": zip_code
                }

                # Send the data payload to the webhook URL
                response = requests.post(WEBHOOK_URL, json=data_payload)

                # Check the response status to ensure the data was sent successfully
                if response.status_code == 200:
                    print("Data sent successfully to the webhook!")
                else:
                    print("Failed to send data to the webhook.")

                # Add the property URL to the list of previously scraped property URLs
                previous_property_urls.append(property_url)

        if new_properties_found == 0:
            print("No new properties found in this iteration.")
        else:
            print(f"Detected {new_properties_found} new properties in this iteration.")

    except Exception as e:
        print("Error occurred while scraping website:", e)

if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run Chrome in headless mode (no GUI)
    driver = webdriver.Chrome(executable_path=r"C:\Users\brand\Desktop\scraper\chromedriver.exe", options=options)  # Initialize ChromeDriver with options
    previous_property_urls = []  # Initialize the list to store previously scraped property URLs
    try:
        while True:
            select_latest_option(driver)  # Ensure "Latest" option is selected before scraping
            scrape_website(driver, previous_property_urls)
            time.sleep(900)  # Wait for 900 seconds (15 minutes) before the next execution

    except KeyboardInterrupt:
        driver.quit()  # Close the browser when the script is interrupted
