#!/usr/bin/env python3

import argparse

# Parse the arguments from the command line
from collections import deque
from pprint import pprint
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


def get_all_links_from_page(url):
    try:
        # Send a request to the website
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)

        # Check if the request was successful (HTTP status code 200)
        if response.status_code == 200:
            # Parse the HTML response
            soup = BeautifulSoup(response.text, "html.parser")

            # Find all <td> tags with the class "link"
            table_cells = soup.find_all("td", class_="link")

            # Create a list to store the results
            links_data = []

            # Iterate over each element and extract href and title
            for cell in table_cells:
                link = cell.find("a")  # Find <a> tag inside <td>
                if link:
                    href = link.get("href")  # Extract the href attribute
                    title = link.get("title")  # Extract the title attribute
                    if href and title:
                        # Combine base URL with href to create full URL
                        full_url = urljoin(url, href)
                        # Add the data to the list
                        links_data.append({"title": title, "link": full_url})
            return links_data
        else:
            print(f"Error: HTTP status code {response.status_code}")

    except Exception as e:
        print(f"Error during scraping: {e}")


def main():
    # Set up argparse to take arguments from the command line
    parser = argparse.ArgumentParser(
        description="Scrape links from a website and save them in a JSON file."
    )
    parser.add_argument("url", help="The URL of the website to scrape.")

    args = parser.parse_args()

    # Run the scraping function
    seen = set(["../"])
    link_queue = deque([args.url])
    output_data = deque()
    while link_queue:
        current_url = link_queue.popleft()
        if current_url in seen:
            continue
        seen.add(current_url)
        links_data = get_all_links_from_page(current_url)
        if links_data:
            # trailing slash are pages
            for obj in links_data:
                link = obj["link"]
                if link.endswith("/"):
                    link_queue.append(link)
                else:
                    output_data.append(obj)
        pprint(output_data)
    print(output_data)


if __name__ == "__main__":
    main()
