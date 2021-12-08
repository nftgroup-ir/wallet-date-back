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



class listCreate(ListBulkCreateUpdateAPIView):
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

def scrape(requestt):
    driver = webdriver.Firefox(executable_path="C:\FireFoxDriver\geckodriver.exe")
    driver.get('https://etherscan.io/accounts/')
    books = driver.find_elements_by_tag_name('tr')
    count = 0
    while True:
        if count == 2:
            break
        count += 1
        print('page ', count)
        books = driver.find_elements_by_tag_name('tr')

        for book in books:
            try:
                name = book.find_elements_by_tag_name('td')[1]
                try:
                    address = name.find_elements_by_tag_name('a')[0].text
                    csv = CSV(address = address)
                    csv.save()

                except:
                    address = 'Not availbale'
                print('name:', name)
                print('address :', address)
                print('_' * 100)
            except:
                pass

        driver.find_element_by_class_name('pagination').find_elements_by_tag_name('a')[-2].click()
        print('|' * 100)


class AddressSerializer(ListBulkCreateUpdateAPIView):
    queryset = CSV.objects.all()
    serializer_class = AddressSerializer

def transactiondetails(request):
    csv = CSV.objects.all()
    for i in csv:
        response = requests.get(f"https://api.covalenthq.com/v1/1/address/{i.address}/transactions_v2/?key=ckey_12d0a9ab40ec40778e2f5f7965c")
        data = response.json()
        for k in data['data']['items']:
            new_transaction = Transaction()
            new_transaction.from_address = k['from_address']
            new_transaction.hash = k['tx_hash']
            new_transaction.from_address = k['from_address']
            new_transaction.to_address = k['to_address']
            new_transaction.value = k['value']
            new_transaction.parent_id = i.id
            new_transaction.gas_price = k['gas_price']
            new_transaction.receipt_gas_used = k['gas_spent']
            new_transaction.save()
            print(new_transaction)


    
    
    
def  nftDetails(request):
    csv = CSV.objects.all()
    count  = 0
    for i in csv:
        if count == 5:
            break
        count+=1
        response = requests.get(f"https://deep-index.moralis.io/api/v2/{i.address}/nft?chain=eth&format=decimal", headers = {"accept":"application/json", "X-API-Key":"Xv6WsHrCbYI3ebzEuHlaBWXZbdRo0tvpDaI9zH8CbffKzClvWp5nX2BkWuRGUbp2"})
        data = response.json()
        if data['result']:
            for k in data['result']:
                new_nft = NFT()
                new_nft.parent_id = i.id
                new_nft.token_address = k['token_address']
                new_nft.token_id = k['token_id']
                new_nft.block_number_minted = k['block_number_minted']
                new_nft.owner_of = k['owner_of']
                new_nft.block_number = k['block_number']
                new_nft.amount = k['amount']
                new_nft.contract_type = k['contract_type']
                new_nft.name = k['name']
                new_nft.symbol = k['symbol']
                new_nft.token_uri = k['token_uri']
                new_nft.metadata = k['metadata']
                new_nft.synced_at = k['synced_at']
                new_nft.is_valid = k['is_valid']
                new_nft.syncing = k['syncing']
                new_nft.frozen = k['frozen']
                new_nft.save()
        else:
            continue









