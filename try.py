import requests
from bs4 import BeautifulSoup

url = "https://news.ycombinator.com/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Extract top story titles
    titles = soup.find_all("a", class_="storylink")
    
    for idx, title in enumerate(titles[:5], 1):
        print(f"{idx}. {title.text}")
else:
    print("Failed to fetch Hacker News.")
