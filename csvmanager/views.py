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

    # driver.get('https://etherscan.io/accounts/')

def scrape(request):
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    firefox_binary = FirefoxBinary('/usr/bin/firefox')
    driver = webdriver.Firefox(options=options, firefox_binary=firefox_binary)
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


class AddressSerializer(ListBulkCreateUpdateAPIView):
    queryset = CSV.objects.all()
    serializer_class = AddressSerializer

def transactiondetails(request):
    csv = CSV.objects.all()
    for i in csv:
        response = requests.get(f"https://api.covalenthq.com/v1/1/address/{i.address}/transactions_v2/?key=ckey_12d0a9ab40ec40778e2f5f7965c")
        data = response.json()
        for k in data['data']['items']:

            obj , created = Transaction.objects.update_or_create(
            hash = k['tx_hash'],
            defaults = {
            'from_address' : k['from_address'],'to_address' : k['to_address'], 'value' : k['value'], 'parent_id' : i.id, 'gas_price' : k['gas_price'], 'receipt_gas_used' : k['gas_spent'],

                }
            )






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
        else:
            continue









