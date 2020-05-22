from django import forms
from .models import Sale, Item, Order

# enter item name
class NameForm(forms.Form):
    itemName = forms.CharField(label='Enter item name', max_length=20)
    
class ItemSaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ('item','size','price','recipient', 'quantity','ship') 
        
class addItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('item','description','retail_price','team_price','xxs','xs','s','m','l','xl','xxl','xxxl','count','gender','itemtype','year')
        
        
class orderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('item', 'size', 'quantity', 'recipient', 'name', 'address1', 'address2','city','state','zip','email','phone')
        