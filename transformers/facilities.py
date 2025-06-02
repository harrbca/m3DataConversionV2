from .base import BaseTransformer

class FacilitiesTransformer(BaseTransformer):
    def get_facility(self):
        return getattr(self.row, 'RWARE#', '').strip()

    def get_warehouse(self):
        return getattr(self.row, 'RWARE#', '').strip()
