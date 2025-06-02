from transformers.base import BaseTransformer
import re

class BWLItemTransformer(BaseTransformer):

    def get_item_number(self):
        item_number = getattr(self.row, 'itemNumber', '').strip()

        if len(item_number) < 3:
            return item_number  # Return as is if item_number is too short

        mfgr_prefix = item_number[:3]  # Get the first three characters
        item_suffix = item_number[3:]  # The rest of the item number

        # Define special cases for manufacturer prefixes
        special_prefixes = {"CAS": "CA", "CAR": "CR", "CAP": "CP"}

        # Determine new prefix
        new_prefix = special_prefixes.get(mfgr_prefix, mfgr_prefix[:2])

        cleaned_item_number = new_prefix + item_suffix

        return self._sanitize(cleaned_item_number)

    def _sanitize(self, value: str) -> str:
        return re.sub(r"[ \\/&.]", "_", value)