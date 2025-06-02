from config_reader import ConfigReader
from database import Database
from template_helper import TemplateHelper
from transformer_factory import TransformerFactory

def main():
    config = ConfigReader.get_instance()
    template_helper = TemplateHelper("API_CRS025MI_AddItemGroup.xlsx")
    query_path = config.get('QUERIES', 'crs025_query')

    # Load the SQL query
    with open(query_path, 'r') as file:
        query = file.read()

    # fetch data from DB
    with Database() as db:
        df = db.fetch_dataframe(query)

    factory = TransformerFactory("config/document_mappings.yml")

    #loop through the rows of the DataFrame
    for row in df.itertuples(index=False):
        result = factory.transform_row("API_CRS025MI_AddItemGroup", row)

        # Add the transformed data to the template
        if result:
            template_helper.add_row(result)

    # Save the template with the transformed data
    template_helper.save('crs025_output_path')


if __name__ == "__main__":
    main()