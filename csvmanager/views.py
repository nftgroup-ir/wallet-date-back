from django.shortcuts import render
from rest_framework import generics 
from .models import *
from .serializer import *
from rest_framework_bulk import (ListBulkCreateUpdateDestroyAPIView,BulkUpdateModelMixin,ListBulkCreateUpdateAPIView)
from django.db.utils import DatabaseError,IntegrityError
from django.db import transaction
import requests
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
import time






class listCreate(generics.ListCreateAPIView):
    queryset = CSV.objects.all()
    serializer_class = CSVserializer






class LotteryListCreate(generics.ListCreateAPIView):
    queryset = Lottery.objects.all()
    serializer_class = LotterySerializer


class TransactionListCreate(generics.ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filterset_fields = ['parent']


class NFTListCreate(generics.ListCreateAPIView):
    queryset = NFT.objects.all()
    serializer_class = NFTSerializer
    filterset_fields = ['parent']

class BalanceDataListCreate(generics.ListCreateAPIView):
    queryset = BalanceData.objects.all()
    serializer_class = BalanceDataSerializer
    filterset_fields = ['parent']

    #

def scrape(request):
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    # firefox_binary = FirefoxBinary('/usr/bin/firefox')
    # driver = webdriver.Firefox(options=options, firefox_binary=firefox_binary)
    driver = webdriver.Firefox(executable_path="C:\FireFoxDriver\geckodriver.exe")
    driver.get('https://etherscan.io/accounts/')
    all_addresses = driver.find_elements_by_tag_name('tr')
    count = 0
    while True:
        if count == 2:
            break
        count += 1
        print('page ', count)
        all_addresses = driver.find_elements_by_tag_name('tr')

        for one_address in all_addresses:
            try:
                name = one_address.find_elements_by_tag_name('td')[1]
                try:
                    address = name.find_elements_by_tag_name('a')[0].text
                    csv , created = CSV.objects.update_or_create(address = address)

                except:
                    address = 'Not availbale'
                print('_' * 100)
            except:
                pass

        driver.find_element_by_class_name('pagination').find_elements_by_tag_name('a')[-2].click()
        print('|' * 100)



def transactiondetails(request):
    csv = CSV.objects.all()
    for i in csv:
        response = requests.get(f"https://api.covalenthq.com/v1/1/address/{i.address}/transactions_v2/?key=ckey_12d0a9ab40ec40778e2f5f7965c")
        print(response.status_code)
        if response.status_code != 400:

            data = response.json()
            print(len(data['data']['items']))
            for k in data['data']['items']:

                obj , created = Transaction.objects.update_or_create(
                hash = k['tx_hash'],
                defaults = {
                'from_address' : k['from_address'],'to_address' : k['to_address'], 'value' : k['value'], 'parent_id' : i.id, 'gas_price' : k['gas_price'], 'receipt_gas_used' : k['gas_spent'],

                    }
                )
            i.total_Txs = len(data['data']['items'])
            i.save()


def balanceDetails(request):
    csv = CSV.objects.all()
    for i in csv:
        balances = BalanceData.objects.all().filter(parent_id=i.id).values('contract_address')
        print(balances)
        response = requests.get(
            f"https://api.covalenthq.com/v1/1/address/{i.address}/balances_v2/?key=ckey_12d0a9ab40ec40778e2f5f7965c")
        if response.status_code != 400:
            data = response.json()
            for k in data['data']['items']:
                new_balance, created = BalanceData.objects.update_or_create(contract_address=k["contract_address"],
                                          defaults={
                                              "parent_id": i.id,
                                              "contract_decimals": k['contract_decimals'],
                                              "contract_name": k['contract_name'],
                                              "contract_ticker_symbol": k['contract_ticker_symbol'],
                                              "contract_address": k['contract_address'],
                                              "logo_url": k['logo_url'],
                                              "last_transferred_at": k['last_transferred_at'],
                                              "type": k['type'],
                                              "balance": k['balance'],
                                              "balance_24h": k['balance_24h'],
                                              "quote_rate": k['quote_rate'],
                                              "quote_rate_24h": k['quote_rate_24h'],
                                              "quote": k['quote'],
                                              "quote_24h": k['quote_24h'],
                                          })











def  nftDetails(request):
    csv = CSV.objects.all()
    count  = 0
    print(csv)
    for i in csv:
        print("address:",i)
        response = requests.get(f"https://deep-index.moralis.io/api/v2/{i.address}/nft?chain=eth&format=decimal", headers = {"accept":"application/json", "X-API-Key":"Xv6WsHrCbYI3ebzEuHlaBWXZbdRo0tvpDaI9zH8CbffKzClvWp5nX2BkWuRGUbp2"})
        data = response.json()
        print(response)
        print(data['total'])


        if data['total']:
            i.total_nfts = data['total']
        else:
            i.total_nfts = 0
        i.save()
        if data['result']:
            for k in data['result']:
                token_address = k['token_address']
                token_id = k['token_id']
                field_unique_process = ""
                field_unique_process = token_address + token_id
                new_nft , created = NFT.objects.update_or_create(field_unique = field_unique_process,
                defaults = { "parent_id" : i.id , "token_address" : k['token_address'] ,
                             "token_id" : k['token_id'] ,
                             "block_number_minted" : k['block_number_minted'] ,
                             "owner_of" : k['owner_of'],
                             "block_number" : k['block_number'],
                             "amount" : k['amount'],
                             "contract_type" :  k['contract_type'],
                             "name" : k['name'],
                             "symbol" : k['symbol'],
                             "token_uri" : k['token_uri'],
                             "metadata" : k['metadata'],
                             "synced_at" : k['synced_at'],
                             "is_valid" : k['is_valid'],
                             "syncing" : k['syncing'],
                             "frozen" :  k['frozen'],
                             "field_unique" : field_unique_process })





class filters(generics.ListAPIView):
    queryset = CSV.objects.all()
    serializer_class = CSVserializer

    def get_queryset(self,*args, **kwargs  ):
        queryset=CSV.objects.all()
        #NFT
        if self.request.GET['NFTCount'] != "":
            if self.request.GET['NFTOperator'] == 'gt':
                queryset = queryset.filter(total_nfts__gt=self.request.GET['NFTCount'])
            elif self.request.GET['NFTOperator'] == 'lt':
                queryset = queryset.filter(total_nfts__lt=self.request.GET['NFTCount'])
            elif self.request.GET['NFTOperator'] == 'eq':
                queryset = queryset.filter(total_nfts=self.request.GET['NFTCount'])

        #Tx
        if self.request.GET['TxCount'] != "":
            if self.request.GET['TxOperator'] == 'gt':
                queryset = queryset.filter(total_Txs__gt=self.request.GET['TxCount'])
            elif self.request.GET['TxOperator'] == 'lt':
                queryset = queryset.filter(total_Txs__lt=self.request.GET['TxCount'])
            elif self.request.GET['TxOperator'] == 'eq':
                queryset = queryset.filter(total_Txs=self.request.GET['TxCount'])


        #Balance
        if self.request.GET['BalanceValue'] != "":
            if self.request.GET['BalanceOperator'] == 'gt':
                queryset = queryset.filter(balancedata__gt=self.request.GET['BalanceValue'])
            elif self.request.GET['BalanceOperator'] == 'lt':
                queryset = queryset.filter(balancedata__lt=self.request.GET['BalanceValue'])
            elif self.request.GET['BalanceOperator'] == 'eq':
                queryset = queryset.filter(balancedata=self.request.GET['BalanceValue'])





        if self.request.GET['BalanceSortBy'] != 'none':
            if self.request.GET['BalanceSortBy']=="ASC":
                queryset = queryset.order_by('balancedata')
            elif self.request.GET['BalanceSortBy']=="DESC":
                queryset = queryset.order_by('-balancedata')

        if self.request.GET['NFTSortBy'] != 'none':
            if self.request.GET['NFTSortBy']=="ASC":
                queryset = queryset.order_by('total_nfts')
            elif self.request.GET['NFTSortBy']=="DESC":
                queryset = queryset.order_by('-total_nfts')

        if self.request.GET['TxSortBy'] != 'none':
            if self.request.GET['TxSortBy']=="ASC":
                queryset = queryset.order_by('total_Txs')
            elif self.request.GET['TxSortBy']=="DESC":
                queryset = queryset.order_by('-total_Txs')

        return queryset














