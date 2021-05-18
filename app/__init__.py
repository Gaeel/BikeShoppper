from app.scrapper.alltricks.alltricks_scrapper import AlltricksScrapper
from app.utils.logger import configure_root_logger
from app.model.urls_collection import UrlsCollecion
from app.scrapper.probikeshop.probikeshop_scrapper import ProbikeshopScrapper
from app.model.product import Product

from pprint import pprint


def main():
    logger = configure_root_logger()
    products = [
        Product("L03A", None, UrlsCollecion(
            "https://www.probikeshop.fr/plaquettes-resine-shimano-l-2a/115933.html", None)),
        Product("CS-R8000-11.30", "(.*)11(.*)30(.*)", UrlsCollecion("https://www.probikeshop.fr/cassette-shimano-11v-ultegra-8000/139465.html",
                "https://www.alltricks.fr/F-11911-cassettes/P-259868-cassette_shimano_ultegra_cs_r8000_11v"))
    ]

    logger.info("Scrapping Probikesop")
    pbk_res = ProbikeshopScrapper().scrape(products)
    logger.info("Scrapping Alltricks")
    alltricks_res = AlltricksScrapper().scrape(products)

    pprint([*pbk_res, *alltricks_res])
