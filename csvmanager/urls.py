from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
        path('csv/', views.listCreate.as_view(), name='listCreate'),
        path('csv/<pk>', views.listCreate.as_view(), name='listtCreate'),
        path('csv/lottery/', views.LotteryListCreate.as_view(), name='LotteryListCreate'),

]

