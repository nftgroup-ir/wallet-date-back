from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import *
from rest_framework_bulk import (
    BulkListSerializer,
    BulkSerializerMixin,
)


class TransactionSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

class BalanceDataSerializer(ModelSerializer):
    class Meta:
        model = BalanceData
        fields = '__all__'

        
class CSVserializer(BulkSerializerMixin, ModelSerializer):
    balancedata = serializers.SerializerMethodField()
    transaction = serializers.SerializerMethodField()
    nft = serializers.SerializerMethodField()

    class Meta(object):
        model = CSV
        list_serializer_class = BulkListSerializer
        fields = '__all__'

    def get_balancedata(self, id):
        balanceofdata = BalanceData.objects.filter(parent=id).distinct()
        return BalanceDataSerializer(balanceofdata, many=True).data

    def get_transaction(self, id):
        transactions = Transaction.objects.filter(parent=id).distinct()
        return TransactionSerializer(transactions, many=True).data

    def get_nft(self, id):
        nftofwallet = NFT.objects.filter(parent=id).distinct()
        return  NFTSerializer(nftofwallet, many=True, read_only = True).data




class LotterySerializer(ModelSerializer):
    class Meta:
        model = Lottery
        fields = '__all__'




class NFTSerializer(ModelSerializer):
    class Meta:
        model = NFT
        fields = '__all__'

