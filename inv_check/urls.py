from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib import admin
from . import views

#app_name = 'inventoryCheck'

urlpatterns = [
    path('', include('django.contrib.auth.urls')), #accounts/
    #path(r'admin/', admin.site.urls),
    path(r'', views.index, name='index'),
    #path('<int:item_id>/', views.showInventory, name='details'),
    #path(r'select-item-public/', views.findBySelectionPublic, name='item-select-public'), #original public viewing page for item
    path(r'select-item-public/', views.productViewOrder, name='item-select-public'),
    #path(r'select-item-public/', views.productViewOrder_test, name='item-select-public'), #
    path(r'order-form/', views.makeOrder, name='order-form'),
    #path(r'search-item/', views.findbyname, name='item-search'),
    #path(r'select-item/', views.findBySelection, name='item-selection'),
    #path(r'record-sale/', views.recordSale, name='record-sale'),
    path(r'add-new-item/', views.addNewItem, name='new-item'),
    path(r'show-orders/', views.showOrders_ver2, name='show-orders'),
    path(r'order-cart/', views.orderCart, name='order-cart'),
    path(r'order-confirmation/', views.orderConfirm, name='order-confirm'),
    #path(r'select-order-public/', views.productViewOrder, name='select-order'),
]