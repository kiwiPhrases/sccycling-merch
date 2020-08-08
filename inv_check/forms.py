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
        fields = ('item','description','retail_price','team_price','xxs','xs','s','m','l','xl','xxl','xxxl','count','gender','itemtype','year','imgurl_1')
        
        
class orderForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super(orderForm,self ).__init__(*args,**kwargs)
        self.fields['item'].queryset = Item.objects.filter(forSale=True)
        
    class Meta:
        model = Order
        fields = ('item', 'size', 'quantity', 'recipient', 'name', 'address1', 'address2','city','state','zip','email','phone')

"""     
class itemOrderForm(forms.ModelForm):
    def __init__(self,*args,**kwargs): #size_choices=None,max_quant=100,  
        size_choices = kwargs.pop('size_choices',None)
        max_quant = kwargs.pop('max_quant',None)
        item = kwargs.pop('item', None)
        super(itemOrderForm,self).__init__(*args,**kwargs) #itemOrderForm,self
        
        if size_choices:
            self.fields['item'].choices = [(s,s) for s in [item]]
            self.fields['size'].choices = size_choices
            self.fields['quantity'].choices = [(i+1,i+1) for i in range(max_quant)]
 
    class Meta:
        model = Order
        fields = ('item','size', 'quantity')  
"""
      
class itemOrderForm(forms.Form):
    item = forms.CharField(max_length=50)
    
    countFields = [ 'xxs','xs','s','m','l','xl','xxl','xxxl','count']
    sizeChoices = [(s.lower(),s.upper()) for s in countFields]
    size = forms.ChoiceField(choices = sizeChoices)
    
    quantity = forms.ChoiceField(choices = [(i,i) for i in range(5)])
    
    #recipientChoices = [('TEAM', 'TEAM MEMBER'),('RETAIL','RETAIL')]
    #recipient = forms.ChoiceField(choices = recipientChoices, required=True)
    
    def __init__(self,*args,**kwargs): #size_choices=None,max_quant=100,  
        size_choices = kwargs.pop('size_choices',None)
        max_quant = kwargs.pop('max_quant',None)
        item = kwargs.pop('item', None)
        super(itemOrderForm,self).__init__(*args,**kwargs) #itemOrderForm,self
        
        if size_choices:
            #self.fields['item'].choices = [(s,s) for s in [item]]
            self.initial['item'] = item
            self.fields['size'].choices = size_choices
            self.fields['quantity'].choices = [(i+1,i+1) for i in range(max_quant)]
            #self.fields['item'].disabled=True
            
class orderContactForm(forms.ModelForm):  
   def __init__(self,*args,**kwargs):
        super(orderContactForm,self).__init__(*args,**kwargs)
        self.initial['address2'] = " "
        self.fields['address2'].required = False
            
   class Meta:
        model = Order
        fields = ('name','email','phone','address1','address2','city','state','zip')

    
    
    
    

    