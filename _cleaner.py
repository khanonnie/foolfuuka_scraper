import os
import glob
import re
import time
import ftfy
from bs4 import BeautifulSoup
import concurrent.futures

MAX_THREADS = 4
BAD_FILENAME_PATTERN = re.compile("^([\d]{13}|[\da-f]+|file|(?!.*[ \-\_])(?=.*[0-9])(?=.*[a-zA-Z]).{7,}|(?=.*Screen[ \-_]?[Ss]hot).+)\.\w{3}$")
BAD_POST_PATTERN = re.compile(r"\AAnonymous - No.\d{9}\s(?:>>\d{9}\s)*\s*\Z", re.MULTILINE)

def parse_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        print(f"Reading {filename}...")
        content = f.read()
        print(f"Parsing {filename}...")
        soup = BeautifulSoup(content, "lxml")
        print(f"Cleaning {filename}...")
        cleaned_posts = []

        op_post = soup.find('article', attrs={'data-thread-num' : True})
        op_post_title = op_post.find('h2', class_='post_title').text
        op_post_id = f"No.{op_post.find(title='Reply to this post').text}"
        op_post_filename = get_post_filename(op_post.find('a', class_='post_file_filename'))
        op_post_text_node = op_post.find('div', class_='text')
        for br in op_post_text_node('br'):
            br.replace_with('\n')
        op_post_text = clean_text(op_post_text_node.get_text())
        op_post_final = f"{op_post_title} - Anonymous - {op_post_id}\n{op_post_filename}{op_post_text}"
        cleaned_posts.append(op_post_final)
        # if op_post_filename: print(op_post_filename)

        posts = soup.find_all('div', class_='post_wrapper')

        for p in posts:
            post_author = "Anonymous"
            post_id = f"No.{p.find(title='Reply to this post').text}"
            post_filename = get_post_filename(p.find('a', class_='post_file_filename'))
            post_text_node = p.find('div', class_='text')
            for br in post_text_node('br'):
                br.replace_with('\n')
            post_text = clean_text(post_text_node.get_text())
            post_final = f"{post_author} - {post_id}\n{post_filename}{post_text}"
            if should_ignore_post(post_final):
                print("Skipping post")
                print(post_final)
                continue
            cleaned_posts.append(post_final)
    all_posts = "\n".join(cleaned_posts)
    with open(f".\\cleaned\\Thread_{op_post_id}.txt", "wb") as fh:
        fh.write(all_posts.encode(encoding='UTF-8'))

def clean_text(text):
    text = text.strip()
    text = ftfy.fix_text(text).replace('…', '...').replace('\N{SOFT HYPHEN}', '').replace('\u200b', '').replace(u"\uFFFD", '').replace(u"\u009D", '').replace(u"\u0081", '') # cleanup unicode special
    text = re.sub(r'\n+', '\n', text, flags=re.M) # no extra linebreaks
    return text

# Returns formatted post filename if it seems relevant, given a beautifulsoup node
# Tries to omit uninteresting/generated filenames like:
# - reposted 4chan image ids
# - base16 filenames/uuid-like things (phoneposters)
# - 'file.jpg'
# - long strings of numbers/mixed case characters (imgur/reddit/tumblr filenames)
# - Screenshots
def get_post_filename(filename_node):
    if not filename_node: return ""
    
    has_title = "title" in filename_node.attrs
    filename = filename_node['title'] if has_title else filename_node.text
    if BAD_FILENAME_PATTERN.match(filename): return ""

    return f"File: {filename}\n"

# Detects post which contain no content or only contain quotes. Usually happens
# when someone replies with only an image, and the image was pruned by `get_post_filename`
def should_ignore_post(post_final):
    return bool(BAD_POST_PATTERN.match(post_final))

html_files = glob.glob(r"./*.html")
threads = min(MAX_THREADS, len(html_files))
with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
    executor.map(parse_file, html_files)
