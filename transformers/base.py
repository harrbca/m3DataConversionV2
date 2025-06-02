
class BaseTransformer:
    def __init__(self, row):
        self.row = row

    def get_value(self, field_name):
        return getattr(self.row, field_name, "")
