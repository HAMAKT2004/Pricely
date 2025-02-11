import time
import json
import logging
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Set up logging
logging.basicConfig(filename='scraper_errors.log', level=logging.ERROR)

# User-Agent list to rotate
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
]

# Function to get a random User-Agent
def get_random_user_agent():
    return random.choice(USER_AGENTS)

# Function to check if a product is a phone based on brand or model name
def is_phone(product_name):
    include_keywords = [
        "phone", "smartphone", "mobile", "android", "iphone", 
        "samsung", "apple", "oneplus", "xiaomi", "redmi", "oppo", "vivo", 
        "realme", "nokia", "motorola", "asus", "sony", "huawei", "google", 
        "pixel", "lenovo", "zte", "meizu", "micromax", "infinix", "tecno", 
        "itel", "lava", "gionee", "coolpad", "blackberry", "panasonic", 
        "sharp", "leeco", "alcatel", "blu", "honor", "iqoo", "doogee", 
        "umidigi", "poco", "tcl", "blackshark", "fairphone", "shiftphone", 
        "essential", "xolo", "karbonn", "lyf", "elephone", "cat", "energizer",
        "nubia", "surface duo", "nothing"
    ]
    
    exclude_keywords = [
        "case", "cover", "stand", "charger", "screen protector", "Power Bank", "Projector", "Selfie Stick", "Wireless Charging",
        "battery", "earphones", "headphones", "cable", "adapter", "holder", "smartwatch", "Camera Lens", "Rotating Vertical Mobile Tripod Monopod",
        "Cleaner Kit", "Gaming Cooler", "Mini Projector", "Memory Card", "Sanitizer Kit", "Mount Strap", "Mobile Speaker",
        "Mic", "Screen Protect Plan", "Writing Pad", "Leather Belt", "Phone Shaker", "Installation Kit", "Card Reader", "SanDisk", "Gamepad", "Joysticks", "Cleaner",
        "Vlogging Stabilizer", "Phone Pouch", "Mouse", "Vlogging", "Sim Card", "Video Screen", "Microscope", "Item", "Smartphone Compatible",
        "Virtual Reality", "Headset", "Bluetooth", "Watch", "Pen", "Triggers", "Tempered Glass", "wifi", "Phone Accessories", "Fan", "Screen Protect Plan",
        "Telescope", "Phone Repair", "Retail Packaging", "lanyard", "Finger ", "Bike", "Leather", "spray", "wireless", "Teleprompter", "Physical Kit", "Lock Clamp",
        " USB Ports", "Handheld Stabilizer", "Magnetic Ring", "PopGrip", "Read", "Video", "Kit", "Charging", "speaker", "Screen Damage", "Desk Mount",
        "Extended Warranty", "Protection Plan", "OTG", "Keyboard", "Leather_Brown", "Stabilizer", "Earphone", "Headphone", "Bulb", " Liquid", "USB Hub",
    ]
    
    is_phone = any(keyword.lower() in product_name.lower() for keyword in include_keywords)
    is_accessory = any(keyword.lower() in product_name.lower() for keyword in exclude_keywords)
    
    return is_phone and not is_accessory

# Function to scrape product data from a search result page
def scrape_main_page(driver, main_page_url, existing_products_set):
    driver.get(main_page_url)
    time.sleep(random.uniform(2, 4))  # Wait for the page to load

    products = []
    items = driver.find_elements(By.XPATH, '//div[@data-component-type="s-search-result"]')

    for item in items:
        try:
            sponsored = item.find_elements(By.XPATH, './/span[contains(text(),"Sponsored")]')
            if sponsored:
                continue
            
            product_name = item.find_element(By.XPATH, './/h2/a').text.strip()
            if not is_phone(product_name) or product_name in existing_products_set:
                continue
            
            product_link = item.find_element(By.XPATH, './/h2/a').get_attribute('href')
            price = item.find_element(By.XPATH, './/span[@class="a-price-whole"]').text.strip()
            image_url = item.find_element(By.XPATH, './/img').get_attribute('src')
            rating = item.find_elements(By.XPATH, './/span[@class="a-icon-alt"]')
            rating = rating[0].text.split(' ')[0] if rating else "No rating"

            product = {
                "Product Name": product_name,
                "Price": price,
                "Image URL": image_url,
                "Product Link": product_link,
                # "Rating": rating
            }
            products.append(product)
            existing_products_set.add(product_name)
        except Exception as e:
            logging.error(f"Error scraping product: {e}")

    return products

# Function to iterate over multiple search result pages
def scrape_multiple_pages(base_url, total_pages):
    all_products = []
    existing_products_set = set()  # To keep track of unique product names
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")  # Start maximized for better visibility
    # Uncomment the line below for headless mode
    # chrome_options.add_argument("--headless")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        for page in range(1, total_pages + 1):
            if not driver.window_handles:  # Check if the Chrome window is closed
                print("Chrome window closed. Stopping the scraper.")
                break

            print(f"Scraping page {page}...")
            main_page_url = f"{base_url}&page={page}"
            products = scrape_main_page(driver, main_page_url, existing_products_set)
            all_products.extend(products)
            
            # Random sleep time between requests to avoid detection
            time.sleep(random.uniform(3, 5))
    finally:
        driver.quit()  # Ensure the driver is closed
        return all_products

# Main function
def main():
    base_url = "https://www.amazon.in/s?k=smartphone&i=electronics&crid=1M0WU9CT8275U&sprefix=%2Celectronics%2C333&ref=nb_sb_ss_recent_1_0_recent"
    total_pages = 400  # Adjust this as needed

    products = scrape_multiple_pages(base_url, total_pages)

    # Save the product data to a JSON file
    with open('amazon_mobiles.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=4)

    # Display the total number of products scraped
    print(f"Total products scraped: {len(products)}")
    print(f"Data saved to amazon_mobiles.json")

# Run the scraper
if __name__ == "__main__":
    main()
