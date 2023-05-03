'''
prompt

Write code to extract data from the invoice
"https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbHdMvz%2FbtscHQrjdn7%2Fs9sHRPtvsfKKVtkTliikx1%2Fimg.png"
and store it in a dataframe using Python's 'mindee' library.

'''


import pandas as pd
import mindee

# Set up Mindee API key
mindee.set_api_key('3cdc41fac36e7f877c7ca11b23e97708')

# Load the invoice image
invoice_image = 'https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbHdMvz%2FbtscHQrjdn7%2Fs9sHRPtvsfKKVtkTliikx1%2Fimg.png'
response = mindee.invoice(file_url=invoice_image)

# Extract relevant data fields from the JSON response
invoice_data = {}
invoice_data['invoice_number'] = response['data']['invoice_number']
invoice_data['invoice_date'] = response['data']['invoice_date']
invoice_data['company_name'] = response['data']['seller']['name']
invoice_data['total_amount'] = response['data']['total_amount']

# Store the extracted data in a pandas dataframe
df = pd.DataFrame([invoice_data])
print(df)





'''
prompt

I want to extract line item data also.
'''

import requests
import json
import re
import pandas as pd
from PIL import Image
from io import BytesIO
from mindee import Client

# Define your Mindee API credentials
client = Client(api_key="3cdc41fac36e7f877c7ca11b23e97708")

# Load the invoice image from URL
url = "https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbHdMvz%2FbtscHQrjdn7%2Fs9sHRPtvsfKKVtkTliikx1%2Fimg.png"
response = requests.get(url)
img = Image.open(BytesIO(response.content))

# Extract the invoice data using the Mindee API
result = client.invoice.process_file(img, output_format='df')

# Define a regex pattern to extract line item information
pattern = r'([A-Z].+?)\s+(\d+)\s+(\d+,\d+.\d+)\s+(\d+,\d+.\d+)'

# Find the table regions that contain line item information
line_item_regions = []
for region in result['document']['page'][0]['table_regions']:
    if 'line_items' in region:
        line_item_regions.append(region)

# Extract the line item data from each table region
line_items = []
for region in line_item_regions:
    for line_item in region['line_items']:
        text = line_item['text']
        matches = re.findall(pattern, text)
        if matches:
            name, qty, price, total = matches[0]
            line_items.append({
                'name': name,
                'quantity': qty,
                'price': price,
                'total': total
            })

# Convert the line item data to a dataframe
line_items_df = pd.DataFrame(line_items)

# Merge the line item data with the invoice data
merged_df = pd.merge(result['document']['line_items'], line_items_df, on='name', how='outer')

# Print the merged dataframe
print(merged_df)


'''
prompt
module 'mindee' has no attribute 'set_api_key'
'''



import requests
from mindee import MindeeAPI
from mindee import Document

api_key = "YOUR_API_KEY_HERE"
document_url = "https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbHdMvz%2FbtscHQrjdn7%2Fs9sHRPtvsfKKVtkTliikx1%2Fimg.png"

# create a MindeeAPI instance with your API key
mindee_api = MindeeAPI(api_key)

# get the document
response = requests.get(document_url)
document = Document(content=response.content, filename="invoice.png")

# extract the invoice data
invoice_data = mindee_api.invoice(document).to_dict()

# extract line item data
line_item_data = []
for line_item in invoice_data["line_items"]:
    line_item_dict = {}
    for key, value in line_item.items():
        if key == "product_name":
            line_item_dict["product"] = value
        elif key == "quantity":
            line_item_dict[key] = float(value)
        elif key == "unit_price":
            line_item_dict[key] = float(value.replace(",", "."))
        elif key == "total_price":
            line_item_dict[key] = float(value.replace(",", "."))
    line_item_data.append(line_item_dict)

# create a dataframe with the line item data
import pandas as pd
line_item_df = pd.DataFrame(line_item_data)

print(line_item_df)





'''
prompt
'Client' object has no attribute 'invoice'
'''

import requests
import pandas as pd
from mindee import Client

# set API key
Client.set_api_key('3cdc41fac36e7f877c7ca11b23e97708')

# specify image url
url = "https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbHdMvz%2FbtscHQrjdn7%2Fs9sHRPtvsfKKVtkTliikx1%2Fimg.png"

# call the Mindee API to extract data
response = requests.get(url)
doc = Client().document(content=response.content, input_type="content", doc_type="invoice")
data = doc.to_dict()

# extract line item data
line_items = []
for item in data['fields']['items']:
    name = item['name']['text']
    qty = item['quantity']['text']
    price = item['price']['text']
    total = item['total']['text']
    line_items.append({'Name': name, 'Quantity': qty, 'Price': price, 'Total': total})

# store line item data in a dataframe
df = pd.DataFrame(line_items)

# display dataframe
print(df)

'''

'Client' object has no attribute 'document'
type object 'Client' has no attribute 'set_api_key'

'''


import requests
import pandas as pd
import io
from PIL import Image
import mindee

# set API key

# load invoice image
url = 'https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbHdMvz%2FbtscHQrjdn7%2Fs9sHRPtvsfKKVtkTliikx1%2Fimg.png'
response = requests.get(url)
img = Image.open(io.BytesIO(response.content))

# extract invoice data
client = mindee.Client(api_key="3cdc41fac36e7f877c7ca11b23e97708")
result = client.extract(img, type="invoice")

# extract line items data
line_items = []
for line in result['lines']:
    line_items.append({
        'item': line['data'][0]['text'],
        'quantity': line['data'][1]['text'],
        'unit_price': line['data'][2]['text'],
        'total_price': line['data'][3]['text']
    })

# convert line items list to a pandas dataframe
df = pd.DataFrame(line_items)

print(df.head())