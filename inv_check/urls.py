from django.urls import path

from . import views

#app_name = 'inventoryCheck'

urlpatterns = [
    path(r'', views.index, name='index'),
    #path('<int:item_id>/', views.showInventory, name='details'),
    path(r'search-item/', views.findBySelectionPublic, name='item-select-public'),
    path(r'order-form/', views.makeOrder, name='order-form'),
    path(r'search-item/', views.findbyname, name='item-search'),
    path(r'select-item/', views.findBySelection, name='item-selection'),
    path(r'record-sale/', views.recordSale, name='record-sale'),
    path(r'add-new-item/', views.addNewItem, name='new-item'),
    path(r'show-orders/', views.showOrders, name='show-orders'),
]