from django.db import models
import re
import datetime
# Create your models here.
#Item	Description	Price	count	XXS	XS	S	M	L	XL	XXL	XXXL 

class Item(models.Model):
    #itemID = models.AutoField(primary_key = True)
    item = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    retail_price = models.DecimalField(max_digits=6,decimal_places=2)
    team_price = models.DecimalField(max_digits=6,decimal_places=2)
    xxs = models.IntegerField(default=0)
    xs = models.IntegerField(default=0)
    s = models.IntegerField(default=0)
    m = models.IntegerField(default=0)
    l = models.IntegerField(default=0)
    xl = models.IntegerField(default=0)
    xxl = models.IntegerField(default=0)
    xxxl = models.IntegerField(default=0)
    count = models.IntegerField("If no sizes, enter count",default=0)
    class Gender(models.TextChoices):
        Male = 'M'
        Womens = 'W'
        Unisex = 'U'
        
    forSale = models.BooleanField('Is item for sale? ',default = True)    
    gender = models.CharField(max_length = 1, choices = Gender.choices, default =Gender.Unisex)
    itemTypes = [(s,s) for s in ['hoodie','tshirt','jersey','bibs','vest','armwarmers','jacket','cap',  'gloves','water bottle','pedals','wheels','bag','bike','bags','miscellaneous']]
    itemtype = models.CharField(max_length=13, choices = itemTypes) 
    
    def current_year():
        return datetime.date.today().year
        
    year = models.IntegerField("year item is added", default=current_year)
    
    def team_discount(self):
        return( retail_price > team_price)
        
    def MTB(self):
        return('mtb' in self.item.lower())
        
    def __str__(self):
        return self.item
        
    def __iter__(self):
        for field in self._meta.get_fields():
            yield (field.name, field.value_from_object(self))
        
class Coming(models.Model):
    #itemID = models.ForeignKey(itemID)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    xxs = models.IntegerField(default=0)
    xs = models.IntegerField(default=0)
    s = models.IntegerField(default=0)
    m = models.IntegerField(default=0)
    l = models.IntegerField(default=0)
    xl = models.IntegerField(default=0)
    xxl = models.IntegerField(default=0)
    xxxl = models.IntegerField(default=0)
    count = models.IntegerField(default=0)
    
    def __str__(self):
        return self.item.item
    def __iter__(self):
        for field in self._meta.get_fields():
            yield (field.name, field.value_from_object(self))
            
class Sale(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    #gender = models.ForeignKey(Item, on_delete=models.CASCADE)
    
    class Recipient(models.TextChoices):
        TEAM = 'TEAM'
        RETAIL = 'RETAIL'

    recipient = models.CharField(max_length=6, choices = Recipient.choices)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField("Receipt $ amount ",max_digits=6,decimal_places=2)
    ship = models.BooleanField("Does price include shipping?", default=False)
    itemSizes = [(s,s.upper()) for s in  ['xxs','xs','s','m','l','xl','xxl','xxxl','count']]
    size = models.CharField("Item size (if no size, select count) ", max_length = 5, choices = itemSizes)
    date = models.DateField('date of sale',auto_now_add=True)
    
    #def __str__(self):
    #    return self.item.item
    
    #def __iter__(self):
    #    for field in self._meta.get_fields():
    #        yield (field.name, field.value_from_object(self))

class Order(models.Model):
    # item description
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    itemSizes = [(s,s.upper()) for s in  ['xxs','xs','s','m','l','xl','xxl','xxxl','count']]
    size = models.CharField("Sold item size (if no size, select count) ", max_length = 5, choices = itemSizes)
    quantity = models.IntegerField(default=1)
    
    class Recipient(models.TextChoices):
        TEAM = 'TEAM MEMBER'
        RETAIL = 'RETAIL'

    recipient = models.CharField(max_length=11, choices = Recipient.choices, default=Recipient.RETAIL)
    date = models.DateField('date of order',auto_now_add=True)
    
    # contact form
    name = models.CharField(max_length=50)
    address1 = models.CharField(max_length=50)
    address2 = models.CharField(default = '',max_length=10)
    city = models.CharField(max_length=15)
    state = models.CharField(max_length=3)
    zip = models.IntegerField()
    email = models.EmailField()
    phone = models.CharField(max_length=13)
    completed = models.BooleanField(default=False)