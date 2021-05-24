from app.scrapper.abstract.abstract_scrapper import AbstractSrapper
from playwright.async_api import async_playwright
from typing import List
from re import compile
from logging import getLogger

from app.model.product import Product
from app.model.availability import Availability


class AlltricksScrapper(AbstractSrapper):

    def __init__(self) -> None:
        self.logger = getLogger()
        self.url_regex = compile(r"^https://www.alltricks.fr/(.*)/(.*)$")
        self.site_name = "ALLTRICKS"

    def __check_url(self, url) -> bool:
        if not self.url_regex.match(url):
            self.logger.warn(
                f"{url} does not look like an alltricks product URL.")
            return False

        return True

    async def scrape(self, products: List[Product]):
        result: List[Availability] = []
        first_page = True

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            for product in products:
                self.logger.info(f"Processing {product.urls.alltricks_url}")
                if not product.urls.alltricks_url:
                    continue

                if not self.__check_url(product.urls.alltricks_url):
                    result.append(
                        Availability(product.name, product.option,
                                     self.site_name, None, None)
                    )
                    continue

                await page.goto(product.urls.alltricks_url)

                if first_page:
                    await page.click('xpath=//*[@id="didomi-notice-agree-button"]')
                    first_page = False

                is_multi = (await selector_multi.is_visible()) if (selector_multi := await page.query_selector(
                    "#product-header-order-size-select")) else False
                picker = await page.query_selector("#product-header-order-form")
                if is_multi:
                    option_regex = compile(product.option)
                    opts = await picker.query_selector_all(
                        ".alltricks-ChildSelector-customOption")
                    found = False
                    for opt in opts:
                        label = (await(await opt.query_selector(
                            ".alltricks-ChildSelector-customOptionLabel")).inner_text()).strip()
                        price = (await(await opt.query_selector(
                            ".alltricks-ChildSelector-customOptionPrice")).inner_text()).strip()
                        avail = (await (await (await opt.query_selector(
                            ".alltricks-ChildSelector-customOptionStockLabel")).query_selector("span")).inner_text()).strip()
                        if option_regex.match(label):
                            found = True
                            result.append(
                                Availability(
                                    product.name,
                                    product.option,
                                    self.site_name,
                                    avail not in [
                                        "Epuisé", "Retrait rapide en magasin"],
                                    self.parse_price(price)
                                )
                            )

                    if not found:
                        result.append(
                            Availability(
                                product.name,
                                product.option,
                                self.site_name,
                                False,
                                False
                            )
                        )

                else:
                    in_stock = await (await(await page.query_selector("#product-header-order")).query_selector('text="En stock"')).is_visible()
                    if in_stock:
                        price = (await (await page.query_selector('xpath=//*[@id="form_current_product"]/div[2]/div[1]/div[1]/p[1]')).inner_text()).strip()
                        result.append(
                            Availability(
                                product.name,
                                product.option,
                                self.site_name,
                                True,
                                self.parse_price(price)
                            )
                        )
                    else:
                        result.append(
                            Availability(
                                product.name,
                                product.option,
                                self.site_name,
                                False,
                                None
                            )
                        )

        return result
