from sqlalchemy.orm import sessionmaker
from app.schema.product_availabity import ProductAvailability
from app.scrapper.alltricks.alltricks_scrapper import AlltricksScrapper
from app.utils.logger import configure_root_logger
from app.model.urls_collection import UrlsCollecion
from app.scrapper.probikeshop.probikeshop_scrapper import ProbikeshopScrapper
from app.model.product import Product
from app.utils.pushbullet_client import PushBulletClient
from app.config.pushbullet import PUSHBULLET_TOKEN
from app.config.database import DATABASE_URI

from asyncio import get_event_loop, gather
from textwrap import dedent
from itertools import chain
from sqlalchemy import create_engine
from datetime import datetime


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
    result = await gather(ProbikeshopScrapper().scrape(products), AlltricksScrapper().scrape(products))
    flat_res = list(chain(*result))

    engine = create_engine(DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()

    pb = PushBulletClient(PUSHBULLET_TOKEN)

    for availability in flat_res:
        if availability.is_available:
            this_product = session.query(ProductAvailability).filter_by(product_name=availability.product_name).order_by(ProductAvailability.timestamp).one()
            print(this_product)
            if not this_product:
                session.add(
                    ProductAvailability(
                        product_name = availability.product_name,
                        product_option = availability.product_option,
                        site_name = availability.site_name,
                        is_available = availability.is_available,
                        price = availability.price,
                        timestamp = datetime.now()
                    )
                )
        

            opt_msg = f"with option like {availability.product_option}" if availability.product_option else ""
            message = dedent(f"""
            Hey, {availability.product_name} {opt_msg} is now available on {availability.site_name} for {availability.price:.2f}€!
            Order now at: {availability.url}
            
            Your humble servant, BikeShoper!
            """)
            pb.notify("A product is available!", message)

    session.commit()
    pb.close()
    print(result)

def main():
    loop = get_event_loop()
    loop.run_until_complete(run())
    loop.close()