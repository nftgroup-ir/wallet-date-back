from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
        path('csv/<pk>', views.listCreate.as_view(), name='listtCreate'),
        path('csv/lottery/', views.LotteryListCreate.as_view(), name='LotteryListCreate'),
        path('csv/transaction/', views.TransactionListCreate.as_view(), name='TransactionListCreate'),
        path('csv/nft/', views.NFTListCreate.as_view(), name='NFTListCreate'),
        path('csv/balancedata/', views.BalanceDataListCreate.as_view(), name='BalanceDataListCreate'),
        path('csv/scrape/', views.scrape , name = 'scrape'),
        path('csv/get_transactions/', views.transactiondetails, name = 'transactiondetails'),
        path('csv/get_nfts/', views.nftDetails, name = 'nftDetails'),
        path('csv/get_balances/', views.balanceDetails, name='nftDetails'),
        path('csv/', views.filters.as_view() , name = 'filters'),
        path('csv/data_getter/', views.getWalletDate,name='dataGetter'),
        path('csv/data_getter_by_token/', views.getWalletDataByToken,name='dataGetterbyToken'),
        path('csv/address_getter/', views.blockchainScraper, name = 'address_getter'),
        path('csv/get_nftcompany/', views.NFTCompanyEtherscanScraper, name = 'GetNftCompany'),
        path('csv/get_txbyblock/', views.getTxByBlock, name = 'getTxByBlock'),
        path('csv/get_block/', views.getBlocksURL, name = 'getBlocks'),
        path('csv/nftcompany/', views.NftCompanyListCreate.as_view() , name='NFTCompanyListCreate'),
        path('csv/chart/', views.Chart  , name = 'TXChart'),
        path('csv/get_tags/', views.tagsDetail  , name = 'tagsDetail'),
        path('csv/get_tokentx/', views.tokenTxGetter  , name = 'tokentx'),
        path('csv/get_tokentxreport/', views.tokenTxReporter  , name = 'tokentx'),

        #path('csv/get_balance/', views.balanceDetails, name = 'nftDetails'),
]

