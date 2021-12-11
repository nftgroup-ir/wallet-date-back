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
    transactions = serializers.SerializerMethodField()
    balancedata = serializers.SerializerMethodField()
    nft = serializers.SerializerMethodField()

    class Meta(object):
        model = CSV
        list_serializer_class = BulkListSerializer
        fields = '__all__'


    def get_transactions(self, id):
        number_of_transactions = Transaction.objects.filter(parent=id).distinct()
        x = len(number_of_transactions)
        return x

    def get_balancedata(self, id):
        balanceofdata = BalanceData.objects.filter(parent=id).distinct()
        if len(balanceofdata) == 0:
            balanceofdata = 0
        else:
            balanceofdata = balanceofdata[0]
        return balanceofdata



    def get_nft(self, id):
        number_of_nfts = NFT.objects.filter(parent=id).distinct()
        y = len(number_of_nfts)
        return  y




class LotterySerializer(ModelSerializer):
    class Meta:
        model = Lottery
        fields = '__all__'




class NFTSerializer(ModelSerializer):
    class Meta:
        model = NFT
        fields = '__all__'


class AddressSerializer(BulkSerializerMixin, ModelSerializer):
    class Meta(object):
        model = CSV
        list_serializer_class = BulkListSerializer
        fields = ['address']
