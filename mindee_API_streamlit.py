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


try:
    if file is not None:
        display_image(file=file, st=col1)
        extract_data_button = col2.button('extract data')
        if col2.button('extract data'):
            # get reponse from mindee
            api_response_prediction = extract_data(file)

            # invoice header data
            df_header = make_df_header(api_response_prediction)
            col2.subheader('Invoice Header')
            col2.write(df_header)

            # invoice item data
            df = make_df_item(api_response_prediction)
            col2.subheader('Invoice Items')
            col2.write(df)
    else:
        st.write('upload invoice or click "Sample invoice" ')
        # Load a file from disk or using URL
        if st.button('Sample invoice'):
            fileurl = "https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FdyPlb5%2FbtscPcNUgnr%2FCkjWKD53kndLyUXeolKYq0%2Fimg.png"
            col1.image(fileurl)
            # read json file
            with open('api_response_prediction.json', 'r') as json_read:
                api_response_prediction = json.load(json_read)

            # invoice header data
            df_header = make_df_header(api_response_prediction)
            col2.subheader('Invoice Header')
            col2.write(df_header)

            # invoice item data
            df = make_df_item(api_response_prediction)
            col2.subheader('Invoice Items')
            col2.write(df)

except Exception as e:
    st.write(e)
    st.write("Error: Could not extract data from the provided URL or file. Please check and try again.")


