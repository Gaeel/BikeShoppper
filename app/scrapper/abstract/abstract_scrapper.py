from re import compile


class AbstractSrapper:
    def parse_price(self, price: str):
        price_regxp = compile(r'^(\d*),(\d*).*€$')
        price_match = price_regxp.match(price)
        price_int_part = int(price_match.group(1))
        price_dec_par = int(price_match.group(2))
        return price_int_part + price_dec_par / 100
