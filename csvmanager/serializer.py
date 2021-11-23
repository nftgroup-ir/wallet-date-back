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
        extra_kwargs = {
            'address': {'validators': []},
        }

class LotterySerializer(ModelSerializer):
    class Meta:
        model = Lottery
        fields = '__all__'


class TransactionSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class NFTSerializer(ModelSerializer):
    class Meta:
        model = NFT
        fields = '__all__'

class BalanceDataSerializer(ModelSerializer):
    class Meta:
        model = BalanceData
        fields = '__all__'