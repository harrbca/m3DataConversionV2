
import importlib
import yaml

class TransformerFactory:
    def __init__(self, mapping_file_path):
        with open(mapping_file_path, 'r') as f:
            self.mapping = yaml.safe_load(f)

    def build_transformers(self, class_paths, row):
        instances = []
        for path in class_paths:
            module_path, class_name = path.rsplit('.', 1)
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            instances.append(cls(row))
        return instances

    def transform_row(self, document_type, row):
        doc_def = self.mapping.get(document_type)
        if not doc_def:
            raise ValueError(f"No mapping found for document type: {document_type}")

        transformer_instances = self.build_transformers(doc_def['transformers'], row)
        field_mappings = doc_def['fields']
        result = {}

        for field, method_name in field_mappings.items():
            for transformer in transformer_instances:
                method = getattr(transformer, method_name, None)
                if method:
                    result[field] = method()
                    break
            else:
                raise AttributeError(f"Method {method_name} not found in any transformer for {document_type}")

        return result
