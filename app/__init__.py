from app.scrapper.alltricks.alltricks_scrapper import AlltricksScrapper
from app.utils.logger import configure_root_logger
from app.model.urls_collection import UrlsCollecion
from app.scrapper.probikeshop.probikeshop_scrapper import ProbikeshopScrapper
from app.model.product import Product

from asyncio import get_event_loop, gather

async def run():
    logger = configure_root_logger()
    products = [
        Product("L03A", None, UrlsCollecion(
            "https://www.probikeshop.fr/plaquettes-resine-shimano-l-2a/115933.html", 
            "https://www.alltricks.fr/F-11934-plaquettes-de-frein/P-899495-paire_de_plaquettes_shimano_resine_l03a")),
        Product("CS-R8000-11.30", "(.*)11(.*)30(.*)", UrlsCollecion(
            "https://www.probikeshop.fr/cassette-shimano-11v-ultegra-8000/139465.html",
            "https://www.alltricks.fr/F-11911-cassettes/P-259868-cassette_shimano_ultegra_cs_r8000_11v"))
    ]
    logger.info("Scrapper started")
    result = [*await gather(ProbikeshopScrapper().scrape(products), AlltricksScrapper().scrape(products))]
    print(result)

def main():
    loop = get_event_loop()
    loop.run_until_complete(run())
    loop.close()