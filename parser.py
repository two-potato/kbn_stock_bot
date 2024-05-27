import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


# TODO: вывод ссылок, если их много. проверка существует ли ссылка. если нет, бот пишет сообщение
def get_product_url(search_query):
    # search_url = f"https://spb.complexbar.ru/catalogsearch/result/?q={search_query}"
    search_url = f"https://spb.complexbar.ru/?match=all&subcats=Y&pcode_from_q=Y&pshort=Y&pfull=Y&pname=Y&pkeywords=Y&search_performed=Y&q={search_query}&dispatch=products.search&security_hash=79bedb42e2ceb29d2274d45831b8ec7c"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, "html.parser")
    product_link = soup.find("div", class_="ut2-gl__name cmx-product-name").find("a")[
        "href"
    ]
    title = soup.find("a", class_="product-title").text
    price = soup.find("span", class_="ty-price").text
    brand = soup.find(
        "div", class_="cmx-product-grid__item-brand cmx-products-brand-name"
    ).text
    print(title)
    print(brand)
    print(price)
    product_data = {
        "title": title,
        "price": price,
        "brand": brand,
        "url": f"https://spb.complexbar.ru/{product_link}",
    }
    if product_link:
        print(product_link)
        # return f"https://spb.complexbar.ru/{product_link}"
        return product_data
    else:
        return None


def parse_product_info(search_query):
    product_data = get_product_url(search_query)
    product_url = product_data["url"]
    product_title = product_data["title"]
    print(product_title)
    if not product_url:
        return "Product not found."

    options = webdriver.ChromeOptions()
    # driver = webdriver.Remote(
    #     command_executor="http://selenium-hub:4444/wd/hub", options=options
    # )
    driver = webdriver.Chrome()

    try:
        driver.get(product_url)
        clarify_stock_link = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "ga-clarify-stock"))
        )
        clarify_stock_link.click()
        stock_info = WebDriverWait(driver, 5).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "product-stock-info"))
        )
        stock_details = stock_info.text
        stock_warehouse = (
            WebDriverWait(driver, 5)
            .until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        "//span[contains(text(), 'На складе:')]/following-sibling::span",
                    )
                )
            )
            .text
        )
        remote_warehouse = (
            WebDriverWait(driver, 5)
            .until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        "//span[contains(text(), 'На удаленном складе:')]/following-sibling::span",
                    )
                )
            )
            .text
        )
        showroom_stock = (
            WebDriverWait(driver, 10)
            .until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        "//span[contains(text(), 'В шоуруме:')]/following-sibling::span",
                    )
                )
            )
            .text
        )
        data = {
            "stock_warehouse": stock_warehouse,
            "remote_warehouse": remote_warehouse,
            "showroom_stock": showroom_stock,
            "title": product_title,
            "price": product_data["price"],
            "brand": product_data["brand"],
        }
        print(data)
        return data
    # (
    #         # f"Это:{title}\n"
    #         f"Stock Information:\n{stock_details}\n\n"
    #         f"Warehouse Stock:\n{stock_warehouse}\n\n"
    #         f"Remote Warehouse Stock:\n{remote_warehouse}\n\n"
    #         f"Showroom Stock:\n{showroom_stock}"
    #     )
    except TimeoutException as e:
        return f"Error: {str(e)}"
    finally:
        driver.quit()
