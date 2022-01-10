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




class CSVserializer(ModelSerializer):
    transactions = serializers.SerializerMethodField()
    # tags = serializers.SerializerMethodField()
    # balancedata = serializers.SerializerMethodField()
    nft = serializers.SerializerMethodField()

    class Meta(object):
        model = CSV
        list_serializer_class = BulkListSerializer
        fields = '__all__'


    def get_transactions(self, id):
        number_of_transactions = Transaction.objects.filter(parent=id).distinct()
        x = len(number_of_transactions)
        return x

    # def get_balancedata(self, id):
    #     balanceofdata = BalanceData.objects.filter(parent=id).distinct()
    #     if len(balanceofdata) == 0:
    #         balanceofdata = 0
    #     else:
    #         balanceofdata = balanceofdata[0]
    #     return balanceofdata


    def get_nft(self, id):
        number_of_nfts = NFT.objects.filter(parent=id).distinct()
        y = len(number_of_nfts)
        return  y

    # def get_tags(self , id):
    #     tags = Tags.objects.filter(wallet_tags = id)
    #     return tags

class BalanceDataSerializer(ModelSerializer):
    owner = serializers.SerializerMethodField()

    class Meta:
        model = BalanceData
        fields = '__all__'

    def get_owner(self, id):
        print(id.parent_id)
        owner = CSV.objects.filter(id=id.parent_id)[0].address
        return  owner





class LotterySerializer(ModelSerializer):
    class Meta:
        model = Lottery
        fields = '__all__'




class NFTSerializer(ModelSerializer):
    nft_feature = serializers.SerializerMethodField()

    class Meta:
        model = NFT
        fields = '__all__'

    def get_nft_feature(self, id):
        try:
            print(id.nft_company_id,'avvali')
            x = NftCompany.objects.filter(id=id.nft_company_id).values_list()
            print(x[0][0])
            s = CompanyFeature.objects.filter(nft_company = x[0][0]).values("name")
            return s
        except:
            print('nashod')


class filters(BulkSerializerMixin, ModelSerializer):
    class Meta(object):
        model = CSV
        fields = '__all__'

class CompanyFeatureSerializer(ModelSerializer):
    class Meta:
        model = CompanyFeature
        fields = '__all__'


class NFTCompanySerializer(ModelSerializer):
    features = serializers.SerializerMethodField()
    class Meta:
        model = NftCompany
        fields = '__all__'

    def get_features(self, id):
        feature = CompanyFeature.objects.filter(nft_company=id).values("name")
        if feature == None:
            return ""
        else:
            return  feature
        





