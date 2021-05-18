from dataclasses import dataclass
from typing import Optional

@dataclass
class Availability:
    product_name: str
    product_option: str
    site_name: str
    is_available: bool
    price: Optional[float]