from rest_framework.serializers import ModelSerializer
from .models import *
from rest_framework_bulk import (
    BulkListSerializer,
    BulkSerializerMixin,
)



class CSVserializer(BulkSerializerMixin, ModelSerializer):
    class Meta(object):
        model = CSV
        list_serializer_class = BulkListSerializer
        fields = '__all__'


