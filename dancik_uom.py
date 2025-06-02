import logging
from collections import deque
from database import Database
from config_reader import ConfigReader
from pprint import pprint
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_DOWN


class UOMService:
    def __init__(self, item_number, final_result_precision=2):
        # setup logging
        self.logger = logging.getLogger(__name__)
        self.final_result_precision = final_result_precision
        self.db = Database()
        self.item_number = item_number
        self.config = ConfigReader.get_instance()
        query_path = self.config.get("QUERIES", "dancik_package_query_path", "queries/dancik_package_query.sql")
        query_item_package_path = self.config.get("QUERIES", "dancik_package_item_query_path", "queries/dancik_package_item_query.sql")
        with open(query_path) as file:
            self.package_query = file.read()
        with open(query_item_package_path) as file:
            self.item_package_query = file.read()
        self.item_details = self._load_item_details()
        self._build_bidirectional_conversion_graph()
        self.logger.debug("Conversion graph:")
        self.logger.debug(self.graph)


    def _load_item_details(self):
        with self.db as db:
            df = db.fetch_dataframe(self.package_query, (self.item_number,))


        if df.empty:
            with self.db as db:
                df = db.fetch_dataframe(self.item_package_query,(self.item_number,))

        if df.empty:
            print(f"Error: No item details found for item number {self.item_number}")
            return None

        if len(df) > 1:
            print(f"Error: Multiple item details found for item number {self.item_number}")
            return None

        return df.iloc[0].to_dict()

    def _add_conversion_to_graph(self,  qty,  to_uom,  from_uom):
        graph = self.graph
        try:
            dec_qty = Decimal(str(qty))
        except Exception as e:
            print(f"Error: Unable to convert quantity {qty} to decimal: {e} for item number {self.item_number} package class {self.item_details['IPACCD']}.")
            return

        if to_uom not in graph:
            graph[to_uom] = {}
        if from_uom not in graph:
            graph[from_uom] = {}

        graph[to_uom][from_uom] = Decimal("1") / dec_qty
        graph[from_uom][to_uom] = dec_qty

    def _build_bidirectional_conversion_graph(self):
        item_details = self.item_details
        self.graph = {}
        if item_details is None:
            return


        for i in range(1, 7):
            qty_key = f"UMF_{i}"
            to_uom_key = f"UM1_{i}"
            from_uom_key = f"UM2_{i}"

            if qty_key in item_details and to_uom_key in item_details and from_uom_key in item_details:
                qty = item_details[qty_key]
                to_uom = item_details[to_uom_key]
                from_uom = item_details[from_uom_key]
                if qty == 0:
                    continue
                self._add_conversion_to_graph(qty, to_uom, from_uom)

        if item_details["ICOMPO"] == 'R':
            self._add_conversion_to_graph(9, "SF", "SY")

            width = Decimal(str(item_details["IWIDTH"]))
            if width == 0:
                width = Decimal("72")  # default width in inches

            # Because your system expects: 1 SY = factor × IN
            in_to_sy_inverse = Decimal("1296") / width
            self._add_conversion_to_graph(in_to_sy_inverse, "IN", "SY")

            # SF to LF: 1 LF = 1 SF / (width in feet)
            width_feet = width / Decimal("12")
            self._add_conversion_to_graph(width_feet, "SF", "LF")

    def _find_conversion_path(self, from_uom, to_uom):
        if from_uom not in self.graph or to_uom not in self.graph:
            raise ValueError(f"Cannot convert between {from_uom} and {to_uom} for item number {self.item_number}")

        path = []

        # initialize the queue with the from_uom, conversion factor 1, and an empty path
        # this way, if you are convertion from CT to CT ( why, could happen ), the conversion rate is authomatically 1;
        # plus, this primes the system
        queue = deque([(from_uom, [], Decimal("1"))])
        visited = set()


        while queue:
            current_unit, path, factor = queue.popleft()
            if current_unit in visited:
                continue
            visited.add(current_unit)

            if current_unit == to_uom:
                return path  # Return list of conversion steps

            for neighbor, conversion_rate in self.graph[current_unit].items():
                if neighbor not in visited:
                    queue.append((neighbor, path + [(current_unit, neighbor, conversion_rate)], conversion_rate))

        #raise ValueError(f"No conversion path found between {from_uom} and {to_uom} for item {self.item_number}.")
        print (f"Error: No conversion path found between {from_uom} and {to_uom} for item {self.item_number}.")
        return []

    def get_uom_list(self):
        return list(self.graph.keys())

    def has_uom(self, uom):
        """
        Check if the item has a specific UOM in its conversion graph.
        """
        return uom in self.graph.keys()

    def convert(self, value, from_uom, to_uom, final_result_precision=2):
        if from_uom == to_uom:
            return value
        if self.item_details is None:
            return None

        conversion_steps = self._find_conversion_path(from_uom, to_uom)
        dec_value = Decimal(str(value)) # make sure its a decimal because floating point math is iffy and imprecise

        self.logger.debug(f"Conversion steps from {from_uom} to {to_uom}:")
        for step_from, step_to, factor in conversion_steps:
            self.logger.debug(f"  {step_from} -> {step_to}  factor: {factor}")
            dec_value *= factor

        # round the final value to the final_result_prevision using ROUND_HALF_UP
        rounded_result = dec_value.quantize(Decimal(f"0.{'0' * final_result_precision}"), rounding=ROUND_HALF_DOWN)

        #print(f"Final result: {rounded_result}  raw value: {dec_value}")
        return rounded_result

    def convert_price(self, value, from_uom, to_uom, final_result_precision=6):
        if from_uom == "IN" and to_uom == "SY":
            return value

        if from_uom == to_uom:
            return value


        if self.item_details is None:
            return None

        conversion_steps = self._find_conversion_path(from_uom, to_uom)
        dec_value = Decimal(str(value))

        self.logger.debug(f"Price conversion from {from_uom} to {to_uom}")
        for step_from, step_to, factor in conversion_steps:
            self.logger.debug(f"  {step_from} -> {step_to} ÷ {factor}")
            dec_value /= factor  # Use division for price

        return dec_value.quantize(Decimal(f"0.{'0' * final_result_precision}"), rounding=ROUND_HALF_UP)