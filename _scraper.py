import requests
import time
from bs4 import BeautifulSoup

BASE_URL = "https://arch.b4k.co/vg/search/subject/%2Faids%2F/type/op/"

def main():
    search_loop()
    sleep(5)

def search_loop():
    print(f"Starting search... ({BASE_URL})")
    current_url = BASE_URL
    all_links = []
    while current_url != "#":
        print(f"Downloading search results... ({current_url})")
        response = requests.get(current_url)
        search_soup = BeautifulSoup(response.content, "html.parser")
        thread_links = get_thread_links(search_soup)

        if len(thread_links) == 0:
            print("No thread links found. Ending search loop.")
            current_url = None
            break

        all_links = all_links + thread_links
        print(f"Added {len(thread_links)} links ({all_links} total).")
        current_url = get_next_page_url(search_soup)
        time.sleep(0.5)
    
    print(all_links)
    with open("all_links.txt", "wb") as outfile:
        outfile.writelines("%s\n" % l for l in all_links)

def get_thread_links(soup):
    results = soup.find_all("span", class_="post_controls")
    result_links = []
    for r in results:
        result_links.append(r.find("a")["href"])
    return result_links

def get_next_page_url(soup):
    return soup.find(class_="next").a["href"]

main()
