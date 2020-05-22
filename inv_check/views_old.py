from django.http import HttpResponse, HttpResponseRedirect, Http404
from django import forms
from django.views.generic import ListView, CreateView, UpdateView
from django.template import loader 
from django.shortcuts import render, redirect
from inv_check.models import Item, Coming, Sale
from django.db.models import Max

from .forms import NameForm,ItemSaleForm, addItemForm #, ItemSelectForm

def index(request):
   #return HttpResponse("<h1><strong><center>SC Cycling Inventory</center></strong></h1>")
   latestYear = Item.objects.aggregate(Max('year'))['year__max']
   latestItems = Item.objects.filter(year=latestYear)
   datDict = {}
   datDict['headers'] =  ['item','gender','available sizes','price']
   datDict['rows'] = []
   countFields = [ 'xxs','xs','s','m','l','xl','xxl','xxxl','count']
   for item in latestItems:
       itemName =  item.item
       sizeList = []
       for size in countFields:
            if getattr(latestItems[0],size)>0:
                sizeList.append(size)
       datDict['rows'].append([itemName.title(),item.gender,",".join(sizeList).upper(),item.retail_price])

   context = {'fields':datDict}     
   return render(request, 'inv_check/index.html', context)

class itemsListView(ListView):
    model = Item
    context_object_name = 'item'
    
def recordSale(request):
   if request.method == 'POST':
        form = ItemSaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)

            # get corresponding item
            item = Item.objects.get(item__iexact = sale.item.item)
            itemID = item.id
            if sale.size == 'count':
                item.count = item.count - sale.quantity
                item.save(update_fields = ['count'])
            if sale.size != 'count':
                n = getattr(item, sale.size)
                setattr(item,sale.size,n-sale.quantity)
                item.save(update_fields=[sale.size])
                
        return HttpResponseRedirect('/inv_check/%d/' %itemID)    
   else:
        form = ItemSaleForm()
   return render(request, 'inv_check/sale.html', {'form': form}) 
   
def addNewItem(request):
   if request.method == 'POST':
        form = addItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.save()
        itemID = item.id
        return HttpResponseRedirect('/inv_check/%d/' %itemID) 
   else:
        form = addItemForm()
   return render(request, 'inv_check/newItem.html', {'form': form})
   
def findbyname(request):
    #if this is a POST request we need to process the form data
    if request.method == 'POST':
        #create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        #check whether it's valid:
        if form.is_valid():
            itemName = form.cleaned_data['itemName']
            #reverse look up item id
            try:
                itemsFound = Item.objects.filter(item__icontains=itemName)
                if len(itemsFound) == 1:
                    itemID = itemsFound[0].id
                    redirect to a new URL:
                    return HttpResponseRedirect('/inv_check/%d/' %itemID)
                    
                if len(itemsFound)>1:
                    itemChoices = [(i.item.lower(),i.item) for i in itemsFound]
                    return HttpResponse('Multiple items found, please try again')
                    return createdropdown(request, itemChoices)
                    
            except IndexError:
                raise Http404("Item does not exist")

    #if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()

    return render(request, 'inv_check/name.html', {'form': form})  
    
 
    
def createdropdown(request, itemChoices):
    #define the form
    class ItemSelectForm(forms.Form):
        selected_item = forms.ChoiceField(label="Select item", choices = itemChoices)
    
    #get form input
    form = ItemSelectForm(request.POST, itemChoices)
    if form.is_valid():
        #get the item ID
        itemName = form.cleaned_data['selected_item']
        itemID = Item.objects.get(item__iexact=itemName).id
        #redirect to a new URL:
        return HttpResponseRedirect('/inv_check/%d/' %itemID)    
        return render(request, 'inv_check/itemchoices.html', {'form': form})
    else:
        form = ItemSelectForm()

    return render(request, 'inv_check/itemchoices.html', {'form': form}) 
    
def findBySelection(request):   
    items = Item.objects.all()
    itemChoices = [(i.item.lower(),i.item) for i in Item.objects.all()]  
    return createdropdown(request,itemChoices)

