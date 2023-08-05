import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = 'https://www.truepeoplesearch.com'
SEED_URL = 'https://www.truepeoplesearch.com/find/smith'
PROXY_FILE = 'proxies.txt'
PROCESSED_URLS_FILE = 'processed_urls.txt'
OUTPUT_FILE = 'output.txt'

def load_proxies():
    with open(PROXY_FILE, 'r') as f:
        proxies = f.read().splitlines()
    return proxies

def save_processed_url(url):
    with open(PROCESSED_URLS_FILE, 'a') as f:
        f.write(url + '\n')

def is_processed(url):
    with open(PROCESSED_URLS_FILE, 'r') as f:
        processed_urls = f.read().splitlines()
    return url in processed_urls

def scrape_page(url, proxies):
    options = Options()
    driver = webdriver.Chrome(options=options)

    try:
        # Установить прокси, если доступны
        if proxies:
            proxy = proxies.pop(0)
            options.add_argument('--proxy-server=http://{}'.format(proxy))
        
        driver.get(url)

        # Дождитесь загрузки страницы
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="your-element-id"]')))

        # Получите содержимое элемента, который вы хотите скрапить
        element = driver.find_element(By.XPATH, '//*[@id="your-element-id"]')
        content = element.get_attribute('innerText')

        # Теперь вы можете обработать содержимое элемента, например, записать его в файл
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            f.write(content + '\n')

        # Сохраните URL в списке обработанных
        save_processed_url(url)

        # Найдите ссылки на странице и пройдите по ним рекурсивно
        links = driver.find_elements(By.TAG_NAME, 'a')
        for link in links:
            href = link.get_attribute('href')
            if href and href.startswith(BASE_URL) and not is_processed(href):
                scrape_page(href, proxies)

    except Exception as e:
        print(f"Произошла ошибка при обработке страницы: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    proxies = load_proxies()
    scrape_page(SEED_URL, proxies)
