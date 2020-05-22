from django.urls import path

from . import views

#app_name = 'inventoryCheck'

urlpatterns = [
    path('', views.index, name='index'),
    #path('<int:item_id>/', views.showInventory, name='details'),
    path('search-item/', views.findBySelectionPublic, name='item-select-public'),
    path('order-form/', views.makeOrder, name='order-form'),
    path('search-item/', views.findbyname, name='item-search'),
    path('select-item/', views.findBySelection, name='item-selection'),
    path('record-sale/', views.recordSale, name='record-sale'),
    path('add-new-item/', views.addNewItem, name='new-item'),
    path('show-orders/', views.showOrders, name='show-orders'),
]