from mindee import Client, documents
import pandas as pd
import streamlit as st

# Init a new client
api_key = st.secrets["mindee_invoice_api_key"]
mindee_client = Client(api_key=api_key)

# Load a file from disk or using URL
# filepath = "C:/Users/namkee.lee/Documents/AI Builder Document Processing Sample Data/Invoices/Adatum/Train/Adatum 3.pdf"
# filepath = "C:/Users/namkee.lee/Documents/AI Builder Document Processing Sample Data/Invoices/Contoso/Train/Contoso 3.pdf"

# input_doc = mindee_client.doc_from_path(filepath)


# fileurl = "https://drive.google.com/file/d/1OON-E-_EMX9_d6pFpe-J2QHeOKH9Phzj/view?usp=share_link"

# fileurl = "https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbHdMvz%2FbtscHQrjdn7%2Fs9sHRPtvsfKKVtkTliikx1%2Fimg.png"

fileurl = "https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FdyPlb5%2FbtscPcNUgnr%2FCkjWKD53kndLyUXeolKYq0%2Fimg.png"
input_doc = mindee_client.doc_from_url(fileurl)

# Parse the document by passing the appropriate type
api_response = input_doc.parse(documents.TypeInvoiceV4)
# a = api_response.__dict__
# type(a)
import json
api_response_dict = api_response.__dict__['http_response']['document']['inference']
# json 파일로 저장
with open('api_response.json', 'w') as f :
	json.dump(api_response_dict, f, indent=4)

api_response_prediction_dict = api_response.__dict__['http_response']['document']['inference']['prediction']
# json 파일로 저장
with open('api_response_prediction.json', 'w') as f :
	json.dump(api_response_prediction_dict, f, indent=4)

with open('api_response_prediction.json', 'r') as json_read:
    json_str = json.load(json_read)  # json.load 로 파일 읽기
api_response_prediction = json.loads(json_str)


predictions_header = api_response.__dict__['http_response']['document']['inference']['prediction']
features_header = api_response.__dict__['http_response']['document']['inference']['product']['features'][:-2]

# predictions[features[0]][0]['value']


# isinstance(predictions_header[features_header[0]],list) and len(predictions_header[features_header[0]]) == 1

predictions_line_items = api_response.__dict__['http_response']['document']['inference']['prediction']['line_items']

df = pd.DataFrame(predictions_line_items)

for i in range(len(features_header)):
    predictions_header_dict = {}
    if isinstance(predictions_header[features_header[i]],list) and len(predictions_header[features_header[i]]) == 1:
        predictions_header_dict = predictions_header[features_header[i]][0]
        last_value = list(predictions_header_dict.keys())[-1]
        df[features_header[i]] = predictions_header_dict[last_value]
        # print(str(i), features_header[i], ": ", predictions_header_dict[last_value])
    elif isinstance(predictions_header[features_header[i]],list) and len(predictions_header[features_header[i]]) == 0:
        # print(str(i), features_header[i], ": ", "N/A")
        df[features_header[i]] = "N/A"
    elif isinstance(predictions_header[features_header[i]], dict):
        predictions_header_dict = predictions_header[features_header[i]]
        last_value = list(predictions_header_dict.keys())[-1]
        df[features_header[i]] = predictions_header_dict[last_value]
        # print(str(i), features_header[i], ": ", predictions_header_dict[last_value])


'''
for i in range(len(features_header)):
    predictions_header_dict = {}
    if isinstance(predictions_header[features_header[i]],list) and len(predictions_header[features_header[i]]) == 1:
        predictions_header_dict = predictions_header[features_header[i]][0]
        last_value = list(predictions_header_dict.keys())[-1]
        print(str(i), features_header[i], ": ", predictions_header_dict[last_value])
    elif isinstance(predictions_header[features_header[i]],list) and len(predictions_header[features_header[i]]) == 0:
        print(str(i), features_header[i], ": ", "N/A")
    elif isinstance(predictions_header[features_header[i]], dict):
        predictions_header_dict = predictions_header[features_header[i]]
        last_value = list(predictions_header_dict.keys())[-1]
        print(str(i), features_header[i], ": ", predictions_header_dict[last_value])

'''

# Print a brief summary of the parsed data
print(api_response.document)

type(api_response.document)

'''
chat GPT prompt

how about using following cod to extract data.
fileurl = "https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbHdMvz%2FbtscHQrjdn7%2Fs9sHRPtvsfKKVtkTliikx1%2Fimg.png"

input_doc = mindee_client.doc_from_url(fileurl)

# Parse the document by passing the appropriate type
api_response = input_doc.parse(documents.TypeInvoiceV4)

I want to store data to dataframe from "api_response.document"

'''


# Import pandas library
import pandas as pd

# Extract invoice data from the response
invoice_data = api_response.document.invoice.data

# Extract line item data from the response
line_item_data = api_response.document.invoice.line_items.data

# Create dataframe for invoice data
invoice_df = pd.DataFrame(invoice_data.items(), columns=['Field', 'Value'])

# Create dataframe for line item data
line_item_df = pd.DataFrame([x.items() for x in line_item_data], columns=['Field', 'Value']).explode('Value').reset_index(drop=True)

# Display the dataframes
print("Invoice Data:\n", invoice_df)
print("\nLine Item Data:\n", line_item_df)





import pdf2image
from pdf2image import convert_from_path

file_name = 'File'
file_path = 'C:/Users/namkee.lee/Documents/AI Builder Document Processing Sample Data/Invoices/Contoso/Train/Contoso 1.pdf'
pop_path = 'C:/Users/namkee.lee/PycharmProjects/OCR_API/poppler/Library/bin'

pages = convert_from_path(file_path, poppler_path=pop_path)

PDF_FILE_PATH = 'C:/Users/namkee.lee/Documents/AI Builder Document Processing Sample Data/Invoices/Contoso/Train/Contoso 1.pdf'
pages = convert_from_path(PDF_FILE_PATH)



#    onvert_from_path(PDF_FILE_PATH)
for i, page in enumerate(pages):
    page.save(f"./data/{str(i)}.jpg", "JPEG")
















