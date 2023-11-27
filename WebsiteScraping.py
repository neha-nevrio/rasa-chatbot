import time
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


urls = {
        "url": 'https://www.flexispy.com',
        "path": r'Knowledge\flexispy_data.txt'
    }

allLinks = []


options = webdriver.ChromeOptions()
options.headless = True  # it's more scalable to work in headless mode
options.page_load_strategy = 'none'
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options=options)
driver.implicitly_wait(5)

def extract_links(urlToParse):
    driver.get(urlToParse)
    time.sleep(4)
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    anchor_tags = soup.find_all("a", href=True)
    special_char = re.compile('#')
    href_links = [tag['href'] for tag in anchor_tags if special_char.search(tag['href']) is None]
    href_links = [url["url"] + link for link in href_links if link.count("https") == 0]

    print('href_links ->', href_links)

    for each_link in href_links:

            if each_link not in allLinks and each_link.count('flexispy.com') == 1:
                try:
                    print(each_link)
                    allLinks.append(each_link)

                    with open("all_links.txt", mode='a+') as file:
                        file.write(str(each_link) + "\n")

                    extract_links(each_link)
                except:
                    continue


    return allLinks


def extract_data(data_path):
    print(allLinks)
    print(f"NUMBER of LINKS : {len(allLinks)}")
    for each_link in allLinks:
        try:
            driver.get(each_link)
            time.sleep(5)

            filtered_text = driver.find_element(By.XPATH, "/html/body").text

            for text in filtered_text:
                with open(data_path, "a+") as f:
                    f.write(text)
        except Exception as e:
            continue


for url in urls:
    print(url)
    allLinks.append(url["url"])
    extract_links(url["url"])
    extract_data(url["path"])
    allLinks = []

driver.close()