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



# Create your views here.


class listCreate(ListBulkCreateUpdateAPIView):
    queryset = CSV.objects.all()
    serializer_class = CSVserializer





class LotteryListCreate(generics.ListCreateAPIView):
    queryset = Lottery.objects.all()
    serializer_class = LotterySerializer


class TransactionListCreate(generics.ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    # def create(self, request):
    #     print(request.data)
    #     # for value in request.data:
    #     #     new_transaction = Transaction(value)
    #     #     new_transaction.save()
    #     return request.data

class NFTListCreate(generics.ListCreateAPIView):
    queryset = NFT.objects.all()
    serializer_class = NFTSerializer

class BalanceDataListCreate(generics.ListCreateAPIView):
    queryset = BalanceData.objects.all()
    serializer_class = BalanceDataSerializer


def scrape(request):

    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    firefox_binary = FirefoxBinary('/usr/bin/firefox')
    driver = webdriver.Firefox(options=options,firefox_binary=firefox_binary)

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
                print('author :', address)
                print('_' * 100)
            except:
                pass

        driver.find_element_by_class_name('pagination').find_elements_by_tag_name('a')[-2].click()
        print('|' * 100)


class AddressSerializer(ListBulkCreateUpdateAPIView):
    queryset = CSV.objects.all()
    serializer_class = AddressSerializer

def  transactiondetails(request):
    csv = CSV.objects.all()
    for i in csv:
        response = requests.get(f"https://api.covalenthq.com/v1/1/address/{i.address}/transactions_v2/?key=ckey_12d0a9ab40ec40778e2f5f7965c")
        data = response.json()
        print(data)

        for k in data['data']['items']:
            new_transaction = Transaction()
            new_transaction.hash = k['tx_hash']
            new_transaction.from_address = k['from_address']
            new_transaction.to_address = k['to_address']
            new_transaction.value = k['value']
            new_transaction.parent_id = i.id
            new_transaction.gas_price = k['gas_price']
            new_transaction.receipt_gas_used = k['gas_spent']
            new_transaction.save()




