import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def fetch_valid_image_src(banner):
    """Try to fetch the correct image source from various attributes."""
    try:
        img = banner.find_element(By.TAG_NAME, 'img')
        
        # Attempt to get the src attribute
        img_src = img.get_attribute('src')
        
        # Check for alternative data attributes if img_src is a placeholder
        if img_src.endswith('mdefault.png'):
            # Check for any data attributes that may contain a valid image source
            data_src = img.get_attribute('data-src')
            if data_src:
                img_src = data_src
            
            # If still a placeholder, look for any other images in the parent or sibling elements
            parent_images = banner.find_elements(By.CSS_SELECTOR, 'div img')
            if parent_images:
                img_src = parent_images[0].get_attribute('src')  # Get the first valid image
        
        return img_src

    except Exception as e:
        print(f"Error fetching image source: {e}")
        return None

def scrape_offer_banners(driver, url):
    driver.get(url)

    try:
        # Wait for the specific offer banners section to load
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "slick-slide"))
        )
        
        offers_data = []
        unique_links = set()  # To track unique product links

        while True:
            offer_banners = driver.find_elements(By.CSS_SELECTOR, '.slick-slide')
            for banner in offer_banners:
                img_src = fetch_valid_image_src(banner)
                img_alt = banner.find_element(By.TAG_NAME, 'img').get_attribute('alt')
                img_title = banner.find_element(By.TAG_NAME, 'img').get_attribute('title')

                # Extract the product link from the banner (if available)
                product_link = banner.find_element(By.TAG_NAME, 'a').get_attribute('href')

                # Only add the offer if the image source is valid and product link is unique
                if img_src and img_src != 'https://www.reliancedigital.in/build/client/images/loaders/mdefault.png':
                    if product_link not in unique_links:
                        unique_links.add(product_link)  # Add the product link to the set
                        offers_data.append({
                            "Image Source": img_src,
                            "Alt Text": img_alt,
                            "Title": img_title,
                            "Product Link": product_link
                        })

            # Check if there is a next button and if it can be clicked
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, '.slick-next')
                if next_button.is_enabled():
                    next_button.click()
                    time.sleep(10)  # Wait for the next slide to load
                else:
                    break  # Exit the loop if there are no more slides
            except Exception:
                break  # Exit if no next button is found

        return offers_data

    except Exception as e:
        print(f"Error finding offer banners: {e}")
        return []

# Usage
url = "https://www.reliancedigital.in/smartphones/c/S101711?searchQuery=:relevance&page=0"
driver = webdriver.Chrome()  # or any other driver you are using
offers = scrape_offer_banners(driver, url)

# Save to JSON file
with open('offer.json', 'w') as json_file:
    json.dump(offers, json_file, indent=4)

print("Offers data saved to offers.json")
driver.quit()
