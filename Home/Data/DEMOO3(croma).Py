from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from selenium.webdriver.chrome.options import Options

# Set up Chrome options
chrome_options = Options()

# Set up the WebDriver without headless mode
driver = webdriver.Chrome(options=chrome_options)

# URL to scrape
url = "https://www.croma.com/searchB?q=smartphone%3Arelevance&text=smartphone"
driver.get(url)

# Initialize lists for product details
Product_name = []
Product_Price = []
Product_Link = []
Product_Pic = []

# Maximum number of "View More" clicks
max_view_more_clicks = 1000  # Set to a high number
click_delay = 0.5  # Adjusted delay time to 500ms

try:
    view_more_clicks = 0  # Initialize a counter for page clicks (or views)

    while view_more_clicks < max_view_more_clicks:
        print(f"Scraping page {view_more_clicks + 1}...")  # Display current page being scraped

        # Wait for product elements to load (set WebDriverWait to 10 seconds)
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "product-img"))
        )

        # Find all products on the page at once
        products = driver.find_elements(By.CLASS_NAME, "cp-product")

        if len(products) == 0:
            print("No products found on this page. Stopping scraping.")
            break  # Stop if no products are found, something might be wrong

        for product in products:
            try:
                # Extract product name
                name_element = product.find_element(By.CLASS_NAME, "plp-prod-title")
                Product_name.append(name_element.text)

                # Extract product price
                try:
                    price_element = product.find_element(By.CLASS_NAME, "plp-srp-new-amount")
                    Product_Price.append(price_element.text)
                except:
                    Product_Price.append("Price not found")

                # Extract product link from the <a> tag
                try:
                    link_element = product.find_element(By.CLASS_NAME, "plp-prod-title").find_element(By.TAG_NAME, "a")
                    product_url = link_element.get_attribute('href')
                    Product_Link.append(f"{product_url}")
                except:
                    Product_Link.append("Link not found")

                # Extract product image link (check for both 'data-src' and 'src')
                img_element = product.find_element(By.CLASS_NAME, "product-img")
                try:
                    img_src = img_element.find_element(By.TAG_NAME, 'img').get_attribute('data-src')
                except:
                    img_src = img_element.find_element(By.TAG_NAME, 'img').get_attribute('src')
                
                Product_Pic.append(img_src)

            except Exception as e:
                print(f"Error extracting product details: {e}")

        # Click the "View More" button if available
        try:
            view_more_button = driver.find_element(By.CLASS_NAME, "btn-viewmore")
            view_more_button.click()
            view_more_clicks += 1
            time.sleep(click_delay)  # Adjusted sleep time
        except Exception as e:
            print(f"No more 'View More' button or error: {e}")
            break

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Check if any data was collected before saving
    if len(Product_name) > 0:
        # Create a DataFrame to organize the data
        min_length = min(len(Product_name), len(Product_Price), len(Product_Link), len(Product_Pic))
        data = pd.DataFrame({
            'Product Name': Product_name[:min_length],
            'Price': Product_Price[:min_length],
            'Product Link': Product_Link[:min_length],
            'Image Link': Product_Pic[:min_length]
        })

        # Save the data to a CSV file
        data.to_csv('croma_mobiles.csv', index=False)

        # Print some data for preview
        print(data.head())
    else:
        print("No data was scraped.")

    # Close the browser
    driver.quit()

# CONVERT CSV TO JSON
import pandas as pd
import os

try:
    # Load the CSV file
    csv_file = 'croma_mobiles.csv'  # Update this with your actual CSV file name
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"File '{csv_file}' does not exist.")
    
    # Read the CSV into a DataFrame
    df = pd.read_csv(csv_file)

    # Debug: Print the DataFrame to check its content
    print("DataFrame contents:")
    print(df.head())

    # Convert the DataFrame to JSON format with indentation
    json_file = 'croma_mobiles.json'
    df.to_json(json_file, orient='records', lines=False, indent=4)  # Indent by 4 spaces

    # Print out the JSON file content for inspection
    with open(json_file, 'r') as file:
        print("\nGenerated JSON file contents:")
        print(file.read())

    print(f"Data successfully converted to {json_file}")

except FileNotFoundError as e:
    print(e)
except Exception as e:
    print(f"An error occurred: {e}")

# DATA FIXER
import json
import re

# Load the JSON data from file
with open('croma_mobiles.json', 'r') as file:
    data = json.load(file)

# Function to fix the Product Link and Image Link
def clean_link(link):
    # Remove extra double quotes
    link = link.replace('\"', '')
    
    # Correct double URL prefix for flipkart links
    link = re.sub(r"https:\/\/www\.flipkart\.comhttps:\/\/www\.flipkart\.com", "https://www.flipkart.com", link)
    
    return link

# Iterate through each item and clean the links
for item in data:
    item['Product Link'] = clean_link(item['Product Link'])
    item['Image Link'] = clean_link(item['Image Link'])

# Save the corrected data back to the JSON file
with open('croma_mobiles_2.json', 'w') as file:
    json.dump(data, file, indent=4)

print("Data has been cleaned and saved to croma_mobiles_2.json")
