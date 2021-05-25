from sqlalchemy import Column, String, Float, Boolean, DateTime
from app.schema import Base

class ProductAvailability(Base):
    __tablename__ = "ProductAvailability"
    product_name = Column(String, primary_key=True)
    product_option = Column(String)
    site_name = Column(String)
    is_available = Column(Boolean)
    price = Column(Float)
    timestamp = Column(DateTime)