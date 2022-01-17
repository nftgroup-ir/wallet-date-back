import decimal
from logging import error
from typing import Counter
from django.db.models.fields import DecimalField
from django.shortcuts import render
from rest_framework import generics

from csvmanager.web3funcs import TxWeb3BalanceByBlock 
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
import environ
import os
from .web3funcs import *
from django.db.models import Q


BASE_DIR = os.path.dirname(os.path.dirname((os.path.abspath(__file__))))
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
env = environ.Env()
import django_filters
from django_filters import DateFromToRangeFilter
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta, MO





infura = 'https://mainnet.infura.io/v3/5e5b7b87ad6a4a899bd80becd958b765'

def removeUnicodeCharacters(data):
    if data != None:
        data = data.encode('ascii', 'ignore').decode("utf-8")
    else: data = ""
    return data
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
            
        elif response.status_code == 504 or response.status_code ==524 or response.status_code == 503:
            time.sleep(10)

        elif response.status_code == 429:
            time.sleep(5)

        else: 
            print('transactions error for ',walletAddress , 'error code: ',response.status_code)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        return False
    
def TokenTxCovaltGetter(walletAddress,tokenSC):
        response = requests.get(f"https://api.covalenthq.com/v1/1/address/{walletAddress}/transfers_v2/?contract-address={tokenSC}&key=ckey_12d0a9ab40ec40778e2f5f7965c")
        if response.status_code == 200:
            data = response.json()
            for block in data['data']['items']:
                for transfers in block['transfers']:
                    Unique = transfers['tx_hash']+transfers['delta']
                    obj, created = TokenTransactions.objects.update_or_create(unique = Unique,
                            defaults={
                                    "fromAddress" : transfers['from_address'],
                                    "toAddress" : transfers['to_address'],
                                    "tokenName" : transfers['contract_name'],
                                    "tokenSymbol" : transfers['contract_ticker_symbol'],
                                    "tokenDelta": Decimal(transfers['delta']),
                                    "tokenSingle" : transfers['quote_rate'],
                                    "tokenDeltaUSD" : transfers['delta_quote'],
                                    "tokenSC" :  transfers['contract_address'],
                                    "txType" :  transfers['transfer_type'] ,
                                    "tokenDecimal" : transfers['contract_decimals'],
                                    "Date" : transfers['block_signed_at'],
                                    "ethDelta" :  block['gas_quote_rate'],
                                    "blockNumber": block['block_height'],
                                    "txHash": transfers['tx_hash'],
                            }
                    )

            print('token transactions update for: ',walletAddress,)
        elif response.status_code == 504 or response.status_code ==524 or response.status_code == 503:
            time.sleep(10)

        elif response.status_code == 429:
            time.sleep(5)

        else: 
            print('transactions error for ',walletAddress , 'error code: ',response.status_code)
        return True

class TokenTransactionsFilter(django_filters.FilterSet):
    Date = DateFromToRangeFilter()
    class Meta:
        model = TokenTransactions
        fields = ['Date']

def TokenTxCovaltReporter (wallet,tokenSC,fromDate,toDate):
    TokenTxCovaltGetter(wallet,tokenSC)
    buyToken = 0
    sellToken=0
    spendETH=0
    earnETH=0
    decimal = 0
    print(fromDate,toDate)
    TXs = TokenTransactionsFilter({'Date_after': fromDate , 'Date_before': toDate})
  
    TXs = TXs.qs.filter(
        Q(fromAddress=wallet) |
        Q(toAddress=wallet)
    ).filter(tokenSC=tokenSC)
    print(len(TXs))
    for tx in TXs:
        if tx.txType=='IN':
            buyToken += tx.tokenDelta
            spendETH += tx.tokenDeltaUSD/tx.ethDelta
        else:
            sellToken += tx.tokenDelta
            earnETH += tx.tokenDeltaUSD/tx.ethDelta   
        decimal = tx.tokenDecimal    
    return {
        'wallet': wallet,
        'buy token' :  Decimal(buyToken/(10**decimal)),
        'spend eth': spendETH,
        'sell token':  Decimal(sellToken/(10**decimal)),
        'earnETH': earnETH
    }



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
        
        elif response.status_code == 504 or response.status_code ==524 or response.status_code == 503:
            time.sleep(10)

        elif response.status_code == 429:
            time.sleep(5)

        

        else:
            print('balances error for ',walletAddress , 'error code: ',response.status_code)
            return False
    except :
        print("Unexpected error:", sys.exc_info()[0])
        return False

def startbalanceCovaltGetter(walletAddress,walletID):
    t = threading.Thread(target=balanceCovaltGetter,args=[walletAddress,walletID])
    t.setDaemon(True)
    t.start()



def balanceDetails(request):
    csv = CSV.objects.all()
    for index,i in enumerate(csv):
        if index % 15 == 0:
            time.sleep(1.25)
        startbalanceCovaltGetter(i.address,i.id)
    responseData = {
        'result': 'balances Updated',
    }
    return JsonResponse(responseData)
    
def NftMoralisGetter(walletAddress,walletID,index):
    try:
        response = requests.get(f"https://deep-index.moralis.io/api/v2/{walletAddress}/nft?chain=eth&format=decimal", headers = {"accept":"application/json", "X-API-Key":"Xv6WsHrCbYI3ebzEuHlaBWXZbdRo0tvpDaI9zH8CbffKzClvWp5nX2BkWuRGUbp2"})

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
        
        elif response.status_code == 504 or response.status_code ==524 or response.status_code == 503:
            time.sleep(10)

        elif response.status_code == 429:
            time.sleep(5)
            
        else:
            print('nft error for ',walletAddress , 'error code: ',response.status_code)
            return False

    except :
        print("Unexpected error:", sys.exc_info()[0])
        return False

    
        



def startNftMoralisGetter(walletAddress,walletID,index):
    t = threading.Thread(target=NftMoralisGetter,args=[walletAddress,walletID,index])
    t.setDaemon(True)
    t.start()
    
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
        if self.request.GET['TagsValue'] != "":
            queryset = queryset.filter(nft_company=self.request.GET['TagsValue'])



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
    if env('SERVER') == "1":
        driver=webdriver.Firefox(options=options, firefox_binary=firefox_binary)
    else:
        driver = webdriver.Firefox(executable_path=env('DRIVER'))

    
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
    for index,i in enumerate(csv):
        if index % 10 == 0:
            time.sleep(2)
        startTxCovaltGetter(i.address,i.id)
    responseData = {
        'result': 'Transactions Updated',
    } 
    return JsonResponse(responseData)




        

def  nftDetails(request):
    csv = CSV.objects.all()
    for index,i in enumerate(csv):
        if index % 5 == 0:
            time.sleep(1.5)
        startNftMoralisGetter(i.address,i.id,index)
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
    if env('SERVER') == "1":
        driver=webdriver.Firefox(options=options, firefox_binary=firefox_binary)
    else:
        driver = webdriver.Firefox(executable_path=env('DRIVER'))
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



def NFTCompanyEtherscanScraper(request):
    # driver = webdriver.Firefox(executable_path="C:\FireFoxDriver\geckodriver.exe")
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    firefox_binary = FirefoxBinary('/usr/bin/firefox')
    if env('SERVER') == "1":
        driver=webdriver.Firefox(options=options, firefox_binary=firefox_binary)
    else:
        driver = webdriver.Firefox(executable_path=env('DRIVER'))
    nft = NFT.objects.values_list('token_address', flat=True).distinct()
    for i in nft:
        try:
            driver.get(f"https://etherscan.io/token/{i}")
            name = driver.find_element(By.CSS_SELECTOR, '.h4 .text-secondary').text
            site_url = driver.find_elements(By.CSS_SELECTOR, '.col-md-8')[4].find_element(By.CSS_SELECTOR, 'a').text

            if "http" in site_url:
                new_nftcompany, created = NftCompany.objects.update_or_create(site_url = site_url, defaults = {
                    'site_url': site_url,
                    'name' : name,
                    'smartContract':i
                    })
                print(new_nftcompany.id)
        except:
            pass


class NFTFilter(django_filters.FilterSet):
    synced_at = DateFromToRangeFilter()
    class Meta:
        model = NFT
        fields = ['synced_at']

class TransactionFilter(django_filters.FilterSet):
    block_timestamp = DateFromToRangeFilter()
    class Meta:
        model = Transaction
        fields = ['block_timestamp']

class BalanceFilter(django_filters.FilterSet):
    last_transferred_at = DateFromToRangeFilter()
    class Meta:
        model = BalanceData
        fields = ['last_transferred_at']



def Chart(request):
    Address= request.GET['address']
    csv = CSV.objects.filter(address=Address)[0].id
    if request.GET['Type'] == 'NFT':
        if request.GET['TimeBase'] == 'day':
            nft_list = []
            fromdate = request.GET['fromdate']
            todate = request.GET['todate']

            while fromdate <= todate:
                f = NFTFilter({'synced_at_after': fromdate , 'synced_at_before': fromdate})
                date = datetime.strptime(fromdate, '%Y-%m-%d').date()
                date_str = str(date.month)+'/'+str(date.day)
                new_pairs = {'date': date_str , 'NFTs' : len(f.qs.filter(parent_id = csv)) }
                nft_list.append(new_pairs)
                fromdate = datetime.strptime(fromdate, '%Y-%m-%d').date()
                fromdate += timedelta(days=1)
                fromdate = str(fromdate)

            responseData = {
                'result': nft_list,
            }
            return JsonResponse(responseData)

        elif request.GET['TimeBase'] == 'month':
            nft_list = []
            fromdate = request.GET['fromdate']
            todate = request.GET['todate']

            while fromdate <= todate:
                next_month = datetime.strptime(fromdate, '%Y-%m-%d').date()
                next_month += relativedelta(months=1)
                next_month = str(next_month)
                f = NFTFilter({'synced_at_after': fromdate, 'synced_at_before': next_month})
                date = datetime.strptime(fromdate, '%Y-%m-%d').date()
                date_str = str(date.year) + '/' + str(date.month)
                new_pairs = {'date': date_str, 'NFTs': len(f.qs.filter(parent_id=csv))}
                nft_list.append(new_pairs)
                fromdate = datetime.strptime(fromdate, '%Y-%m-%d').date()
                fromdate += relativedelta(months=1)
                fromdate = str(fromdate)

            responseData = {
                'result': nft_list,
            }
            return JsonResponse(responseData)

        elif request.GET['TimeBase'] == 'year':
            nft_list = []
            fromdate = request.GET['fromdate']
            todate = request.GET['todate']

            while fromdate <= todate:
                last_month_of_year = datetime.strptime(fromdate, '%Y-%m-%d').date()
                last_month_of_year += relativedelta(years=1)
                last_month_of_year = str(last_month_of_year)
                f = NFTFilter({'synced_at_after': fromdate, 'synced_at_before': last_month_of_year})
                date = datetime.strptime(fromdate, '%Y-%m-%d').date()
                date_str = str(date.year) + '/' + str(date.month)
                new_pairs = {'date': date_str, 'NFTs': len(f.qs.filter(parent_id=csv))}
                nft_list.append(new_pairs)
                fromdate = datetime.strptime(fromdate, '%Y-%m-%d').date()
                fromdate += relativedelta(years=1)
                fromdate = str(fromdate)

            responseData = {
                'result': nft_list,
            }
            return JsonResponse(responseData)

    elif request.GET['Type'] == 'Transaction':
        sendGet = Transaction.objects.filter(from_address=Address)
        receiveGet = Transaction.objects.filter(to_address=Address)
        if request.GET['TimeBase'] == 'day':
            transaction_list = []
            fromdate = request.GET['fromdate']
            todate = request.GET['todate']

            while fromdate <= todate:
                # p = TransactionFilter({'block_timestamp_after': fromdate , 'block_timestamp_before': fromdate})
                date = datetime.strptime(fromdate, '%Y-%m-%d').date()
                date_str = str(date)
                timestamp_date = time.mktime(datetime.strptime(date_str, "%Y-%m-%d").timetuple())
                # date_str = str(date.month)+'/'+str(date.day)
                send = len(sendGet.filter(block_timestamp__range=[fromdate , fromdate]))
                receive = len(receiveGet.filter(block_timestamp__range=[fromdate , fromdate]))
                new_pairs = {'date': timestamp_date ,'send': send,'receive': receive,'total': send + receive}
                transaction_list.append(new_pairs)
                fromdate = datetime.strptime(fromdate, '%Y-%m-%d').date()
                fromdate += timedelta(days=1)
                fromdate = str(fromdate)

            responseData = {
                'result': transaction_list,
            }
            return JsonResponse(responseData)

        elif request.GET['TimeBase'] == 'month':
            transaction_list = []
            fromdate = request.GET['fromdate']
            todate = request.GET['todate']

            while fromdate <= todate:
                next_month = datetime.strptime(fromdate, '%Y-%m-%d').date()
                next_month += relativedelta(months=1)
                next_month = str(next_month)
                f = TransactionFilter({'block_timestamp_after': fromdate, 'block_timestamp_before': next_month})
                date = datetime.strptime(fromdate, '%Y-%m-%d').date()
                date_str = str(date)
                timestamp_date = time.mktime(datetime.strptime(date_str, "%Y-%m-%d").timetuple())
                new_pairs = {'date': timestamp_date,'send': len(f.qs.filter(from_address=Address)),'receive': len(f.qs.filter(to_address=Address)),'total': len(f.qs.filter(from_address=Address))+len(f.qs.filter(to_address=Address))}
                transaction_list.append(new_pairs)
                fromdate = datetime.strptime(fromdate, '%Y-%m-%d').date()
                fromdate += relativedelta(months=1)
                fromdate = str(fromdate)

            responseData = {
                'result': transaction_list,
            }
            return JsonResponse(responseData)


        # elif request.GET['TimeBase'] == 'year':
        #     transaction_list = []
        #     fromdate = request.GET['fromdate']
        #     todate = request.GET['todate']
        #     print(fromdate , '------------------------------', todate)

        #     while fromdate <= todate:
        #         last_month_of_year = datetime.strptime(fromdate, '%Y-%m-%d').date()
        #         last_month_of_year += relativedelta(years=1)
        #         last_month_of_year = str(last_month_of_year)
        #         # f = TransactionFilter({'block_timestamp_after': fromdate, 'block_timestamp_before': last_month_of_year})
        #         f = Transaction.objects.filter(block_timestamp__range=[fromdate , last_month_of_year])
        #         date = datetime.strptime(fromdate, '%Y-%m-%d').date()
        #         date_str = str(date)
        #         timestamp_date = time.mktime(datetime.strptime(date_str, "%Y-%m-%d").timetuple())
        #         # s = f.qs
        #         print(len(f),"inja",f ,"-----------" , f.filter(to_address=Address))
        #         send = len(f.filter(from_address=Address))
        #         receive = len(f.filter(to_address=Address))
        #         print(f.filter(to_address=Address).explain( analyze=True))
        #         new_pairs = {'date': timestamp_date ,'send': send,'receive': receive,'total': send + receive}
        #         transaction_list.append(new_pairs)
        #         fromdate = datetime.strptime(fromdate, '%Y-%m-%d').date()
        #         fromdate += relativedelta(years=1)
        #         fromdate = str(fromdate)
        elif request.GET['TimeBase'] == 'year':
            transaction_list = []
            fromdate = request.GET['fromdate']
            todate = request.GET['todate']
            

            while fromdate <= todate:
                last_month_of_year = datetime.strptime(fromdate, '%Y-%m-%d').date()
                last_month_of_year += relativedelta(years=1)
                last_month_of_year = str(last_month_of_year)
                # f = TransactionFilter({'block_timestamp_after': fromdate, 'block_timestamp_before': last_month_of_year})
                # f = Transaction.objects.filter(block_timestamp__range=[fromdate , last_month_of_year])
                date = datetime.strptime(fromdate, '%Y-%m-%d').date()
                date_str = str(date)
                timestamp_date = time.mktime(datetime.strptime(date_str, "%Y-%m-%d").timetuple())
                # s = f.qs
                # print(len(f),"inja",f ,"-----------" , f.filter(to_address=Address))
                send = len(sendGet.filter(block_timestamp__range=[fromdate , last_month_of_year]))
                receive = len(receiveGet.filter(block_timestamp__range=[fromdate , last_month_of_year]))
                new_pairs = {'date': timestamp_date ,'send': send,'receive': receive,'total': send + receive}
                transaction_list.append(new_pairs)
                fromdate = datetime.strptime(fromdate, '%Y-%m-%d').date()
                fromdate += relativedelta(years=1)
                fromdate = str(fromdate)

            responseData = {
                'result': transaction_list,
            }
            return JsonResponse(responseData)



    elif request.GET['Type'] == 'Balance':
        balance_list = [ ]
        balances = BalanceData.objects.filter(parent_id = csv)
        for i in balances:
            new_pairs = {'category' : i.contract_ticker_symbol, 'value' : float(i.int_balance) }
            balance_list.append(new_pairs)
            
        responseData = {
            'result': balance_list,
        }
        return JsonResponse(responseData)
            




class NftCompanyListCreate(generics.ListCreateAPIView):
    queryset = NftCompany.objects.all()
    serializer_class = NFTCompanySerializer

    def get_queryset(self, *args, **kwargs):
        queryset = NftCompany.objects.all()

        if self.request.GET['nameInput'] != "":
            queryset = queryset.filter(name=self.request.GET['nameInput']).distinct()
        
        if self.request.GET['urlInput'] != "":
            queryset = queryset.filter(site_url=self.request.GET['urlInput'])
        
        if self.request.GET['tagInput'] != "":
            tags = self.request.GET.getlist('tagInput')
            print(tags)
            for tag in tags:
                queryset = queryset.filter(Nft_Company_Features__name = tag)
            
        
        return queryset.distinct()


def getTxByBlock(request):
    result = TxWeb3BalanceByBlock('0x4fe2117d5390d752ddb8765a228e5641779e315b',13924830,13924831)
    responseData = {
        'result': result,
    }
    return JsonResponse(responseData)

def getBlocksURL(request):
    result = getBlocks(request.GET['from'],request.GET['to'])
    responseData = {
        'result': 'shod',
    }
    return JsonResponse(responseData)


def tagsDetail(request):
    nftAll = NFT.objects.all()
    for i in nftAll:
        if i.nft_company:
            nftCompany = NftCompany.objects.filter(name = i.nft_company)[0]
            walletId = CSV.objects.filter(address = i.owner_of).values_list('id')[0][0]
            for k in CompanyFeature.objects.filter(nft_company = nftCompany):
                new_tag , created = Tags.objects.get_or_create(name = k.name , 
                defaults ={
                    'important': False,
                })
                new_tag.wallet_tags.add(walletId)
        else:
            nftCompany = NftCompany.objects.all() 
            for j in nftCompany:
                if i.token_address == j.smartContract:
                    i.nft_company_id = j.id 
                    i.save()
                    print(i,"---",i.id,"---",i.nft_company_id, "----" , j.smartContract)
                    print('nft company added')
    responseData = {
        'result': 'shod',
    }
    return JsonResponse(responseData)


def tokenTxGetter(request):
    wallets = request.GET.getlist('wallet')
    smartContract = request.GET['sc']
    report={}
    for wallet in wallets:
        if TokenTxCovaltGetter(wallet,smartContract):report[wallet]='done'
        else: msg = "error"
    return JsonResponse(report)


def tokenTxReporter(request):
    wallets = request.GET.getlist('wallet')
    smartContract = request.GET['sc']
    fromDate = request.GET['from']
    toDate = request.GET['to']
    report = []
    for wallet in wallets:
        report.append(TokenTxCovaltReporter(wallet,smartContract,fromDate,toDate))
    return JsonResponse({'data':report})



def TokenCompanyEtherscanScraper(request):
    # driver = webdriver.Firefox(executable_path="C:\FireFoxDriver\geckodriver.exe")
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    firefox_binary = FirefoxBinary('/usr/bin/firefox')
    if env('SERVER') == "1":
        driver=webdriver.Firefox(options=options, firefox_binary=firefox_binary)
    else:
        driver = webdriver.Firefox(executable_path=env('DRIVER'))
    balance = BalanceData.objects.values_list('contract_address', flat=True).distinct()
    for i in balance:
        try:
            driver.get(f"https://etherscan.io/token/{i}")
            name = driver.find_element(By.CSS_SELECTOR, '.h4 .text-secondary').text
            site_url = driver.find_elements(By.CSS_SELECTOR, '.col-md-8')[5].find_element(By.CSS_SELECTOR, 'a').text

            if "http" in site_url:
                new_tokencompany, created = TokenCompany.objects.update_or_create(site_url = site_url, defaults = {
                    'site_url': site_url,
                    'name' : name,
                    'ContractAddress':i
                    })
                print(new_nftcompany.id)
        except:
            pass

class TokenCompanyListCreate(generics.ListCreateAPIView):
    queryset = TokenCompany.objects.all()
    serializer_class = TokenCompanySerializer

    def get_queryset(self, *args, **kwargs):
        queryset = TokenCompany.objects.all()

        if self.request.GET['nameInput'] != "":
            queryset = queryset.filter(name=self.request.GET['nameInput']).distinct()
        
        if self.request.GET['urlInput'] != "":
            queryset = queryset.filter(site_url=self.request.GET['urlInput'])
        
        if self.request.GET['tokenAddressInput'] != "":
            queryset = queryset.filter(ContractAddress=self.request.GET['tokenAddressInput'])
        
        # if self.request.GET['tagInput'] != "":
        #     tags = self.request.GET.getlist('tagInput')
        #     print(tags)
        #     for tag in tags:
        #         queryset = queryset.filter(Nft_Company_Features__name = tag)
            
        
        return queryset.distinct()

def dashboardDetail(request):
    tableType = request.GET['table']
    walletAddress = request.GET['walletAddress']
    parentID = CSV.objects.filter(address=walletAddress)[0].id
    if tableType == 'balance':
        responseData = list(BalanceData.objects.filter(parent_id = parentID)[:10].values())

    elif tableType == 'NFT':
        responseData =list(NFT.objects.filter(parent_id = parentID)[:10].values())

        
    elif tableType == 'transaction':
        responseData = list(Transaction.objects.filter(Q(from_address = walletAddress) | Q(to_address = walletAddress))[:10].values())
    return JsonResponse(responseData , safe = False)
        