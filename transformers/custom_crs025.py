
from .item import ItemTransformer

class CustomCRS025Transformer(ItemTransformer):
    def get_name(self):
        return f"Overridden-{self.row.itemNumber}"
