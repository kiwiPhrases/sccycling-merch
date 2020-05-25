from inv_check.models import Item, Coming, Sale, Order
from django.core.exceptions import ValidationError
import os, re
import numpy as np
import pandas as pd

data_path = "C:/Users/SpiffyApple/Documents/USC/Clubs/Cycling/sccycling-heroku"

df = pd.read_excel("/".join([data_path, 'assets.xlsx']))

# replace NaNs with 0s
sizeCols = ['XXS', 'XS', 'S', 'M', 'L', 'XL',
       'XXL', 'XXXL','count']
       
df.loc[:,sizeCols] = df.loc[:,sizeCols].replace(np.nan, 0)   


# replace nans with empty string    
df.Description.replace(np.nan, 'no description',inplace=True)
defaultImageUrl = 'https://drive.google.com/uc?id=1WZFyFdPikqZtkAI1KtvgmMJzJBzNHT8U'
df.imgurl_1.replace(np.nan, defaultImageUrl,inplace=True)

# assign genders
df.loc[:,'gender'] = 'U'
df.loc[df.Item.str.contains('M$'),'gender'] = 'M'
df.loc[df.Item.str.contains('W$'),'gender'] = 'W'

# get field names from Item
#fields = [i.name for i in Item.objects.get(pk=1)._meta.get_fields()]


#skip fields:
skipFields = ['coming', 'sale', 'order','id']

# align field names with those of the df
df.columns = df.columns.str.lower().str.replace("\s",'_')
df.rename(columns = {'item_type':'itemtype', 'forsale':'forSale'},inplace=True)
df.loc[:,['retail_price','team_price']] = df.loc[:,['retail_price','team_price']].replace(np.nan, 0)

skippedItems = []
for i,row in df.iterrows():
    try:
        item = Item.objects.create(**row.to_dict())

        item.full_clean()
        item.save()
    except ValidationError as e:
        skippedItems.append(i)
        print(i,e.message_dict)