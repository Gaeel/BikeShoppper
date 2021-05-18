from playwright.sync_api import sync_playwright
from typing import List
from re import compile
from logging import getLogger

from app.model.product import Product
from app.model.availability import Availability

class ProbikeshopScrapper:

    def __init__(self) -> None:
        self.logger = getLogger()
        self.url_regex = compile(r"^https:\/\/www.probikeshop\.fr\/(.*)/(\d*).html$")
        self.site_name = "PROBIKESHOP"

    def __check_url(self, url) -> bool:
        if not self.url_regex.match(url):
            self.logger.warn(f"{url} does not look like a probikeshop product URL.")
            return False

        return True

    def scrape(self, products: List[Product]):
        result: List[Availability] = []
        first_page = True
        price_regxp = compile(r'^(\d*),(\d*).*€$')

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            for product in products:
                self.logger.info(f"Processing {product.urls.probikeshop_url}")
                if not product.urls.probikeshop_url:
                    continue

                if not self.__check_url(product.urls.probikeshop_url):
                    result.append(
                        Availability(product.name, product.option, self.site_name, None, None)
                    )
                    continue
                    
                page.goto(product.urls.probikeshop_url)
                
                # Accept and close cookies popup
                if first_page:
                    page.click('xpath=//*[@id="onetrust-accept-btn-handler"]')
                    first_page = False
                
                price = page.inner_text("#product-price").strip()
                price_match = price_regxp.match(price)
                price_int_part = int(price_match.group(1))
                price_dec_par = int(price_match.group(2))
                final_price = price_int_part + price_dec_par / 100
                avail = len(page.query_selector_all(".productPageContentInfosTop_stockOut")) == 0

                if avail and product.option:
                    page_has_option_selector = len(page.query_selector_all("#add-product-select")) != 0
                    if not page_has_option_selector:
                        self.logger.warn(f"An option ({product.option}) has been specified but this product ({product.name}) does not has options according to ProbikeShop")
                        avail = False

                    options_found = page.query_selector_all("#add-product-select > option")
                    option_regex = compile(product.option)
                    options_matching = list(filter(lambda opt: bool(option_regex.match(opt.inner_text().strip())), options_found))
                    if not options_matching:
                        avail = False
                    else:
                        # Update price with option's overcost
                        matching_opt = options_matching[0]
                        overcost = float(matching_opt.get_attribute("overcost"))
                        final_price += overcost


                result.append(Availability(product.name, product.option, self.site_name, avail, final_price))
            
        return result