from playwright.sync_api import sync_playwright
from typing import List
from re import compile
from logging import getLogger

from app.model.product import Product
from app.model.availability import Availability

class AlltricksScrapper:

    def __init__(self) -> None:
        self.logger = getLogger()
        self.url_regex = compile(r"^https://www.alltricks.fr/(.*)/(.*)$")
        self.site_name = "PROBIKESHOP"

    def __check_url(self, url) -> bool:
        if not self.url_regex.match(url):
            self.logger.warn(f"{url} does not look like an alltricks product URL.")
            return False

        return True
    
    def scrape(self, products: List[Product]):
        result: List[Availability] = []
        first_page = True

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            for product in products:
                self.logger.info(f"Processing {product.urls.alltricks_url}")
                if not product.urls.alltricks_url:
                    continue
                
                if not self.__check_url(product.urls.alltricks_url):
                    result.append(
                        Availability(product.name, product.option, self.site_name, None, None)
                    )
                    continue
                
                page.goto(product.urls.alltricks_url)
                
                if first_page:
                    page.click('xpath=//*[@id="didomi-notice-agree-button"]')
                    first_page = False
                    

                price = page.inner_text('xpath=//*[@id="form_current_product"]/div[8]/div[1]/div[1]/p[1]/span').strip()
                
            
        return result