from django.contrib import admin

from .models import Item, Coming, Sale, Order, FrontPics

admin.site.register(Item)
admin.site.register(Coming)
admin.site.register(Sale)
admin.site.register(Order)
admin.site.register(FrontPics)
# Register your models here.
