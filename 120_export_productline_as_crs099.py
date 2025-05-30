from database import Database
from template_helper import TemplateHelper
from plugin_manager import load_transformer
from config_reader import ConfigReader

def main():
    config = ConfigReader.get_instance()
    template_helper = TemplateHelper("API_CRS099MI_AddProductLine.xlsx")
    query_path = config.get('QUERIES', 'crs099_sql_query_path')
    transformer = config.get('TRANSFORMER', 'crs099_transformer')

    # load the SQL query
    with open(query_path, 'r') as file:
        query = file.read()

    # load the transformer (default or custom)
    transformer = load_transformer("crs099", transformer)

    # fetch data from DB
    with Database() as db:
        df = db.fetch_dataframe(query)

    for row in df.itertuples(index=False):
        data = transformer.transform(row)
        if data:
            template_helper.add_row(data)

    template_helper.save('crs099_output_path')

if __name__ == "__main__":
    main()
