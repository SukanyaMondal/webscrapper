import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from itertools import zip_longest

base_url = "https://rategain.com/blog"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def extract_data(url):
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract blog titles, dates, likes, and image URLs here
        
        # Extract blog titles
        blog_titles = [title.text.strip() for title in soup.select('.content h6 a')]

        # Extract publication dates
        blog_dates = [date.text.strip() for date in soup.select('.blog-detail div.bd-item:first-of-type span')]

        # Extract blog likes
        likes_count = [re.search(r'\d+', like.text.strip()).group() for like in soup.select('.zilla-likes span') if re.search(r'\d+', like.text.strip())]

        # Extract image URLs, considering missing image URLs
        blog_image_urls = [img['data-bg'] if img.get('data-bg') else None for img in soup.select('.img a[data-bg]')]

        return blog_titles, blog_dates, likes_count, blog_image_urls
    else:
        print(f"Failed to fetch the webpage at URL: {url}")
        return [], [], [], []

def main():
    base_url = "https://rategain.com/blog"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    current_page = 1
    all_data = {
        'Title': [],
        'Date': [],
        'Likes': [],
        'Image_URL': []
    }

    while True:
        current_url = base_url if current_page == 1 else f"{base_url}/page/{current_page}/"
        titles, dates, likes, images = extract_data(current_url)
        
        max_len = max(len(titles), len(dates), len(likes), len(images))
        titles.extend([None] * (max_len - len(titles)))
        dates.extend([None] * (max_len - len(dates)))
        likes.extend([None] * (max_len - len(likes)))
        images.extend([None] * (max_len - len(images)))
        
        all_data['Title'].extend(titles)
        all_data['Date'].extend(dates)
        all_data['Likes'].extend(likes)
        all_data['Image_URL'].extend(images)

        # Check for the next page or break the loop
        next_page = current_page + 1
        next_page_link = f"{base_url}/page/{next_page}/"
        
        response = requests.get(next_page_link, headers=headers)
        if response.status_code != 200 or f'page-numbers current">{next_page}</span>' not in response.text:
            break
        
        current_page = next_page

    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    df.to_csv('blog_data.csv', index=False)  # saving data to CSV

if __name__ == "__main__":
    main()