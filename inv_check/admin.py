from django.contrib import admin

from .models import Item, Coming, Sale, Order

admin.site.register(Item)
admin.site.register(Coming)
admin.site.register(Sale)
admin.site.register(Order)
# Register your models here.
