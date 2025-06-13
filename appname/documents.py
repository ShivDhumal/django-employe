from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from .models import employee

@registry.register_document
class EmployeeDocument(Document):
    class Index:
        name = 'employee-index'  # This is your Elasticsearch index name

    class Django:
        model = employee
        fields = [
            'employe_name',
            'employe_add',
            'employe_number',
        ]
