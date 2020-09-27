from django.http import HttpResponse, HttpResponseRedirect, Http404
from django import forms
from django.views.generic import ListView, CreateView, UpdateView
from django.template import loader 
from django.shortcuts import render, redirect
from inv_check.models import Item, Coming, Sale, Order, FrontPics
from django.db.models import Max, Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
import json

from .forms import NameForm,ItemSaleForm, addItemForm, orderForm, itemOrderForm,orderContactForm #, ItemSelectForm 

## -------------------------- home-page functions --------------------------     
def index(request):
   #return HttpResponse("<h1><strong><center>SC Cycling Inventory</center></strong></h1>")
   latestYear = Item.objects.aggregate(Max('year'))['year__max']
   
   # fetch the latest items that are for sale
   latestItems = Item.objects.filter(year=latestYear) & Item.objects.filter(forSale=True)
   latestItems = latestItems.order_by('-retail_price').order_by('-gender')
   # create dictionary of fields and values to print
   datDict = {}
   datDict['headers'] =  ['item','gender','available sizes','price']
   datDict['rows'] = []
   countFields = [ 'xxs','xs','s','m','l','xl','xxl','xxxl','count']

   for item in latestItems:
       itemName =  item.item
       sizeList = []
       for size in countFields:
            if getattr(item,size)>0:
                sizeList.append(size)
       datDict['rows'].append([itemName.title(),item.gender,",".join(sizeList).upper(),item.retail_price])
        
   # create context
   picList = [i for i in FrontPics.objects.all()][:3]
   context = {'fields':datDict, 'frontImages':picList}     
   return render(request, 'inv_check/index.html', context)

## --------------------------  HELPER FUNCTIONS -------------------------- 
class itemsListView(ListView):
    model = Item
    context_object_name = 'item'

def fetchItemDetails(item_id, fields2exclude = ['coming', 'sale', 'id','order','imgurl_1']):    
    countFields = [ 'xxs','xs','s','m','l','xl','xxl','xxxl','count']
    item = Item.objects.get(pk = item_id)
    
    # get item fields and values into a dictionary
    datDict = {}
    for field in [i.name for i in item._meta.get_fields()]:
        if field not in fields2exclude:
            val = getattr(item, field)
            # filter out 0 value count fields
            if (field in countFields):
                if (val>0):
                    datDict[field.upper()] = val
            else:
                datDict[field.title()] = val
    return(datDict)
    
def fetchOrderDetails(item_id, fields2exclude = ['coming', 'sale', 'id','order','imgurl_1']):    
    countFields = [ 'xxs','xs','s','m','l','xl','xxl','xxxl','count']
    item = Order.objects.get(pk = item_id)
    
    # get item fields and values into a dictionary
    datDict = {}
    for field in [i.name for i in item._meta.get_fields()]:
        if field not in fields2exclude:
            val = getattr(item, field)
            datDict[field.title()] = val
    return(datDict)    

### -------------------------- PUBLIC FUNCTIONS --------------------------     
def productViewOrder(request):
    # only show items for sale
    itemChoices = Item.objects.filter(forSale=True).order_by('item').order_by('-year') 

    # get item types
    #itemTypes = [i[0] for i in Item._meta.get_field('itemtype').choices] # this gets all item types
    
    # get item types from for-sale items
    itemTypes = list(dict.fromkeys([i.itemcategory for i in itemChoices]))
    itemTypes.insert(0, "select")
    itemGenders = list(dict.fromkeys([i.gender for i in itemChoices]))
    itemGenders.insert(0,'select')
    
    # create initial context
    defaultImageUrl = 'https://drive.google.com/uc?id=1WZFyFdPikqZtkAI1KtvgmMJzJBzNHT8U'
    context = {'items':itemChoices,'itemtypes':itemTypes,'itemgenders':itemGenders, 'fields':[], 'img_url':defaultImageUrl}
            
    if request.method == 'GET':
        # process GET for filter
        itemType = request.GET.get('item-type')
        itemGender = request.GET.get('item-gender')
        
        # filter item menu by type or gender
        if itemType:
            itemChoices = Item.objects.filter(itemcategory__icontains=itemType).filter(forSale=True).order_by('item').order_by('-year')
            context['items'] = itemChoices
            
        if itemGender:
            itemChoices = Item.objects.filter(gender__icontains=itemGender).filter(forSale=True).order_by('item').order_by('-year')
            context['items'] = itemChoices

        # process GET for actual item info request
        itemName = request.GET.get('item-choice')

        # if an item was selected, load its info and picture.'
        # also, show order form
        if itemName:
            # fetch the item from the database
            itemsFound = Item.objects.filter(item__icontains=itemName)
            itemID = itemsFound[0].id
            
            # display team price if user is authenticated
            if request.user.is_authenticated:
                datDict = fetchItemDetails(itemID,['coming', 'sale','order','id','forSale','imgurl_1','itemcategory','itemtype'])
            
            # do not display team price if user is not authenticated
            else:
                datDict = fetchItemDetails(itemID,['coming', 'sale','order','id','forSale','team_price','imgurl_1','itemcategory','itemtype'])
            keys = datDict.keys()      
            # unpack them into another dictionary for printing table
            #fields = {
            #    'headers': list(keys),
            #    'rows':[datDict[key] for key in keys]}
            fields = []
            for key in datDict:
                fields.append((key,datDict[key]))
                
            # update output dictionary values based on query results    
            context['fields'] = fields
            context['img_url'] = itemsFound[0].imgurl_1
            
            # get available sizes
            countFields = [ 'xxs','xs','s','m','l','xl','xxl','xxxl','count']
            sizes = [key for key in datDict.keys() if key.lower() in countFields]
            sizeChoices = [(s.lower(),s.upper()) for s in sizes]
            
            # get max quant that can be ordered
            max_quant = 0
            for s in sizes:
                if datDict[s]>max_quant:
                    max_quant = datDict[s]

            # update form with sizes, item, and quantity max
            context['form'] = itemOrderForm(size_choices = sizeChoices,max_quant = max_quant, item=itemsFound[0].item) #initial = {'item':itemsFound[0],'recipient':'RETAIL'},, item=itemsFound[0]
            
            #save item to session
            request.session['orderItem'] = itemsFound[0].id 
            
            return render(request, 'inv_check/itemchoicesshowANDorder.html', context) 
    
    #process submitted form
    if request.method == 'POST':
        form = itemOrderForm(request.POST)
        
        if form.is_valid():
            datDict = {}
            # fetch data from session
            item = Item.objects.get(pk = request.session.get('orderItem'))
            print(item)
            # fetch data from database
            
            ## if user is authenticated, user team price
            if request.user.is_authenticated:
                datDict['price'] = int(item.team_price)
            ## else use team price
            else:
                datDict['price'] = int(item.retail_price)
            #datDict['item'] = item.item
            datDict['item'] = form.cleaned_data['item']
            #datDict['img_url'] = item.imgurl_1
            
            # fetch data from the form
            datDict['size'] = form.cleaned_data['size'].upper()
            datDict['quantity'] = int(form.cleaned_data['quantity'])
            
            fields = {}
            fields['rows'] = []
            fields['headers'] = ['item','size','quantity','price']
            fields['rows'].append([datDict[key] for key in fields['headers']])
            
            # add items to order
            if request.session.get('order'):
                #sessionOrderNum = len(json.loads(request.session.get('order')))
                print("Adding items to order")

                tmpList = json.loads(request.session['order'])
                tmpList.append(fields)
                request.session['order'] = json.dumps(tmpList)
                print(request.session['order'])
            
            else:
                print("First order addition")
                request.session['order'] = json.dumps([fields])
                   
            print(json.loads(request.session.get('order')))
            #context = {'fields':json.loads(request.session.get('order'))} #:fields

            return redirect('order-cart')      
        else:
            print("Form didn't validate")
            print(request.session.get('orderItem'))
            print(form)
            print(form.errors)
            
    context['form'] = itemOrderForm()#orderForm_part1()
    return render(request, 'inv_check/itemchoicesshowANDorder.html', context)   

def orderCart(request):
    # grab order info and print to table
    fields = {}
    context = {'fields':{'headers':[],'rows':[]}}

    
    # populate order details with order info from session
    if request.session.get('order'):
        basket = json.loads(request.session.get('order'))
        fields['headers'] = basket[0]['headers']
        fields['rows'] = []
        for i in basket:
            fields['rows'].append(*i['rows'])
        print(fields)
        context = {'fields':fields}
        
    # clear cart on clear button click:
    if request.method=='GET':
        print(request.GET.get('clear-cart'))
        if request.GET.get('clear-cart'):
            request.session.pop('order')
            context['fields'] = {'headers':[],'rows':[]}
            print("basket has been cleared")
            return render(request, 'inv_check/ordercart.html', context)
        print("Get was passed but no action taken")
        
    if request.method=='POST':
        # if form is valid, create a complete Order form for each entry in the basket
        form = orderContactForm(request.POST)
        if form.is_valid():
            headers = basket[0]['headers']
            # loop over the basket
            for i in basket:
                orderDict = {}
                # process item details
                for col,val in zip(headers,*i['rows']):
                    if col == 'item':
                        itemInst = Item.objects.filter(item__icontains = val)[0]
                        orderDict['item'] = itemInst#[0]
                    if col == 'price':
                        pass
                    if col == 'size':
                        orderDict[col] = val.lower()
                    if col not in ['item', 'price', 'size']:
                        orderDict[col.lower()] = val
                # add contact from contact form
                contactMessage = 'Contact details\n'
                for col in ('name','email','phone','address1','address2','city','state','zip'):
                    orderDict[col] = form.cleaned_data[col]
                    contactMessage += "\t\n" + ": ".join([col,str(form.cleaned_data[col])])
                print(orderDict)
                # save the orders
                order = Order(**orderDict)
                try:
                    order.full_clean()
                    print(" -------- Order  saved! --------------")
                    order.save()
                except ValidationError as e:
                    print(e)
                    raise Http404(print(e) + " \nIf you get this, email burinski@usc.edu with the above message. Thank you! ")
            # if order is good,    
            # clear up the basket:
            request.session.pop('order')
            sendOrderEmail_cart(basket,contactMessage,orderDict['email'])
            
            # send to confirmation page
            return redirect('order-confirm')
            
    # get contact info
    context['contactform'] = orderContactForm()
    return render(request, 'inv_check/ordercart.html', context)
 
def readbasket(basket):
    headers = basket[0]['headers']
    lines = []
    for i in basket:
        linedict = {}
        for col,val in zip(headers,*i['rows']):
            #print(col,val)
            linedict[col] = str(val)
        lines.append(", ".join(["%s: %s" %(key,str(linedict[key])) for key in linedict.keys()]))
    messageContent = "\n".join(lines)
    return(messageContent)
    
def sendOrderEmail_cart(basket, contactDetails ,recipientemail):
    subjectline = 'New USC Merch Order'
    fromemail = 'info@usccycling.com'
    toemail = 'info@usccycling.com'
    preable = "Your order confirmation USC Cycling Club:\n\n"
    messageContent = readbasket(basket)
    postable = "\n\nThank you and fight on!"
    send_mail(subjectline,
        "\n\n".join([preable,messageContent,contactDetails,postable]),
        fromemail,
        [toemail,recipientemail],
    fail_silently=False)   

def sendOrderEmail(datdict):
    subjectline = 'New USC Merch Order'
    fromemail = 'info@usccycling.com'
    toemail = 'info@usccycling.com'
    messageContent = ",\n".join(["%s: %s" %(key,str(datdict[key])) for key in datdict.keys()])
    send_mail(subjectline,
        messageContent,
        fromemail,
        [toemail,datdict['Email']],
    fail_silently=False)    
    
def orderConfirm(request):
   #context = {}
   return render(request, 'inv_check/orderconfirmation.html')
    
def findBySelectionPublic(request):
    items = Item.objects.all()
    # only show items for sale
    itemChoices = Item.objects.filter(forSale=True).order_by('item').order_by('-year') 
    
    # create initial context
    defaultImageUrl = 'https://drive.google.com/uc?id=1WZFyFdPikqZtkAI1KtvgmMJzJBzNHT8U'
    context = {'itemChoices':itemChoices, 'fields':{'headers':[], 'rows':[]}, 'img_url':defaultImageUrl}
                    
    # show request on the website
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        itemName = request.GET.get('item-choice')
        #print(itemName)
        if itemName:
            # fetch the item from the database
            itemsFound = Item.objects.filter(item__icontains=itemName)
            itemID = itemsFound[0].id
            datDict = fetchItemDetails(itemID,['coming', 'sale','order','id','forSale','team_price','imgurl_1'])
            keys = datDict.keys()      
            # unpack them into another dictionary for printing table
            fields = {
                'headers': list(keys),
                'rows':[datDict[key] for key in keys]}
                
            # update output dictionary values based on query results    
            context['fields'] = fields
            context['img_url'] = itemsFound[0].imgurl_1
            return render(request, 'inv_check/itemchoicesshow.html', context)      

    return render(request, 'inv_check/itemchoicesshow.html', context) 

#### ------------ sendOrderEmail is an obsolete function (Delete later) -------------- 
def sendOrderEmail(datdict):
    subjectline = 'New USC Merch Order'
    fromemail = 'info@usccycling.com'
    toemail = 'info@usccycling.com'
    messageContent = ",\n".join(["%s: %s" %(key,str(datdict[key])) for key in datdict.keys()])
    send_mail(subjectline,
        messageContent,
        fromemail,
        [toemail,datdict['Email']],
    fail_silently=False)
#### --------------  makeOrder is an obsolete function (Delete later) --------------     
def makeOrder(request):
    context = {'form':orderForm(),'fields':{'headers':[], 'rows':[],'confirmation':[]}} 
    if request.method == 'POST':
        form = orderForm(request.POST)
        if form.is_valid():
            item = form.save(commit=True)
            itemID = item.id
            datDict = fetchOrderDetails(itemID,fields2exclude = ['coming', 'sale', 'id','order','date','completed'])
            keys = datDict.keys()      
            # unpack them into another dictionary for printing table
            fields = {
                'headers': list(keys),
                'rows':[datDict[key] for key in keys]}
            context['fields'] = fields   
            context['confirmation'] = ['Thank you for your order, confirmation e-mail has been sent', 'Your order details']
            # send notification of new order
            sendOrderEmail(datDict)
            return render(request, 'inv_check/makeorder.html', context)

    return render(request, 'inv_check/makeorder.html', context)    

### -------------------------- EBOARD FUNCTIONS: -------------------------- 
####  -------------- findbyname is an obsolete function (Delete later) -------------- 
@login_required
def findbyname(request):
    defaultImageUrl = 'https://drive.google.com/uc?id=1WZFyFdPikqZtkAI1KtvgmMJzJBzNHT8U'
    fields = {'headers':[], 'rows':[]}
    context = {'fields':fields, 'img_url':defaultImageUrl}
    
    
    # if this is a POST request we need to process the form data
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        itemName = request.GET.get('item-name')
        print(itemName)
        if itemName:
            itemsFound = Item.objects.filter(item__icontains=itemName)
            try:
                itemID = itemsFound[0].id
                datDict = fetchItemDetails(itemID)
                keys = datDict.keys()      
                # unpack them into another dictionary for printing table
                fields = {
                    'headers': list(keys),
                    'rows':[datDict[key] for key in keys]}
                context = {'fields':fields}
                context['img_url'] = itemsFound[0].imgurl_1
                return render(request, 'inv_check/detailshow.html', context)    
            except IndexError:
                context['fields']['headers'] = ['item']
                context['fields']['rows'] = ["Can't find item. Being more specific may help"]

    return render(request, 'inv_check/detailshow.html', context)      


## Select item functions 
@login_required
def findBySelection(request):
    items = Item.objects.all()
    # show all items
    itemChoices = Item.objects.all().order_by('item').order_by('-year')
    
    # create initial context
    defaultImageUrl = 'https://drive.google.com/uc?id=1WZFyFdPikqZtkAI1KtvgmMJzJBzNHT8U'
    context = {'itemChoices':itemChoices, 'fields':{'headers':[], 'rows':[]}, 'img_url':defaultImageUrl}
    
    # show request on the website
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        itemName = request.GET.get('item-choice')
        print(itemName)
        if itemName:
            itemsFound = Item.objects.filter(item__icontains=itemName)
            itemID = itemsFound[0].id
            datDict = fetchItemDetails(itemID, )
            keys = datDict.keys()      
            # unpack them into another dictionary for printing table
            fields = {
                'headers': list(keys),
                'rows':[datDict[key] for key in keys]}
            context['fields'] = fields
            context['img_url'] = itemsFound[0].imgurl_1
            return render(request, 'inv_check/itemchoicesshow.html', context)      

    return render(request, 'inv_check/itemchoicesshow.html', context)   


@login_required    
def recordSale(request):
   context = {'form':ItemSaleForm(),'fields':{'headers':[], 'rows':[]}}
   if request.method == 'POST':
        form = ItemSaleForm(request.POST)
         
        if form.is_valid():
            sale = form.save(commit=False)
            # get corresponding item
            item = Item.objects.get(item__iexact = sale.item.item)
            itemID = item.id
            if sale.size == 'count':
                n = item.count #old quant
                m = sale.quantity #new quant
                item.count = n - m
                item.save(update_fields = ['count'])
            if sale.size != 'count':
                n = getattr(item, sale.size) #old value
                m = n-sale.quantity #new value
                setattr(item,sale.size,m)
                item.save(update_fields=[sale.size])
        context['fields'] = {'headers':['size','old quantity', 'new quantity'],'rows':[sale.item.item,n,m]}
        return render(request, 'inv_check/sale.html', context)     
   return render(request, 'inv_check/sale.html', context)    

@login_required 
def addNewItem(request):
   context = {'form':addItemForm(),'fields':{'headers':[], 'rows':[]}}
   if request.method == 'POST':
        form = addItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.save()
        itemID = item.id
        datDict = fetchItemDetails(itemID)
        keys = datDict.keys()      
        # unpack them into another dictionary for printing table
        fields = {
            'headers': list(keys),
            'rows':[datDict[key] for key in keys]}
        context['fields'] = fields       
        return render(request, 'inv_check/newItem.html', context)

   return render(request, 'inv_check/newitem.html', context)
   
@login_required        
def showInventory(request, item_id):
    try:
        datDict = fetchItemDetails(item_id)           
        keys = datDict.keys()      
        # unpack them into another dictionary for printing table
        fields = {
            'headers': list(keys),
            'rows':[datDict[key] for key in keys]}
        context = {'fields':fields}
        
    except Item.DoesNotExist:
        raise Http404("Item does not exist")
        
    return render(request, 'inv_check/detail.html', context)
    

@login_required(login_url='/accounts/login/')    
def showOrders_ver2(request):
    context = {'fields':{'headers':[], 'rows':[]}} #,'form':ItemSaleForm()} 
    orders = Order.objects.filter(completed=False)
    context['orders'] = orders

    # print incompleted orders
    if orders:
        fields = [s.name for s in orders[0]._meta.get_fields()]
        datDict = {}
        datDict['headers'] =  fields
        datDict['rows'] = []
        for order in orders:
            row = []
            for field in fields:
                row.append(getattr(order,field))
            datDict['rows'].append(row)
        for key in context['fields'].keys():        
            context['fields'][key] = datDict[key]
            
    else:
        context['fields']['headers'] = ['Orders']
        context['fields']['rows']=[["Seems there are no outstanding orders"]]
        
    # mark selected order as completed
    if request.method == 'GET':
        orderID = request.GET.get("item-order")
        if orderID:
            print(orderID)
            order2complete = Order.objects.get(id=orderID)
            prefill = {}
            for field in ('item','size','recipient', 'quantity'):
               prefill[field] = getattr(order2complete, field)
            
            if prefill['recipient'] == 'RETAIL':
                prefill['price'] = Item.objects.get(pk =  prefill['item'].id).retail_price
            else:
                prefill['price'] = Item.objects.get(pk =  prefill['item'].id).team_price
                
            prefill['ship'] = False
            
            context['form'] = ItemSaleForm(prefill)
            
            # mark order as completed
            order2complete.completed=True
            order2complete.save(update_fields = ['completed'])
            
    # fill fields in case order needs to be modified         
    if request.method == 'POST':
        form = ItemSaleForm(request.POST)
         
        if form.is_valid():
            sale = form.save(commit=False)
            # get corresponding item
            item = Item.objects.get(item__iexact = sale.item.item)
            itemID = item.id
            if sale.size == 'count':
                n = item.count #old quant
                m = sale.quantity #new quant
                item.count = n - m
                item.save(update_fields = ['count'])
            if sale.size != 'count':
                n = getattr(item, sale.size) #old value
                m = n-sale.quantity #new value
                setattr(item,sale.size,m)
                item.save(update_fields=[sale.size])
                
        context['fields2'] = {'headers':['item','old quantity', 'new quantity'],'rows':[sale.item.item,n,m]}
        return render(request, 'inv_check/showOrders.html', context)    
        
    return render(request, 'inv_check/showOrders.html', context)  


## -------------------------- showOrders is now obsolete, delete later ------------------- ##
@login_required(login_url='/accounts/login/')    
def showOrders(request):
    context = {'fields':{'headers':[], 'rows':[]}} 
    orders = Order.objects.filter(completed=False)
    context['orders'] = orders
    # mark selected order as completed
    if request.method == 'GET':
        orderID = request.GET.get("item-order")
        if orderID:
            print(orderID)
            order2complete = Order.objects.get(id=orderID)
            order2complete.completed = True
            order2complete.save(update_fields=['completed'])
            
    # print incompleted orders
    if orders:
        fields = [s.name for s in orders[0]._meta.get_fields()]
        datDict = {}
        datDict['headers'] =  fields
        datDict['rows'] = []
        for order in orders:
            row = []
            for field in fields:
                row.append(getattr(order,field))
            datDict['rows'].append(row)
        for key in context['fields'].keys():        
            context['fields'][key] = datDict[key]
            
    else:
        context['fields']['headers'] = ['Orders']
        context['fields']['rows']=[["Seems there are no outstanding orders"]]
        
    return render(request, 'inv_check/showOrders.html', context)    