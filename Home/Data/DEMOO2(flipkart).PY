from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import json
import re
import os

# Set up the WebDriver
driver = webdriver.Chrome()  # Ensure chromedriver is in your PATH

# URL to scrape
url = "https://www.flipkart.com/search?q=mobile&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off"
driver.get(url)

# Initialize lists for product details
Product_name = []
Product_Price = []
Product_Link = []
Product_Pic = []
product_counter = 0  # Initialize product counter

page_number = 1  # Initialize the page counter

try:
    while True:
        print(f"Scraping page {page_number}...")  # Display current page being scraped

        # Wait for product elements to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "tUxRFH"))
        )

        # Find product elements
        products = driver.find_elements(By.CLASS_NAME, "tUxRFH")

        if not products:
            print("No products found on this page.")
            break

        for product in products:
            try:
                # Extract product name
                name_element = product.find_element(By.CLASS_NAME, "KzDlHZ")
                Product_name.append(name_element.text)

                # Extract product price
                try:
                    price_element = product.find_element(By.CLASS_NAME, "Nx9bqj")  # Updated class name for price
                    Product_Price.append(price_element.text)
                except:
                    Product_Price.append("Price not found")

                # Extract product link
                link_element = product.find_element(By.CLASS_NAME, "CGtC98")
                Product_Link.append(f'"https://www.flipkart.com{link_element.get_attribute("href")}"')  # Wrapped in double quotes

                # Extract product image link
                img_element = product.find_element(By.CSS_SELECTOR, "img.DByuf4")
                Product_Pic.append(f'"{img_element.get_attribute("src")}"')  # Wrapped in double quotes

                product_counter += 1  # Increment the product counter

            except Exception as e:
                print("Error extracting product details:", e)

        # Print live count of products scraped
        print(f"Total products scraped so far: {product_counter}")

        # Find and click the "Next" button
        try:
            next_button = driver.find_element(By.XPATH, '//a[contains(@class, "_9QVEpD") and span[text()="Next"]]')
            if next_button.is_displayed() and next_button.is_enabled():
                next_button.click()  # Click the next page button
                time.sleep(3)  # Increased wait time for the next page to load
                page_number += 1  # Increment the page counter after each click
            else:
                print("Next button not clickable, ending scrape.")
                break
        except Exception as e:
            print("No more pages to scrape:", e)
            break

except Exception as e:
    print("An error occurred:", e)
finally:
    # Create a DataFrame to organize the data, ensuring all lists are of the same length
    min_length = min(len(Product_name), len(Product_Price), len(Product_Link), len(Product_Pic))
    data = pd.DataFrame({
        'Product Name': Product_name[:min_length],
        'Price': Product_Price[:min_length],
        'Product Link': Product_Link[:min_length],
        'Image Link': Product_Pic[:min_length]
    })

    # Save the data to a CSV file
    data.to_csv('flipkart_mobiles.csv', index=False)

    # Print some data for preview
    print(data.head())
    print(f"Total products scraped: {product_counter}")  # Print total products scraped at the end

    # Close the browser
    driver.quit()

# CONVERT CSV TO JSON
try:
    # Load the CSV file
    csv_file = 'flipkart_mobiles.csv'  # Update this with your actual CSV file name
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"File '{csv_file}' does not exist.")
    
    # Read the CSV into a DataFrame
    df = pd.read_csv(csv_file)

    # Debug: Print the DataFrame to check its content
    print("DataFrame contents:")
    print(df.head())

    # Convert the DataFrame to JSON format with indentation
    json_file = 'flipkart_mobiles.json'
    df.to_json(json_file, orient='records', lines=False, indent=4)  # Indent by 4 spaces

    print(f"Data successfully converted to {json_file}")

except FileNotFoundError as e:
    print(e)
except Exception as e:
    print(f"An error occurred: {e}")

# DATA FIXER
# Load the JSON data from file
with open('flipkart_mobiles.json', 'r') as file:
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
with open('flipkart_mobiles_2.json', 'w') as file:
    json.dump(data, file, indent=4)

print("Data has been cleaned and saved to flipkart_mobiles_2.json")
