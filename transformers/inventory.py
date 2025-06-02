from .base import BaseTransformer

class InventoryTransformer(BaseTransformer):
    def get_facility(self):
        return getattr(self.row, 'RWARE#', '').strip()

    def get_inventory_warehouse(self):
        return getattr(self.row, 'RWARE#', '').strip()

    def get_inventory_lot_number(self):
        return getattr(self.row, 'LOT#', '').strip()

    def get_inventory_last_receipt_date(self):
        return getattr(self.row, 'RLRCTD', '').strip()

    def get_country_of_origin(self):
        return "US"

    def get_status_balance_id(self):
        return 2

    def get_weighted_cost(self):
        return getattr(self.row, 'weightedCost', 0.0)

    def get_inventory_bin_location(self):
        return getattr(self.row, 'RLOC1', '').strip()

    def get_inventory_quantity(self):
        return getattr(self.row, "basic_uom_qty", 0.0)

    def get_inventory_status(self):
        return 2

