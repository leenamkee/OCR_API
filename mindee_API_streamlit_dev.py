import streamlit as st
from mindee import Client, documents
import pandas as pd
from PIL import Image
import base64
import io
import PyPDF2
import os
import time
import json

from PIL import Image

# Init a new client
api_key = st.secrets["mindee_invoice_api_key"]
mindee_client = Client(api_key=api_key)


st.set_page_config(layout="wide")
st.title("Invoice Data Extraction App")

# fileurl = st.text_input('Input URL of invoice image: ')
# st.write('sample: https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbHdMvz%2FbtscHQrjdn7%2Fs9sHRPtvsfKKVtkTliikx1%2Fimg.png')
# st.text('sample: https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbHdMvz%2FbtscHQrjdn7%2Fs9sHRPtvsfKKVtkTliikx1%2Fimg.png')
# st.write('Or')
# file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png", "pdf"])


# def upload_file(self, uploaded_file):
#     timestamp = str(time.time())
#     timestamp = timestamp.replace(".", "")
#
#     file_name, file_extension = os.path.splitext(uploaded_file.name)
#     uploaded_file.name = file_name + "_" + timestamp + file_extension
#
#     if os.path.exists(os.path.join("docs/inference/", uploaded_file.name)):
#         st.write("File already exists")
#         return False
#
#     if len(uploaded_file.name) > 500:
#         st.write("File name too long")
#         return False
#
#     with open(os.path.join("docs/inference/", uploaded_file.name), "wb") as f:
#         f.write(uploaded_file.getbuffer())
#
#     st.success("File uploaded successfully")
#
#     return os.path.join("docs/inference/", uploaded_file.name)

file = None
upload_button_text_desc = 'Choose a file'
upload_help = 'Upload an invoice image to extract data'
upload_button_text = 'Upload'


col1, col2 = st.columns(2)

with col1.form("upload-form", clear_on_submit=True):
    uploaded_file = st.file_uploader(upload_button_text_desc, accept_multiple_files=False,
                                     type=['png', 'jpg', 'jpeg'],
                                     help=upload_help)
    submitted = st.form_submit_button(upload_button_text)

    if submitted and uploaded_file is not None:
        file = uploaded_file
    #     ret = upload_file(uploaded_file)
    #
    #     if ret is not False:
    #         set_image_file(ret)
    #         set_data_result(None)


###########################

import fitz  # PyMuPDF library for working with PDF files

def render_pdf(pdf_doc, page):
    """
    Renders the specified page of the PDF document.
    """
    page = pdf_doc.load_page(page)
    pix = page.get_pixmap()
    img = pix.to_pil_image()
    return img

def pdf_to_base64(file):
    with open(file, "rb") as pdf_file:
        base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
    return base64_pdf

#############################
def display_image(file = None, st = st):
    try:  # Image file
        st.image(file)
        # img_bytes = file.read()
        # encoded_img = base64.b64encode(img_bytes).decode('utf-8')
    except:  # pdf file
        with open(file.read(), "rb") as f:
            base64_pdf = base64.b64encode(f)  # .decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="800" height="800" type="application/pdf"></iframe>'
        col1.markdown(pdf_display, unsafe_allow_html=True)

def extract_data(file):
    input_doc = mindee_client.doc_from_file(file)
    api_response = input_doc.parse(documents.TypeInvoiceV4)
    api_response_prediction = api_response.__dict__['http_response']['document']['inference']['prediction']
    return api_response_prediction

def get_header_values(predictions_header, position):
    features_header = list(predictions_header.keys())
    features_header.remove('line_items')
    df_header = pd.DataFrame()
    for i in range(len(features_header)):
        predictions_header_dict = {}
        if isinstance(predictions_header[features_header[i]], list) and len(
                predictions_header[features_header[i]]) >= 1:
            predictions_header_dict = predictions_header[features_header[i]][0]
            last_value = list(predictions_header_dict.keys())[position]
            # st.write(f'{features_header[i]}: {predictions_header_dict[last_value]}')
            df_header[features_header[i]] = [predictions_header_dict[last_value]]
        elif isinstance(predictions_header[features_header[i]], list) and len(
                predictions_header[features_header[i]]) == 0:
            # st.write(f'{features_header[i]}: N/A')
            df_header[features_header[i]] = [None]
        elif isinstance(predictions_header[features_header[i]], dict):
            predictions_header_dict = predictions_header[features_header[i]]
            last_value = list(predictions_header_dict.keys())[position]
            # st.write(f'{features_header[i]}: {predictions_header_dict[last_value]}')
            df_header[features_header[i]] = [predictions_header_dict[last_value]]
    df_header.dropna(inplace=True, axis=1)
    df_header = df_header.transpose()
    if position == -1:
        df_header.rename(columns={0: 'value'}, inplace=True)
    elif position == 0:
        df_header.rename(columns={0: 'confidence'}, inplace=True)
    return df_header



def make_df_header(api_response_prediction):
    predictions_header = api_response_prediction
    df_value = get_header_values(predictions_header, position=-1)
    df_confidence = get_header_values(predictions_header, position=0)
    df_header = pd.merge(df_value, df_confidence,left_index=True, right_index=True)

    return df_header

def make_df_item(api_response_prediction):
    # invoice item data
    predictions_line_items = api_response_prediction['line_items']
    # line item data frame
    df = pd.DataFrame(predictions_line_items)
    df = df.loc[:, ['confidence', 'description', 'quantity', 'unit_price', 'total_amount']]
    return df

def make_df_download(df):
    columns = ['Invoice_NO', 'Supplier_name', 'Customer_name', 'Date', 'Total_amount', 'Item_NO', 'Item_description',
               'Item_QTY', 'Unit_price', 'Item_total']
    df_download = df.copy()

    # df_download.columns

    df_download = df_download[['description', 'quantity', 'unit_price', 'total_amount']]

    df_download.reset_index(inplace=True)

    df_download.columns = ['Item_NO', 'Item_description', 'Item_QTY', 'Unit_price', 'Item_total']

    df_download['Invoice_NO'] = df_header.loc['invoice_number']['value']
    df_download['Supplier_name'] = df_header.loc['supplier_name']['value']
    df_download['Customer_name'] = df_header.loc['customer_name']['value']
    df_download['Date'] = df_header.loc['date']['value']
    df_download['Total_amount'] = df_header.loc['total_amount']['value']

    df_download = df_download[
        ['Invoice_NO', 'Supplier_name', 'Customer_name', 'Date', 'Total_amount', 'Item_NO', 'Item_description',
         'Item_QTY', 'Unit_price', 'Item_total']]
    return df_download


try:

    if file is not None:
        display_image(file=file, st=col1)
        extract_data_button = col2.button('extract data')
        if col2.button('extract data'):
            api_response_prediction = extract_data(file)
            df_header = make_df_header(api_response_prediction)
            col2.subheader('Invoice Header')
            col2.write(df_header)

            # invoice item data
            df = make_df_item(api_response_prediction)

            # Display the DataFrame
            col2.subheader('Invoice Items')
            col2.write(df)

            df_download = make_df_download(df)


            @st.cache_data
            def convert_df(df):
                return df.to_csv(index=False).encode('utf-8')


            csv = convert_df(df_download)

            display_image(file=file, st=col1)
            col2.download_button(
                "Press to Download",
                csv,
                f"file_{df_header.iloc[9][0]}_{df_header.iloc[2][0]}.csv",
                "text/csv",
                key='download-csv'
            )


            show_json = False  # boolean variable to track whether to show the JSON or not

            if col2.button("Show/Hide JSON"):
                show_json = not show_json  # invert the boolean value

            if show_json:
                # code to display the JSON
                col2.json(api_response_prediction)
            else:
                col2.write(':)')
    else:
        st.write('upload invoice or click "Sample invoice" ')
        # Load a file from disk or using URL
        if st.button('Sample invoice'):
            fileurl = "https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FdyPlb5%2FbtscPcNUgnr%2FCkjWKD53kndLyUXeolKYq0%2Fimg.png"
            col1.image(fileurl)
            # json file 읽기
            with open('api_response_prediction.json', 'r') as json_read:
                api_response_prediction = json.load(json_read)  # json.load 로 파일 읽기

            df_header = make_df_header(api_response_prediction)
            col2.subheader('Invoice Header')
            col2.write(df_header)

            # invoice item data
            df = make_df_item(api_response_prediction)
            # Display the DataFrame
            col2.subheader('Invoice Items')
            col2.write(df)


            # columns = ['Invoice_NO', 'Supplier_name', 'Customer_name', 'Date', 'Total_amount', 'Item_NO', 'Item_description',
            #            'Item_QTY', 'Unit_price', 'Item_total']
            # # df_download = pd.DataFrame(columns=columns)
            # df_download = df.copy()
            #
            # #df_download.columns
            #
            # df_download = df_download[['description', 'quantity', 'unit_price', 'total_amount']]
            #
            # df_download.reset_index(inplace=True)
            #
            # df_download.columns = ['Item_NO', 'Item_description', 'Item_QTY', 'Unit_price', 'Item_total']
            #
            # df_download['Invoice_NO'] = df_header.loc['invoice_number']['value']
            # df_download['Supplier_name'] = df_header.loc['supplier_name']['value']
            # df_download['Customer_name'] = df_header.loc['customer_name']['value']
            # df_download['Date'] = df_header.loc['date']['value']
            # df_download['Total_amount'] = df_header.loc['total_amount']['value']
            #
            # df_download = df_download[
            #     ['Invoice_NO', 'Supplier_name', 'Customer_name', 'Date', 'Total_amount', 'Item_NO', 'Item_description',
            #      'Item_QTY', 'Unit_price', 'Item_total']]
            #
            df_download = make_df_download(df)

            @st.cache_data
            def convert_df(df):
                return df.to_csv(index=False).encode('utf-8')


            csv = convert_df(df_download)

            # col1.image(fileurl)
            col2.download_button(
                "Press to Download",
                csv,
                f"file_{df_header.iloc[9][0]}_{df_header.iloc[2][0]}.csv",
                "text/csv",
                key='download-csv'
            )



except Exception as e:
    st.write(e)
    st.write("Error: Could not extract data from the provided URL or file. Please check and try again.")

# Add an input box for the user to enter a URL

#
# url = ''
# url = st.text_input("Enter image URL:")
#
# if not url:
#     url = 'https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FbHdMvz%2FbtscHQrjdn7%2Fs9sHRPtvsfKKVtkTliikx1%2Fimg.png'
#
# if url:
#     try:
#         # Load the image from the URL
#         input_doc = mindee_client.doc_from_url(url)
#
#         # Parse the document by passing the appropriate type
#         api_response = input_doc.parse(documents.TypeInvoiceV4)
#
#         # invoice header data
#         predictions_header = api_response.__dict__['http_response']['document']['inference']['prediction']
#         features_header = api_response.__dict__['http_response']['document']['inference']['product']['features'][:-2]
#
#         # invoice item data
#         predictions_line_items = api_response.__dict__['http_response']['document']['inference']['prediction']['line_items']
#
#         # data frame
#         df = pd.DataFrame(predictions_line_items)
#
#         for i in range(len(features_header)):
#             predictions_header_dict = {}
#             if isinstance(predictions_header[features_header[i]],list) and len(predictions_header[features_header[i]]) == 1:
#                 predictions_header_dict = predictions_header[features_header[i]][0]
#                 last_value = list(predictions_header_dict.keys())[-1]
#                 df[features_header[i]] = predictions_header_dict[last_value]
#             elif isinstance(predictions_header[features_header[i]],list) and len(predictions_header[features_header[i]]) == 0:
#                 df[features_header[i]] = "N/A"
#             elif isinstance(predictions_header[features_header[i]], dict):
#                 predictions_header_dict = predictions_header[features_header[i]]
#                 last_value = list(predictions_header_dict.keys())[-1]
#                 df[features_header[i]] = predictions_header_dict[last_value]
#
#         # Display the DataFrame
#         st.write(df)
#         st.image(url)
#     except:
#         st.write("Error: Could not extract data from the provided URL. Please check the URL and try again.")

@st.cache_data(ttl=600)
def load_data(sheets_url):
    csv_url = sheets_url.replace("/edit#gid=", "/export?format=csv&gid=")
    return pd.read_csv(csv_url)

df_test = load_data(st.secrets["public_gsheets_url"])

# Print results.
for row in df_test.itertuples():
    st.write(f"{row.name} has a :{row.pet}:")

