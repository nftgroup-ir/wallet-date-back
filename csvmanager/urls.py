from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
        path('csv/', views.listCreate.as_view(), name='listCreate'),
        path('csv/<pk>', views.listCreate.as_view(), name='listtCreate'),
        path('csv/lottery/', views.LotteryListCreate.as_view(), name='LotteryListCreate'),
        path('csv/transaction/', views.TransactionListCreate.as_view(), name='TransactionListCreate'),
        path('csv/nft/', views.NFTListCreate.as_view(), name='NFTListCreate'),
        path('csv/balancedata/', views.BalanceDataListCreate.as_view(), name='BalanceDataListCreate'),
        path('csv/scrape/', views.scrape , name = 'scrape'),
        path('csv/AddressSerializer/', views.AddressSerializer.as_view(), name = 'AddressSerializer'),
        path('csv/get_transactions/', views.transactiondetails, name = 'transactiondetails')
]

