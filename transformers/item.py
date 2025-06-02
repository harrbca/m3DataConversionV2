
from .base import BaseTransformer

class ItemTransformer(BaseTransformer):
    def get_item_number(self):
        return getattr(self.row, 'itemNumber', '').strip()

    def get_item_group(self):
        return getattr(self.row, 'priceClass', '').strip()

    def get_description(self):
        return getattr(self.row, 'description', '').strip()

    def get_name(self):
        return getattr(self.row, 'name', '').strip()

    def get_basic_uom(self):
        if getattr(self.row, 'ICOMPO', '') == 'R':
            return "LF"
        else:
            if getattr(self.row, 'IUM2') is None:
                return getattr(self.row, 'IUNITS', '').strip()
            else:
                return getattr(self.row, 'IUM2', '').strip()