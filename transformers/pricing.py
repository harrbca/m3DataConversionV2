
from .base import BaseTransformer

class PricingTransformer(BaseTransformer):
    def get_trend_curve(self):
        return "DEFAULT_TREND"

    def get_tolerance_catch_weight(self):
        return "1.0"
