from .base import BaseTransformer

class ItemGroupTransformer(BaseTransformer):
    def get_item_group(self):
        return getattr(self.row, 'IPRCCD', "").strip()

    def get_item_group_description(self):
        return getattr(self.row, 'IPRCCD_description', "").strip()

    def get_item_group_name(self):
        return self.get_item_group_description()[:15]
