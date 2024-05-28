import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options

import logging

logging.basicConfig(level=logging.INFO)


def get_product_url(search_query):
    search_url = f"https://spb.complexbar.ru/?match=all&subcats=Y&pcode_from_q=Y&pshort=Y&pfull=Y&pname=Y&pkeywords=Y&search_performed=Y&q={search_query}&dispatch=products.search&security_hash=79bedb42e2ceb29d2274d45831b8ec7c"

    try:
        response = requests.get(search_url)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error fetching search results: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    try:
        product_link = soup.find("div", class_="ut2-gl__name cmx-product-name").find(
            "a"
        )["href"]
        title = soup.find("a", class_="product-title").text.strip()
        price = soup.find("span", class_="ty-price").text.strip()
        brand = soup.find(
            "div", class_="cmx-product-grid__item-brand cmx-products-brand-name"
        ).text.strip()
    except AttributeError as e:
        logging.error(f"Error parsing product details: {e}")
        return None

    product_data = {
        "title": title,
        "price": price,
        "brand": brand,
        "url": f"https://spb.complexbar.ru/{product_link}",
    }

    return product_data


def fetch_stock_info(driver, xpath):
    try:
        return (
            WebDriverWait(driver, 5)
            .until(EC.visibility_of_element_located((By.XPATH, xpath)))
            .text.strip()
        )
    except TimeoutException:
        logging.warning(f"Timeout while fetching stock info for xpath: {xpath}")
        return "Not available"


def parse_product_info(search_query):
    product_data = get_product_url(search_query)
    if not product_data:
        return None

    product_url = product_data.get("url")
    if not product_url:
        return None

    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--headless")
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)

    try:
        driver.get(product_url)
        clarify_stock_link = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "ga-clarify-stock"))
        )
        clarify_stock_link.click()

        stock_info = {
            "stock_warehouse": fetch_stock_info(
                driver, "//span[contains(text(), 'На складе:')]/following-sibling::span"
            ),
            "remote_warehouse": fetch_stock_info(
                driver,
                "//span[contains(text(), 'На удаленном складе:')]/following-sibling::span",
            ),
            "showroom_stock": fetch_stock_info(
                driver, "//span[contains(text(), 'В шоуруме:')]/following-sibling::span"
            ),
        }

        data = {
            "title": product_data.get("title", "Неизвестно"),
            "price": product_data.get("price", "Неизвестно"),
            "brand": product_data.get("brand", "Неизвестно"),
            **stock_info,
            "url": product_url,
        }
        logging.info(f"Product data: {data}")
        return data
    except TimeoutException as e:
        logging.error(f"Error: {e}")
        return None
    finally:
        driver.quit()
