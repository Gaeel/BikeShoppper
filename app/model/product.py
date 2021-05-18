from dataclasses import dataclass
from typing import Optional

from app.model.urls_collection import UrlsCollecion

@dataclass
class Product:
    name: str
    option: Optional[str]
    urls: UrlsCollecion