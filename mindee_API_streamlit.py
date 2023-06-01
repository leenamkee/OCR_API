import streamlit as st
import pandas as pd
from mindee import Client, documents
import base64
import json

# Initialize Mindee client
api_key = st.secrets["mindee_invoice_api_key"]
mindee_client = Client(api_key=api_key)

st.set_page_config(layout="wide")


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
        st.markdown(pdf_display, unsafe_allow_html=True)

def extract_data(input_image, input_type='Upload Image'):
    if input_type == 'Upload Image':
        input_doc = mindee_client.doc_from_file(input_image)
        api_response = input_doc.parse(documents.TypeInvoiceV4)
    elif input_type == 'URL of Image':
        input_doc =mindee_client.doc_from_url(input_image)
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

def make_df_download(df, df_header):
    columns = ['Invoice_NO', 'Supplier_name', 'Customer_name', 'Date', 'Total_amount', 'Item_NO', 'Item_description',
               'Item_QTY', 'Unit_price', 'Item_total']
    df_download = df.copy()
    # df_download.columns
    df_download = df_download[['description', 'quantity', 'unit_price', 'total_amount']]
    df_download.reset_index(inplace=True)
    df_download.columns = ['Item_NO', 'Item_description', 'Item_QTY', 'Unit_price', 'Item_total']
    try:
        df_download['Invoice_NO'] = df_header.loc['invoice_number']['value']
    except:
        columns.remove('Invoice_NO')
    try:
        df_download['Supplier_name'] = df_header.loc['supplier_name']['value']
    except:
        columns.remove('Supplier_name')
    try:
        df_download['Customer_name'] = df_header.loc['customer_name']['value']
    except:
        columns.remove('Customer_name')
    try:
        df_download['Date'] = df_header.loc['date']['value']
    except:
        columns.remove('Date')
    try:
        df_download['Total_amount'] = df_header.loc['total_amount']['value']
    except:
        columns.remove('Total_amount')
    df_download = df_download[columns]
    return df_download


def start_processing(input_image, input_type):
    col1, col2 = st.columns(2)
    col1.title("Invoice Image")
    col2.title("Extracted Data")
    if input_image:
        col1.image(input_image, caption="Uploaded Image", use_column_width=True)

        # Extract data on button click
        if col2.button("Extract data"):
            # Convert uploaded file to bytes
            # file_bytes = uploaded_file.read()
            if input_type == 'Sample Image':
                with open('api_response_prediction.json', 'r') as json_read:
                    api_response_prediction = json.load(json_read)  # json.load 로 파일 읽기
            else:
                api_response_prediction = extract_data(input_image)
            df_header = make_df_header(api_response_prediction)
            col2.subheader('Invoice Header')
            col2.write(df_header)

            # invoice item data
            df = make_df_item(api_response_prediction)

            # Display the DataFrame
            col2.subheader('Invoice Items')
            col2.write(df)

            df_download = make_df_download(df, df_header)

            @st.cache_data
            def convert_df(df):
                return df.to_csv(index=False).encode('utf-8')

            csv = convert_df(df_download)

            col2.download_button(
                "Download csv",
                csv,
                f"file_{df_header.iloc[9][0]}_{df_header.iloc[2][0]}.csv",
                "text/csv",
                key='download-csv'
            )
            # col1.image(uploaded_file, caption="Uploaded Image", use_column_width=True)




# Create a Streamlit app
def main():
    # Set up the layout
    st.sidebar.title("Invoice Data Extraction")
    st.sidebar.markdown("Upload an image file or enter the URL of an image:")
    input_type = st.sidebar.radio("select one", ( "Sample Image", "Upload Image", "URL of Image"))
    # st.sidebar.markdown("Upload an image file:")
    upload_button_text_desc = 'Choose a file'
    upload_help = 'Upload an invoice image to extract data'
    url_help = 'input the URL of invoice image to extract data'
    # upload_button_text = 'Upload'

    if input_type == "Upload Image":
        uploaded_file = st.sidebar.file_uploader(upload_button_text_desc, accept_multiple_files=False,
                                                 type=['png', 'jpg', 'jpeg'],
                                                 help=upload_help)
        try:
            if uploaded_file:
                # Display the uploaded image
                start_processing(uploaded_file, input_type)
                # st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        except Exception as e:
            st.sidebar.write(e)
            st.sidebar.write("Error: Could not extract data from the provided file. Please check and try again.")


    elif input_type == "URL of Image":
        url = st.sidebar.text_input("Input the URL of Invoice Image", help=url_help)
        try:
            if url:
                # Display the image from URL
                start_processing(url, input_type)
                # st.image(url, caption="Image from URL", use_column_width=True)
        except Exception as e:
            st.sidebar.write(e)
            st.sidebar.write("Error: Could not extract data from the provided file. Please check and try again.")

    else:
        fileurl = "https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FdyPlb5%2FbtscPcNUgnr%2FCkjWKD53kndLyUXeolKYq0%2Fimg.png"
        try:
            if fileurl:
                # Display the image from URL
                start_processing(fileurl, input_type)
                # st.image(fileurl, caption="Sample Image", use_column_width=True)
        except Exception as e:
            st.sidebar.write(e)
            st.sidebar.write("Error: Could not extract data from the provided file. Please check and try again.")


if __name__ == "__main__":
    main()