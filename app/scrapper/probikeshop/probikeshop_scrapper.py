from app.scrapper.abstract.abstract_scrapper import AbstractSrapper
from playwright.async_api import async_playwright
from typing import List
from re import compile
from logging import getLogger

from app.model.product import Product
from app.model.availability import Availability


class ProbikeshopScrapper(AbstractSrapper):

    def __init__(self) -> None:
        self.logger = getLogger()
        self.url_regex = compile(
            r"^https:\/\/www.probikeshop\.fr\/(.*)/(\d*).html$")
        self.site_name = "PROBIKESHOP"

    def __check_url(self, url) -> bool:
        if not self.url_regex.match(url):
            self.logger.warn(
                f"{url} does not look like a probikeshop product URL.")
            return False

        return True

    async def scrape(self, products: List[Product]):
        result: List[Availability] = []
        first_page = True

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            for product in products:
                self.logger.info(f"Processing {product.urls.probikeshop_url}")
                if not product.urls.probikeshop_url:
                    continue

                if not self.__check_url(product.urls.probikeshop_url):
                    result.append(
                        Availability(product.name, product.option,
                                     self.site_name, None, None)
                    )
                    continue

                await page.goto(product.urls.probikeshop_url)

                # Accept and close cookies popup
                if first_page:
                    await page.click('xpath=//*[@id="onetrust-accept-btn-handler"]')
                    first_page = False

                price = self.parse_price(
                    (await page.inner_text("#product-price")).strip())
                avail = len(await page.query_selector_all(
                    ".productPageContentInfosTop_stockOut")) == 0

                if avail and product.option:
                    page_has_option_selector = len(
                        await page.query_selector_all("#add-product-select")) != 0
                    if not page_has_option_selector:
                        self.logger.warn(
                            f"An option ({product.option}) has been specified but this product ({product.name}) does not has options according to ProbikeShop")
                        avail = False

                    options_found = await page.query_selector_all(
                        "#add-product-select > option")
                    option_regex = compile(product.option)
                    options_matching = [ opt for opt in options_found if bool(option_regex.match((await opt.inner_text()).strip())) ]
                    
                    if not options_matching:
                        avail = False
                    else:
                        # Update price with option's overcost
                        matching_opt = options_matching[0]
                        overcost = float(
                            await matching_opt.get_attribute("overcost"))
                        price += overcost

                result.append(Availability(
                    product.name, product.option, self.site_name, avail, price))

        return result
