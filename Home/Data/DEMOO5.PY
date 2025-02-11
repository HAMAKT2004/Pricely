from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import json

def scrape_reliance_digital_mobile_data_selenium(url, driver):
    driver.get(url)
    time.sleep(15)  # Wait for the page to load

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    product_data = []
    products = soup.find_all('div', class_='sp__product')

    for product in products:
        # Extract product name
        product_name = product.find('p', class_='sp__name')
        if product_name:
            product_name = product_name.text.strip()
        else:
            product_name = None

        # Extract price
        price_wrapper = product.find('div', class_='StyledPriceBoxM__PriceWrapper-sc-1l9ms6f-0')
        if price_wrapper:
            price = price_wrapper.find('span', class_='TextWeb__Text-sc-1cyx778-0 gimCrs')
            if price:
                price = price.text.strip()  # Get the formatted price
            else:
                price = None
        else:
            price = None

        # Extract product image
        image = product.find('img')  # Get the first image tag inside the product div
        if image and 'src' in image.attrs:
            image_url = "https://www.reliancedigital.in" + image['src']  # Prepend the base URL
        else:
            image_url = None

        # Extract product link
        product_link_tag = product.find('a', attrs={"attr-tag": "anchor"})
        if product_link_tag and 'href' in product_link_tag.attrs:
            product_link = "https://www.reliancedigital.in" + product_link_tag['href']  # Prepend the base URL
        else:
            product_link = None

        # Append data if any value is found
        if any([product_name, price, image_url, product_link]):
            product_data.append({
                'Product Name': product_name,
                'Price': price,
                'Image URL': image_url,
                'Product Link': product_link  # Add the product link
            })

    return product_data

def scrape_all_reliance_digital_pages_selenium(base_url, max_pages=50):
    # Set up the WebDriver using Selenium
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    data = []
    try:
        for page_number in range(max_pages):
            url = f"{base_url}&page={page_number + 1}"  # Ensure the page number is added correctly
            print(f"Scraping page {page_number + 1}: {url}")
            product_data = scrape_reliance_digital_mobile_data_selenium(url, driver)
            if not product_data:
                print("No more data to scrape.")
                break
            data.extend(product_data)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()  # Close the browser after scraping is done
        # Save data to JSON if any was collected
        if data:
            with open('reliance_digital_phones_data_selenium.json', 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, indent=4, ensure_ascii=False)
            print("Data successfully exported to reliance_digital_phones_data_selenium.json")
        else:
            print("No data scraped. Check the provided URL or scraping logic.")

# Correct base URL for Reliance Digital smartphones
base_url = 'https://www.reliancedigital.in/smartphones/c/S101711?searchQuery=:relevance'
scrape_all_reliance_digital_pages_selenium(base_url)
