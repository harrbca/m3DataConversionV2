
from .base import BaseTransformer

class PriceTransformer(BaseTransformer):

    def get_price_list(self):
        return getattr(self.row, 'price_list_name', '').strip()

    def get_price_list_currency(self):
        return getattr(self.row, 'price_list_currency', '').strip()

    def get_price_valid_from_date(self):
        return getattr(self.row, 'valid_from', None)

    def get_sales_price(self):
        return getattr(self.row, 'sales_price', 0.0)
