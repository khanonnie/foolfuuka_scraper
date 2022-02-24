import requests
import time
from bs4 import BeautifulSoup
import concurrent.futures

MAX_THREADS = 5

def main():
    urls = open('output.txt', 'r')
    all_urls = urls.readlines()

    print(f"Starting download of {len(all_urls)} threads...")
    download_urls(all_urls)

def download_urls(urls):
    threads = min(MAX_THREADS, len(urls))
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(download_url, urls)

def download_url(url):
    print(f"Downloading {url}...")
    resp = requests.get(url)
    title = ''.join(x for x in url if x.isalnum()) + ".html"
    with open(title, "wb") as fh:
        fh.write(resp.content)
    time.sleep(0.25)

main()
