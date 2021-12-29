from typing import Counter
from django.db.models.fields import DecimalField
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
from django.db import OperationalError
from django.http import JsonResponse
from web3 import Web3
import sys
import json 
import threading
from selenium.webdriver.common.by import By
import time
import math
from decimal import *

infura = 'https://mainnet.infura.io/v3/5e5b7b87ad6a4a899bd80becd958b765'

def removeUnicodeCharacters(data):
    if data != None:
        data = data.encode('ascii', 'ignore').decode("utf-8")
    else: data = ""
    return 
def TxCovaltGetter(walletAddress,walletID):
    try:
        i = CSV.objects.filter(id=walletID)[0]
        response = requests.get(f"https://api.covalenthq.com/v1/1/address/{walletAddress}/transactions_v2/?key=ckey_12d0a9ab40ec40778e2f5f7965c")
        if response.status_code == 200:
            data = response.json()
            for k in data['data']['items']:
                obj , created = Transaction.objects.update_or_create(
                hash = k['tx_hash'],
                defaults = {
                    'from_address' : k['from_address'],
                        'to_address' : k['to_address'],
                        'value' : k['value'],
                        'parent_id' : walletID,
                        'gas_price' : k['gas_price'],
                        'receipt_gas_used' : k['gas_spent'],

                        }
                    )
            print(len(data['data']['items']),' TXs udated or created for ',walletAddress,)
            i.total_Txs = len(data['data']['items'])
            i.save()
        else: 
            print('transactions error for ',walletAddress , 'error code: ',response.status_code)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        return False


def balanceCovaltGetter(walletAddress,walletID):
    try:
        response = requests.get(
        f"https://api.covalenthq.com/v1/1/address/{walletAddress}/balances_v2/?key=ckey_12d0a9ab40ec40778e2f5f7965c")
        Counter=0
        if response.status_code == 200:
            data = response.json()
            isMAx=False
            for k in data['data']['items']:
                print(Counter)
                Counter+=1
                print(k['contract_decimals'],'==============')
                if k['contract_decimals'] !=0:
                    balance= Decimal(int(k['balance'])/(10**int(k['contract_decimals']))) 
                    if math.trunc(balance)>10**47:
                        isMAx=True
                        balance = 9999999999999999999999999999999999999999999999
                else: 
                    balance = k['balance']
                
                print(walletAddress,k['balance'],balance) 
                new_balance, created = BalanceData.objects.update_or_create(contract_address=k["contract_address"],
                                        defaults={
                                                    "parent_id": walletID,
                                                    "contract_decimals": k['contract_decimals'],
                                                    "contract_name":removeUnicodeCharacters(k['contract_name']),
                                                    "contract_ticker_symbol": removeUnicodeCharacters(k['contract_ticker_symbol']),
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
                                                    "int_balance":balance,
                                                    "max_balance": isMAx,
                                                })
            print(len(data['data']['items']),' Balances udated or created for ',walletAddress,)
            return True

        else: 
            print('balances error for ',walletAddress , 'error code: ',response.status_code)
            return False


    except :
        print("Unexpected error:", sys.exc_info()[0])
        return False

def NftMoralisGetter(walletAddress,walletID):
    try:
        response = requests.get(f"https://deep-index.moralis.io/api/v2/{walletAddress}/nft?chain=eth&format=decimal", headers = {"accept":"application/json", "X-API-Key":"Xv6WsHrCbYI3ebzEuHlaBWXZbdRo0tvpDaI9zH8CbffKzClvWp5nX2BkWuRGUbp2"})
        print(response.status_code)
        if response.status_code == 200:  
            data = response.json()
            i = CSV.objects.filter(id=walletID)[0]
            if data['total']:
                i.total_nfts = data['total']
                totalNFT =data['total']
            else:
                i.total_nfts = 0
                totalNFT=0
            i.save()
            if data['result']:
                for k in data['result']:
                    token_address = k['token_address']
                    token_id = k['token_id']
                    field_unique_process = ""
                    field_unique_process = token_address + token_id
                    new_nft , created = NFT.objects.update_or_create(field_unique = field_unique_process,
                    defaults = { "parent_id" : walletID ,
                                    "token_address" : k['token_address'] ,
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
            print(totalNFT,' NFTs udated or created for ',walletAddress,)
            return True
        else: 
            print('balances error for ',walletAddress , 'error code: ',response.status_code)
            return False

    except :
        print("Unexpected error:", sys.exc_info()[0])
        return False

def tokenBalanceWeb3Getter(walletAddress,tokenContractAddress):
    ABI = json.loads('[{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"}]')
    w3 = Web3(Web3.HTTPProvider(infura))
    wallet_address = Web3.toChecksumAddress(walletAddress)
    token_contract_address = Web3.toChecksumAddress(tokenContractAddress)
    # define contract
    contract = w3.eth.contract(token_contract_address, abi=ABI)

    # call contract and get data from balanceOf for argument wallet_address
    raw_balance = contract.functions.balanceOf(wallet_address).call()

    return raw_balance

def startTxCovaltGetter(walletAddress,walletID):
    t = threading.Thread(target=TxCovaltGetter,args=[walletAddress,walletID])
    t.setDaemon(True)
    t.start()

def getWalletDate(request):
    walletID = CSV.objects.filter(address=request.GET['wallet'])[0].id
    walletAddress = request.GET['wallet']

    if not 'Tx' in request.GET:
        txResult= startTxCovaltGetter(walletAddress,walletID)
    elif  request.GET['Tx'] != 'false' :
        txResult= startTxCovaltGetter(walletAddress,walletID)
    else: txResult ="canceled"

    if not 'balance' in request.GET:
        balanceResult= balanceCovaltGetter(walletAddress,walletID)
    elif  request.GET['balance'] != 'false' :
        balanceResult= balanceCovaltGetter(walletAddress,walletID)
    else: balanceResult ="canceled"
    

    if not 'NFT' in request.GET:
        NFTResult= NftMoralisGetter(walletAddress,walletID)
    elif request.GET['NFT'] != 'false' :
        NFTResult= NftMoralisGetter(walletAddress,walletID)
    else: NFTResult = "canceled"

    if not isinstance(txResult, str) :
        if txResult: txResult = "success"
        else: txResult= "error"
    if not isinstance(NFTResult, str) :   
        if NFTResult: NFTResult = "success"
        else: NFTResult= "error"

    if not isinstance(balanceResult, str) :   
        if balanceResult: balanceResult = "success"
        else: balanceResult= "error"


    responseData = {
        'result': 'transactions:'+txResult+' and NFTs Update:'+NFTResult+' and Balance:'+balanceResult+' for '+ walletAddress,
    } 



    return JsonResponse(responseData)

        
def getWalletDataByToken(request):
    address = request.GET['address']
    tokenAddress = request.GET['token']
    print(address,tokenAddress)
    balance = tokenBalanceWeb3Getter(address,tokenAddress)
    responseData = {
        'result': address+ ' balance for '+tokenAddress+' coin : ' +str(balance),
    } 
    return JsonResponse(responseData)


class listCreate(generics.ListCreateAPIView):
    queryset = CSV.objects.all()
    serializer_class = CSVserializer






class LotteryListCreate(generics.ListCreateAPIView):
    queryset = Lottery.objects.all()
    serializer_class = LotterySerializer


class TransactionListCreate(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def get_queryset(self,*args, **kwargs):

        queryset=Transaction.objects.all()

        #amount
        if self.request.GET['HashValue'] != "":
            queryset = queryset.filter(hash=self.request.GET['HashValue'])
        if self.request.GET['TxIndexValue'] != "":
            queryset = queryset.filter(transaction_index=self.request.GET['TxIndexValue'])


        if self.request.GET['FromValue'] != "":
            queryset = queryset.filter(from_address=self.request.GET['FromValue'])
        if self.request.GET['ToValue'] != "":
            queryset = queryset.filter(to_address=self.request.GET['ToValue'])

        if self.request.GET['InputValue'] != "":
            queryset = queryset.filter(input=self.request.GET['InputValue'])

        if self.request.GET['RCUValue'] != "":
            queryset = queryset.filter(receipt_contract_address=self.request.GET['RCUValue'])
        if self.request.GET['RRValue'] != "":
            queryset = queryset.filter(receipt_root=self.request.GET['RRValue'])
        if self.request.GET['RSValue'] != "":
            queryset = queryset.filter(receipt_status=self.request.GET['RSValue'])
        if self.request.GET['TimeValue'] != "":
            queryset = queryset.filter(block_timestamp=self.request.GET['TimeValue'])
        if self.request.GET['BlockNumberValue'] != "":
            queryset = queryset.filter(block_number=self.request.GET['BlockNumberValue'])
        if self.request.GET['BlockHashValue'] != "":
            queryset = queryset.filter(block_hash=self.request.GET['BlockHashValue'])

        #sort
        if self.request.GET['NonceSortBy'] != 'none':
            if self.request.GET['NonceSortBy']=="ASC":
                queryset = queryset.order_by('nonc')
            elif self.request.GET['NonceSortBy']=="DESC":
                queryset = queryset.order_by('-nonc')

        if self.request.GET['ValueSortBy'] != 'none':
            if self.request.GET['ValueSortBy']=="ASC":
                queryset = queryset.order_by('value')
            elif self.request.GET['ValueSortBy']=="DESC":
                queryset = queryset.order_by('-value')

        if self.request.GET['GasSortBy'] != 'none':
            if self.request.GET['GasSortBy']=="ASC":
                queryset = queryset.order_by('gas')
            elif self.request.GET['GasSortBy']=="DESC":
                queryset = queryset.order_by('-gas')

        if self.request.GET['GasPriceSortBy'] != 'none':
            if self.request.GET['GasPriceSortBy']=="ASC":
                queryset = queryset.order_by('gas_price')
            elif self.request.GET['GasPriceSortBy']=="DESC":
                queryset = queryset.order_by('-gas_price')

        if self.request.GET['RCGUSortBy'] != 'none':
            if self.request.GET['RCGUSortBy']=="ASC":
                queryset = queryset.order_by('receipt_cumulative_gas_used')
            elif self.request.GET['RCGUSortBy']=="DESC":
                queryset = queryset.order_by('-receipt_cumulative_gas_used')

        if self.request.GET['RGUSortBy'] != 'none':
            if self.request.GET['RGUSortBy']=="ASC":
                queryset = queryset.order_by('receipt_gas_used')
            elif self.request.GET['RGUSortBy']=="DESC":
                queryset = queryset.order_by('-receipt_gas_used')


        #Operators
        if self.request.GET['NonceOperator'] != "":
            if self.request.GET['NonceOperator'] == 'gt':
                queryset = queryset.filter(nonc__gt=self.request.GET['NonceValue'])
            elif self.request.GET['NonceOperator'] == 'lt':
                queryset = queryset.filter(nonc__lt=self.request.GET['NonceValue'])
            elif self.request.GET['NonceOperator'] == 'eq':
                queryset = queryset.filter(nonc=self.request.GET['TokenIdValue'])



        if self.request.GET['ValueOperator'] != "":
            if self.request.GET['ValueOperator'] == 'gt':
                queryset = queryset.filter(value__gt=self.request.GET['ValueValue'])
            elif self.request.GET['ValueOperator'] == 'lt':
                queryset = queryset.filter(value__lt=self.request.GET['ValueValue'])
            elif self.request.GET['ValueOperator'] == 'eq':
                queryset = queryset.filter(value=self.request.GET['ValueValue'])



        if self.request.GET['GasOperator'] != "":
            if self.request.GET['GasOperator'] == 'gt':
                queryset = queryset.filter(gas__gt=self.request.GET['GasValue'])
            elif self.request.GET['GasOperator'] == 'lt':
                queryset = queryset.filter(gas__lt=self.request.GET['GasValue'])
            elif self.request.GET['GasOperator'] == 'eq':
                queryset = queryset.filter(gas=self.request.GET['GasValue'])

        if self.request.GET['GasPriceOperator'] != "":
            if self.request.GET['GasPriceOperator'] == 'gt':
                queryset = queryset.filter(gas_price__gt=self.request.GET['GasPriceValue'])
            elif self.request.GET['GasPriceOperator'] == 'lt':
                queryset = queryset.filter(gas_price__lt=self.request.GET['GasPriceValue'])
            elif self.request.GET['GasPriceOperator'] == 'eq':
                queryset = queryset.filter(gas_price=self.request.GET['GasPriceValue'])



        if self.request.GET['RCGUOperator'] != "":
            if self.request.GET['RCGUOperator'] == 'gt':
                queryset = queryset.filter(receipt_cumulative_gas_used__gt=self.request.GET['RCGUValue'])
            elif self.request.GET['RCGUOperator'] == 'lt':
                queryset = queryset.filter(receipt_cumulative_gas_used__lt=self.request.GET['RCGUValue'])
            elif self.request.GET['RCGUOperator'] == 'eq':
                queryset = queryset.filter(receipt_cumulative_gas_used=self.request.GET['RCGUValue'])



        if self.request.GET['RGUOperator'] != "":
            if self.request.GET['RGUOperator'] == 'gt':
                queryset = queryset.filter(gas__gt=self.request.GET['RGUValue'])
            elif self.request.GET['RGUOperator'] == 'lt':
                queryset = queryset.filter(gas__lt=self.request.GET['RGUValue'])
            elif self.request.GET['RGUOperator'] == 'eq':
                queryset = queryset.filter(gas=self.request.GET['RGUValue'])

        return  queryset.distinct()




class NFTListCreate(generics.ListCreateAPIView):
    queryset = NFT.objects.all()
    serializer_class = NFTSerializer

    def get_queryset(self,*args, **kwargs):

        queryset=NFT.objects.all()

        #amount
        if self.request.GET['NameValue'] != "":
            queryset = queryset.filter(name=self.request.GET['NameValue'])

        if self.request.GET['AmountValue'] != "":
            if self.request.GET['AmountOperator'] == 'gt':
                queryset = queryset.filter(amount__gt=self.request.GET['AmountValue'])
            elif self.request.GET['AmountOperator'] == 'lt':
                queryset = queryset.filter(amount__lt=self.request.GET['AmountValue'])
            elif self.request.GET['AmountOperator'] == 'eq':
                queryset = queryset.filter(amount=self.request.GET['AmountValue'])

        if self.request.GET['FrozenValue'] != "":
            queryset = queryset.filter(frozen=self.request.GET['FrozenValue'])

        if self.request.GET['SymbolValue'] != "":
            queryset = queryset.filter(symbol=self.request.GET['SymbolValue'])

        if self.request.GET['SyncingValue'] != "":
            queryset = queryset.filter(syncing=self.request.GET['SyncingValue']).distinct()
        if self.request.GET['IsValidValue'] != "":
            queryset = queryset.filter(is_valid=self.request.GET['IsValidValue'])
        if self.request.GET['MetadataValue'] != "":
            queryset = queryset.filter(metadata=self.request.GET['MetadataValue'])

        if self.request.GET['TokenUriValue'] != "":
            queryset = queryset.filter(token_uri=self.request.GET['TokenUriValue'])
        if self.request.GET['BlockNumberValue'] != "":
            queryset = queryset.filter(block_number=self.request.GET['BlockNumberValue'])

        if self.request.GET['ContractTypeValue'] != "":
            queryset = queryset.filter(contract_type=self.request.GET['ContractTypeValue'])
        if self.request.GET['TokenAddressValue'] != "":
            queryset = queryset.filter(token_address=self.request.GET['TokenAddressValue'])
        if self.request.GET['BlockNumberMintedValue'] != "":
            queryset = queryset.filter(block_number_minted=self.request.GET['BlockNumberMintedValue'])
        if self.request.GET['OwnerOfValue'] != "":
            queryset = queryset.filter(owner_of=self.request.GET['OwnerOfValue'])



        #sort
        if self.request.GET['TokenIdSortBy'] != 'none':
            if self.request.GET['TokenIdSortBy']=="ASC":
                queryset = queryset.order_by('token_id')
            elif self.request.GET['TokenIdSortBy']=="DESC":
                queryset = queryset.order_by('-token_id')

        if self.request.GET['BlockNumberMintedSortBy'] != 'none':
            if self.request.GET['BlockNumberMintedSortBy']=="ASC":
                queryset = queryset.order_by('block_number_minted')
            elif self.request.GET['BlockNumberMintedSortBy']=="DESC":
                queryset = queryset.order_by('-block_number_minted')

        if self.request.GET['AmountSortBy'] != 'none':
            if self.request.GET['AmountSortBy']=="ASC":
                queryset = queryset.order_by('amount')
            elif self.request.GET['AmountSortBy']=="DESC":
                queryset = queryset.order_by('-amount')

        if self.request.GET['IsValidSortBy'] != 'none':
            if self.request.GET['IsValidSortBy']=="ASC":
                queryset = queryset.order_by('is_valid')
            elif self.request.GET['IsValidSortBy']=="DESC":
                queryset = queryset.order_by('-is_valid')

        if self.request.GET['SyncingSortBy'] != 'none':
            if self.request.GET['SyncingSortBy']=="ASC":
                queryset = queryset.order_by('syncing')
            elif self.request.GET['SyncingSortBy']=="DESC":
                queryset = queryset.order_by('-syncing')

        if self.request.GET['FrozenSortBy'] != 'none':
            if self.request.GET['FrozenSortBy']=="ASC":
                queryset = queryset.order_by('frozen')
            elif self.request.GET['FrozenSortBy']=="DESC":
                queryset = queryset.order_by('-frozen')

        if self.request.GET['BlockNumberSortBy'] != 'none':
            if self.request.GET['BlockNumberSortBy']=="ASC":
                queryset = queryset.order_by('block_number')
            elif self.request.GET['BlockNumberSortBy']=="DESC":
                queryset = queryset.order_by('-block_number')


        #Operators
        if self.request.GET['TokenIdOperator'] != "":
            if self.request.GET['TokenIdOperator'] == 'gt':
                queryset = queryset.filter(token_id__gt=self.request.GET['TokenIdValue'])
            elif self.request.GET['TokenIdOperator'] == 'lt':
                queryset = queryset.filter(token_id__lt=self.request.GET['TokenIdValue'])
            elif self.request.GET['TokenIdOperator'] == 'eq':
                queryset = queryset.filter(token_id=self.request.GET['TokenIdValue'])



        if self.request.GET['BlockNumberMintedOperator'] != "":
            if self.request.GET['BlockNumberMintedOperator'] == 'gt':
                queryset = queryset.filter(block_number_minted__gt=self.request.GET['BlockNumberMintedValue'])
            elif self.request.GET['BlockNumberMintedOperator'] == 'lt':
                queryset = queryset.filter(block_number_minted__lt=self.request.GET['BlockNumberMintedValue'])
            elif self.request.GET['BlockNumberMintedOperator'] == 'eq':
                queryset = queryset.filter(block_number_minted=self.request.GET['BlockNumberMintedValue'])

        return queryset.distinct()




class BalanceDataListCreate(generics.ListCreateAPIView):
    queryset = BalanceData.objects.all()
    serializer_class = BalanceDataSerializer

    def get_queryset(self, *args, **kwargs):

        queryset = BalanceData.objects.all()

        # amount

        if self.request.GET['AddressValue'] != "":
            # csv = csv.get(address = self.request.GET['AddressValue'])
            csvID = CSV.objects.filter(address = self.request.GET['AddressValue'])[0].id
            queryset = queryset.filter(parent_id = csvID)
            

        if self.request.GET['ContractDecimalValue'] != "":
            queryset = queryset.filter(contract_decimals=self.request.GET['ContractDecimalValue']).distinct()
        if self.request.GET['ContractNameValue'] != "":
            queryset = queryset.filter(contract_name=self.request.GET['ContractNameValue'])
        if self.request.GET['ContractTickerSymbolValue'] != "":
            queryset = queryset.filter(contract_ticker_symbol=self.request.GET['ContractTickerSymbolValue'])

        if self.request.GET['ContractAddressValue'] != "":
            queryset = queryset.filter(contract_address=self.request.GET['ContractAddressValue'])
        if self.request.GET['LastTransferredAtValue'] != "":
            queryset = queryset.filter(last_transferred_at=self.request.GET['LastTransferredAtValue'])
        if self.request.GET['TypeValue'] != "":
            queryset = queryset.filter(type=self.request.GET['TypeValue'])


        # sort
        if self.request.GET['ContractDecimalSortBy'] != 'none':
            if self.request.GET['ContractDecimalSortBy'] == "ASC":
                queryset = queryset.order_by('contract_decimals')
            elif self.request.GET['ContractDecimalSortBy'] == "DESC":
                queryset = queryset.order_by('-contract_decimals')

        if self.request.GET['BalanceSortBy'] != 'none':
            if self.request.GET['BalanceSortBy'] == "ASC":
                queryset = queryset.order_by('int_balance')
            elif self.request.GET['BalanceSortBy'] == "DESC":
                queryset = queryset.order_by('-int_balance')

        if self.request.GET['Balance24hSortBy'] != 'none':
            if self.request.GET['Balance24hSortBy'] == "ASC":
                queryset = queryset.order_by('balance_24h')
            elif self.request.GET['Balance24hSortBy'] == "DESC":
                queryset = queryset.order_by('-balance_24h')

        if self.request.GET['QuoteRateSortBy'] != 'none':
            if self.request.GET['QuoteRateSortBy'] == "ASC":
                queryset = queryset.order_by('quote_rate')
            elif self.request.GET['QuoteRateSortBy'] == "DESC":
                queryset = queryset.order_by('-quote_rate')

        if self.request.GET['QuoteRate24hSortBy'] != 'none':
            if self.request.GET['QuoteRate24hSortBy'] == "ASC":
                queryset = queryset.order_by('quote_rate_24h')
            elif self.request.GET['QuoteRate24hSortBy'] == "DESC":
                queryset = queryset.order_by('-quote_rate_24h')

        if self.request.GET['QuoteSortBy'] != 'none':
            if self.request.GET['QuoteSortBy'] == "ASC":
                queryset = queryset.order_by('quote')
            elif self.request.GET['QuoteSortBy'] == "DESC":
                queryset = queryset.order_by('-quote')

        if self.request.GET['Quote24hSortBy'] != 'none':
            if self.request.GET['Quote24hSortBy'] == "ASC":
                queryset = queryset.order_by('quote_24h')
            elif self.request.GET['Quote24hSortBy'] == "DESC":
                queryset = queryset.order_by('-quote_24h')

        # Operators
        if self.request.GET['BalanceOperator'] != "":
            if self.request.GET['BalanceOperator'] == 'gt':
                queryset = queryset.filter(int_balance__gt=self.request.GET['BalanceValue'])
            elif self.request.GET['BalanceOperator'] == 'lt':
                queryset = queryset.filter(int_balance__lt=self.request.GET['BalanceValue'])
            elif self.request.GET['BalanceOperator'] == 'eq':
                queryset = queryset.filter(int_balance=self.request.GET['BalanceValue'])

        if self.request.GET['Balance24hOperator'] != "":
            if self.request.GET['Balance24hOperator'] == 'gt':
                queryset = queryset.filter(balance_24h__gt=self.request.GET['Balance24hValue'])
            elif self.request.GET['Balance24hOperator'] == 'lt':
                queryset = queryset.filter(balance_24h__lt=self.request.GET['Balance24hValue'])
            elif self.request.GET['Balance24hOperator'] == 'eq':
                queryset = queryset.filter(balance_24h=self.request.GET['Balance24hValue'])


        if self.request.GET['QuoteRateOperator'] != "":
            if self.request.GET['QuoteRateOperator'] == 'gt':
                queryset = queryset.filter(quote_rate__gt=self.request.GET['QuoteRateValue'])
            elif self.request.GET['QuoteRateOperator'] == 'lt':
                queryset = queryset.filter(quote_rate__lt=self.request.GET['QuoteRateValue'])
            elif self.request.GET['QuoteRateOperator'] == 'eq':
                queryset = queryset.filter(quote_rate=self.request.GET['QuoteRateValue'])

        if self.request.GET['QuoteRate24hOperator'] != "":
            if self.request.GET['QuoteRate24hOperator'] == 'gt':
                queryset = queryset.filter(quote_rate_24h__gt=self.request.GET['QuoteRate24hValue'])
            elif self.request.GET['QuoteRate24hOperator'] == 'lt':
                queryset = queryset.filter(quote_rate_24h__lt=self.request.GET['QuoteRate24hValue'])
            elif self.request.GET['QuoteRate24hOperator'] == 'eq':
                queryset = queryset.filter(quote_rate_24h=self.request.GET['QuoteRate24hValue'])

        if self.request.GET['QuoteOperator'] != "":
            if self.request.GET['QuoteOperator'] == 'gt':
                queryset = queryset.filter(quote__gt=self.request.GET['QuoteValue'])
            elif self.request.GET['QuoteOperator'] == 'lt':
                queryset = queryset.filter(quote__lt=self.request.GET['QuoteValue'])
            elif self.request.GET['QuoteOperator'] == 'eq':
                queryset = queryset.filter(quote=self.request.GET['QuoteValue'])

        if self.request.GET['Quote24hOperator'] != "":
            if self.request.GET['Quote24hOperator'] == 'gt':
                queryset = queryset.filter(quote_24h__gt=self.request.GET['Quote24hValue'])
            elif self.request.GET['Quote24hOperator'] == 'lt':
                queryset = queryset.filter(quote_24h__lt=self.request.GET['Quote24hValue'])
            elif self.request.GET['Quote24hOperator'] == 'eq':
                queryset = queryset.filter(quote_24h=self.request.GET['Quote24hValue'])

        if self.request.GET['QuoteOperator'] != "":
            if self.request.GET['QuoteOperator'] == 'gt':
                queryset = queryset.filter(quote__gt=self.request.GET['QuoteValue'])
            elif self.request.GET['QuoteOperator'] == 'lt':
                queryset = queryset.filter(quote__lt=self.request.GET['QuoteValue'])
            elif self.request.GET['QuoteOperator'] == 'eq':
                queryset = queryset.filter(quote=self.request.GET['QuoteValue'])



        return queryset.distinct()

    #

def scrape(request):
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    firefox_binary = FirefoxBinary('/usr/bin/firefox')
    driver = webdriver.Firefox(options=options, firefox_binary=firefox_binary)
    # driver = webdriver.Firefox(executable_path="C:\FireFoxDriver\geckodriver.exe")
    driver.get('https://etherscan.io/accounts/')
    all_addresses = driver.find_elements_by_tag_name('tr')
    while True:
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
        startTxCovaltGetter(i.address,i.id)
    responseData = {
        'result': 'Transactions Updated',
    } 
    return JsonResponse(responseData)


def balanceDetails(request):
    csv = CSV.objects.all()
    for i in csv:
        balanceCovaltGetter(i.address,i.id)
    responseData = {
        'result': 'balances Updated',
    } 
    return JsonResponse(responseData)

        

                

def  nftDetails(request):
    csv = CSV.objects.all()
    for i in csv:
        NftMoralisGetter(i.address,i.id)
    responseData = {
        'result': 'NFTs Updated',
    } 
    return JsonResponse(responseData)






class filters(generics.ListAPIView):
    queryset = CSV.objects.all()
    serializer_class = CSVserializer

    def get_queryset(self,*args, **kwargs  ):
        queryset=CSV.objects.all()

        if 'special' in self.request.GET:
            if self.request.GET['special'] =='false':
                queryset = queryset.filter(special=False)
            elif self.request.GET['special'] =='true':
                queryset = queryset.filter(special=True)

        #CSV
        if 'AddressInput' in self.request.GET:
            if self.request.GET['AddressInput'] != "":
                queryset = queryset.filter(address=self.request.GET['AddressInput'])

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

        return queryset.distinct()

def blockchainScraper(request):
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    firefox_binary = FirefoxBinary('/usr/bin/firefox')
    driver = webdriver.Firefox(options=options, firefox_binary=firefox_binary)
    driver.get('https://www.blockchain.com/eth/unconfirmed-transactions')
    while True:
        try:
            for i in range(10,0,-1):
                if i != 1:
                    time.sleep(0.5)
                    driver.find_elements(By.CLASS_NAME, 'hXyplo')[i].find_element(By.CSS_SELECTOR, 'a').click()
                    time.sleep(0.5)
                    address_1 = driver.find_elements(By.CSS_SELECTOR, 'a')[31].text
                    object_1, created = CSV.objects.update_or_create(address = address_1)
                    address_2 = driver.find_elements(By.CSS_SELECTOR, 'a')[32].text
                    object_2, created = CSV.objects.update_or_create(address=address_2)
                    driver.back()
                    print(address_1, address_2)
                elif i == 1:
                    i = 50
        except:
            continue







