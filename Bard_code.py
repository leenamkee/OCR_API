'''
prompt

Write code to extract data from the invoice
"https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbHdMvz%2FbtscHQrjdn7%2Fs9sHRPtvsfKKVtkTliikx1%2Fimg.png"
and store it in a dataframe using Python's 'mindee' library.

'''

import mindee
import pandas as pd

# Load the invoice image
invoice_image = mindee.Image("https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbHdMvz%2FbtscHQrjdn7%2Fs9sHRPtvsfKKVtkTliikx1%2Fimg.png")

# Extract the text from the invoice image
text = invoice_image.extract_text()

# Create a dataframe to store the extracted text
df = pd.DataFrame(text.splitlines(), columns=["Text"])

# Clean the dataframe
df = df.dropna()
df = df.reset_index(drop=True)

# Print the dataframe
print(df)

'''
prompt
module 'mindee' has no attribute 'Image'

'''


import mindee
from mindee import Client, documents

# Load the invoice image
invoice_image = mindee.Image.from_url("https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbHdMvz%2FbtscHQrjdn7%2Fs9sHRPtvsfKKVtkTliikx1%2Fimg.png")

# 수정
mindee_client = Client(api_key="3cdc41fac36e7f877c7ca11b23e97708")
invoice_image = mindee_client.doc_from_url("https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbHdMvz%2FbtscHQrjdn7%2Fs9sHRPtvsfKKVtkTliikx1%2Fimg.png")

# Extract the text from the invoice image
text = invoice_image.extract_text()

# Create a dataframe to store the extracted text
df = pd.DataFrame(text.splitlines(), columns=["Text"])

# Clean the dataframe
df = df.dropna()
df = df.reset_index(drop=True)

# Print the dataframe
print(df)