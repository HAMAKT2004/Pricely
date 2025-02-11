import scrapy
import json
import base64
import requests

# ✅ GitHub Repository Details
GITHUB_TOKEN = "ghp_kUV52GE9FkAGPtFOoP2XE6CajLDH12kaTfI"  # 🔴 Replace with your actual token
REPO_OWNER = "HAMAKT2004"
REPO_NAME = "Pricely-Data"
FILE_PATH = "amazon.json"
BRANCH = "main"

class AmazonSpider(scrapy.Spider):
    name = "amazon"
    allowed_domains = ["amazon.in"]
    start_urls = ["https://www.amazon.in/s?k=mobiles&i=electronics"]
    
    custom_settings = {
        "FEEDS": {
            "amazon_products.json": {"format": "json", "encoding": "utf8"},
        },
        "ROBOTSTXT_OBEY": False,  # Amazon blocks bots, so this needs to be False
        "DOWNLOAD_DELAY": 1.5,  # Prevent getting blocked
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1,
        "AUTOTHROTTLE_MAX_DELAY": 3,
    }

    def parse(self, response):
        products = response.css("div[data-component-type='s-search-result']")
        
        for product in products:
            yield {
                "Product Name": product.css("h2 span::text").get(default="N/A").strip(),
                "Price (₹)": product.css("span.a-price-whole::text").get(default="N/A").strip(),
                "Rating": product.css("span.a-icon-alt::text").get(default="N/A").split()[0],
                "Product Link": response.urljoin(product.css("a.a-link-normal::attr(href)").get(default="N/A")),
                "Image Link": product.css("img.s-image::attr(src)").get(default="N/A"),
            }

        # ✅ Follow the next page
        next_page = response.css("a.s-pagination-next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)


# ✅ Function to update JSON file on GitHub
def update_github_json():
    """Fetch 'amazon_products.json' from GitHub, replace it with new data, and commit the update."""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Load Scraped Data
    with open("amazon_products.json", "r", encoding="utf-8") as file:
        new_data = json.load(file)

    # 1️⃣ Fetch existing file to get SHA
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        file_data = response.json()
        sha = file_data['sha']  # Required for updating a file
    else:
        sha = None  # File doesn't exist; it'll be created

    # 2️⃣ Convert new_data to JSON string & encode in base64
    new_content = json.dumps(new_data, indent=4)
    encoded_content = base64.b64encode(new_content.encode()).decode()

    # 3️⃣ Send request to update the file
    payload = {
        "message": "Updated Amazon mobile data",
        "content": encoded_content,
        "branch": BRANCH
    }
    
    if sha:
        payload["sha"] = sha  # Include SHA only if updating

    update_response = requests.put(url, headers=headers, json=payload)

    if update_response.status_code in [200, 201]:
        print("✅ Successfully updated amazon_products.json on GitHub!")
    else:
        print(f"❌ GitHub Update Failed: {update_response.json()}")


# ✅ Run Scrapy and Upload Data
if __name__ == "__main__":
    import os
    os.system("scrapy crawl amazon")
    update_github_json()
