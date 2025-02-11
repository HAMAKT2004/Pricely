import requests
from bs4 import BeautifulSoup
import json
import time
import logging
import random

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
    # List of popular smartphone brands
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
    
    # List of accessories and non-phone products to exclude
    exclude_keywords = [
        "case", "cover", "stand", "charger", "screen protector", "Power Bank", "Projector", "Selfie Stick", "Wireless Charging",
        "battery", "earphones", "headphones", "cable", "adapter", "holder", "smartwatch", "Camera Lens", "Rotating Vertical Mobile Tripod Monopod",
        "Cleaner Kit", "Gaming Cooler", "Mini Projector", "Memory Card", "Sanitizer Kit", "Mount Strap", "Mobile Speaker", "monopod", "tripod",
        "Mic", "Screen Protect Plan", "Writing Pad", "Leather Belt", "Phone Shaker", "Installation Kit", "Card Reader", "SanDisk", "Gamepad", "Joysticks", "Cleaner",
        "Vlogging Stabilizer", "Phone Pouch", "Mouse", "Vlogging", "Sim Card", "Video Screen", "Microscope", "Item", "Smartphone Compatible",
        "Virtual Reality", "Headset", "Bluetooth", "Watch", "Pen", "Triggers", "Tempered Glass", "wifi", "Phone Accessories", "Fan", "Screen Protect Plan",
        "Telescope", "Phone Repair", "Retail Packaging", "lanyard", "Finger ", "Bike", "Leather", "spray", "wireless", "Teleprompter", "Physical Kit", "Lock Clamp",
        "USB Ports", "Handheld Stabilizer", "Magnetic Ring", "PopGrip", "Read", "Video", "Kit", "Charging", "speaker", "Screen Damage", "Desk Mount",
        "Extended Warranty", "Protection Plan", "OTG", "Keyboard", "Leather_Brown", "Stabilizer", "Earphone", "Headphone", "Bulb", "Liquid", "USB Hub",
    ]
    
    # Check if the product name contains any of the smartphone brand names or keywords
    is_phone = any(keyword.lower() in product_name.lower() for keyword in include_keywords)
    
    # Check if the product name contains any accessory-related keywords
    is_accessory = any(keyword.lower() in product_name.lower() for keyword in exclude_keywords)
    
    # Return True if it's a phone and not an accessory, ensuring we exclude any product that contains both
    return is_phone and not is_accessory

# Function to scrape product data from a search result page
def scrape_main_page(main_page_url, existing_products_set):
    headers = {"User-Agent": get_random_user_agent()}
    response = requests.get(main_page_url, headers=headers)
    if response.status_code != 200:
        logging.error(f"Failed to retrieve page: {main_page_url} - Status Code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    products = []

    for item in soup.find_all('div', {'data-component-type': 's-search-result'}):
        try:
            # Avoid sponsored or advertisement products
            sponsored = item.find('span', class_='s-label-popover-default')
            if sponsored and 'Sponsored' in sponsored.text:
                continue
            
            product_name = item.h2.a.text.strip()
            
            # Filter to only include phones, excluding accessories
            if not is_phone(product_name) or product_name in existing_products_set:
                continue
            
            product_link = "https://www.amazon.in" + item.h2.a['href']
            price = item.find('span', 'a-price-whole')
            price = price.text.strip() if price else "N/A"
            image_url = item.find('img')['src']
            
            # Fetching the rating
            rating = item.find('span', class_='a-icon-alt')
            rating = rating.text.split(' ')[0] if rating else "No rating"
            
            product = {
                "Product Name": product_name,
                "Price": price,
                "Image URL": image_url,
                "Product Link": product_link,
                "Rating": rating
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
    
    try:
        for page in range(1, total_pages + 1):
            print(f"Scraping page {page}...")
            main_page_url = f"{base_url}&page={page}"
            products = scrape_main_page(main_page_url, existing_products_set)
            all_products.extend(products)
            
            # Random sleep time between requests to avoid detection
            time.sleep(random.uniform(3, 5))
    
    except KeyboardInterrupt:
        print("Scraping stopped by user.")
        # Save the product data to a JSON file when interrupted
        with open('amazon_products.json', 'w', encoding='utf-8') as f:
            json.dump(all_products, f, ensure_ascii=False, indent=4)
        print(f"Scraped data saved to 'amazon_products.json'. Total products saved: {len(all_products)}")
    
    return all_products

# Main function
def main():
    base_url = "https://www.amazon.in/s?k=smartphone&i=electronics&crid=1M0WU9CT8275U&sprefix=%2Celectronics%2C333&ref=nb_sb_ss_recent_1_0_recent"
    total_pages = 400  # Adjust this as needed

    products = scrape_multiple_pages(base_url, total_pages)

    # Save the product data to a JSON file if completed normally
    with open('amazon_products.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=4)
    
    # Display the total number of products saved
    print(f"Scraping completed. Total products saved: {len(products)}")

# Run the scraper
if __name__ == "__main__":
    main()
