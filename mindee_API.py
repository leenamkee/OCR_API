from mindee import Client, documents
import pandas as pd
import streamlit as st

# Init a new client

api_key = st.secrets["mindee_invoice_api_key"]
mindee_client = Client(api_key=api_key)

# Load a file from disk or using URL
fileurl = "https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbHdMvz%2FbtscHQrjdn7%2Fs9sHRPtvsfKKVtkTliikx1%2Fimg.png"
input_doc = mindee_client.doc_from_url(fileurl)

# Parse the document by passing the appropriate type
api_response = input_doc.parse(documents.TypeInvoiceV4)

# invoice header data
predictions_header = api_response.__dict__['http_response']['document']['inference']['prediction']
features_header = api_response.__dict__['http_response']['document']['inference']['product']['features'][:-2]

# invoice item data
predictions_line_items = api_response.__dict__['http_response']['document']['inference']['prediction']['line_items']


# data frame
df = pd.DataFrame(predictions_line_items)
df = df.loc[:, ['confidence', 'description', 'quantity', 'unit_price', 'tax_amount', 'tax_rate', 'total_amount']]
# df.keys()

for i in range(len(features_header)):
    predictions_header_dict = {}
    if isinstance(predictions_header[features_header[i]],list) and len(predictions_header[features_header[i]]) == 1:
        predictions_header_dict = predictions_header[features_header[i]][0]
        last_value = list(predictions_header_dict.keys())[-1]
        df[features_header[i]] = predictions_header_dict[last_value]
    elif isinstance(predictions_header[features_header[i]],list) and len(predictions_header[features_header[i]]) == 0:
        df[features_header[i]] = "N/A"
    elif isinstance(predictions_header[features_header[i]], dict):
        predictions_header_dict = predictions_header[features_header[i]]
        last_value = list(predictions_header_dict.keys())[-1]
        df[features_header[i]] = predictions_header_dict[last_value]

df_header = pd.DataFrame()

for i in range(len(features_header)):
    predictions_header_dict = {}
    if isinstance(predictions_header[features_header[i]],list) and len(predictions_header[features_header[i]]) == 1:
        predictions_header_dict = predictions_header[features_header[i]][0]
        last_value = list(predictions_header_dict.keys())[-1]
        # st.write(f'{features_header[i]}: {predictions_header_dict[last_value]}')
        df_header[features_header[i]] = [predictions_header_dict[last_value]]
    elif isinstance(predictions_header[features_header[i]],list) and len(predictions_header[features_header[i]]) == 0:
        # st.write(f'{features_header[i]}: N/A')
        df_header[features_header[i]] = [None]
    elif isinstance(predictions_header[features_header[i]], dict):
        predictions_header_dict = predictions_header[features_header[i]]
        last_value = list(predictions_header_dict.keys())[-1]
        # st.write(f'{features_header[i]}: {predictions_header_dict[last_value]}')
        df_header[features_header[i]] = [predictions_header_dict[last_value]]
df_header.dropna(inplace=True, axis=1)
df_header = df_header.transpose()
df_header.rename(columns={0: 'value'}, inplace=True)